from flask import Flask, request, jsonify
import io, time, contextlib, traceback, base64
import pandas as pd
import numpy as np
import multiprocessing as mp
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# ---- safe imports ----
ALLOWED_IMPORTS = {"pandas", "numpy", "time", "json"}

def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    root = name.split(".")[0]
    if root in ALLOWED_IMPORTS:
        return __import__(name, globals, locals, fromlist, level)
    raise ImportError(f"Import blocked: {name}")

# ---- safe builtins ----
SAFE_BUILTINS = {
    "print": print, "len": len, "range": range,
    "min": min, "max": max, "sum": sum,
    "abs": abs, "round": round,
    "enumerate": enumerate, "zip": zip, "sorted": sorted,
    "int": int, "float": float, "str": str, "bool": bool,
    "__import__": safe_import,
}

# ---- isolated execution runner ----
def run_code(code, csv_bytes, result):
    stdout = io.StringIO()
    stderr = io.StringIO()

    sandbox_globals = {
        "__builtins__": SAFE_BUILTINS,
        "pd": pd,
        "np": np,
        "time": time,
        "json": json,
        "df": None
    }

    try:
        if csv_bytes:
            sandbox_globals["df"] = pd.read_csv(
                io.StringIO(csv_bytes.decode())
            )

        with contextlib.redirect_stdout(stdout), \
             contextlib.redirect_stderr(stderr):
            exec(code, sandbox_globals, {})
    except Exception:
        stderr.write(traceback.format_exc())

    result["stdout"] = stdout.getvalue()
    result["stderr"] = stderr.getvalue()

# ---- execution endpoint ----
@app.route("/execute", methods=["POST"])
def execute():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    csv_base64 = data.get("csv", "")

    if not code.strip():
        return jsonify({"stdout": "", "stderr": "No code provided"}), 400

    timeout = min(int(data.get("timeout", 10)), 20)

    csv_bytes = None
    if csv_base64:
        try:
            csv_bytes = base64.b64decode(csv_base64)
        except Exception as e:
            return jsonify({"stdout": "", "stderr": f"CSV decode error: {e}"}), 400

    manager = mp.Manager()
    result = manager.dict()

    proc = mp.Process(
        target=run_code,
        args=(code, csv_bytes, result)
    )

    start_time = time.time()
    proc.start()
    proc.join(timeout)

    if proc.is_alive():
        proc.terminate()
        proc.join()
        return jsonify({
            "stdout": result.get("stdout", ""),
            "stderr": "Execution timed out"
        }), 408

    return jsonify({
        "stdout": result.get("stdout", ""),
        "stderr": result.get("stderr", ""),
        "execution_time": round(time.time() - start_time, 4)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
