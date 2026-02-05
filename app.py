from flask import Flask, request, jsonify
import io, threading, time, contextlib, traceback, base64
import pandas as pd
import numpy as np

app = Flask(__name__)

# ---- safe imports ----
ALLOWED_IMPORTS = {"pandas", "numpy", "time"}
def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    root = name.split(".")[0]
    if root in ALLOWED_IMPORTS:
        return __import__(name, globals, locals, fromlist, level)
    raise ImportError(f"Import blocked: {name}")

# ---- safe builtins ----
SAFE_BUILTINS = {
    "print": print, "len": len, "range": range, "min": min, "max": max,
    "sum": sum, "abs": abs, "round": round, "enumerate": enumerate,
    "zip": zip, "sorted": sorted,
    "int": int, "float": float, "str": str, "bool": bool,
    "__import__": safe_import,
}

# ---- sandbox globals ----
SANDBOX_GLOBALS = {
    "__builtins__": SAFE_BUILTINS,
    "pd": pd,
    "np": np,
    "time": time,
    "df": None  # placeholder for CSV
}

# ---- execution runner ----
def run_code(code, stdout_buffer, stderr_buffer):
    try:
        with contextlib.redirect_stdout(stdout_buffer), \
             contextlib.redirect_stderr(stderr_buffer):
            exec(code, SANDBOX_GLOBALS, {})
    except Exception:
        stderr_buffer.write(traceback.format_exc())

# ---- execution endpoint ----
@app.route("/execute", methods=["POST"])
def execute():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    csv_base64 = data.get("csv", "")  # optional base64 CSV string

    if not code.strip():
        return jsonify({"stdout": "", "stderr": "No code provided"}), 400

    # Decode CSV if provided
    if csv_base64:
        try:
            csv_bytes = base64.b64decode(csv_base64)
            SANDBOX_GLOBALS["df"] = pd.read_csv(io.StringIO(csv_bytes.decode()))
        except Exception as e:
            return jsonify({"stdout": "", "stderr": f"CSV decode error: {e}"}), 400

    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()

    thread = threading.Thread(
        target=run_code,
        args=(code, stdout_buffer, stderr_buffer),
        daemon=True
    )

    start_time = time.time()
    thread.start()
    thread.join(timeout=2)  # hard execution limit

    if thread.is_alive():
        return jsonify({
            "stdout": stdout_buffer.getvalue(),
            "stderr": "Execution timed out"
        }), 408

    return jsonify({
        "stdout": stdout_buffer.getvalue(),
        "stderr": stderr_buffer.getvalue(),
        "execution_time": round(time.time() - start_time, 4)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
