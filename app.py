from flask import Flask, request, jsonify
import io, threading, time, contextlib, traceback, base64
import pandas as pd
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
    "df": None
}

# ---- execution runner ----
def run_code(code, result_dict):
    try:
        exec(code, SANDBOX_GLOBALS, result_dict)
    except Exception:
        result_dict["error"] = traceback.format_exc()

# ---- execution endpoint ----
@app.route("/execute", methods=["POST"])
def execute():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    csv_base64 = data.get("csv", "")

    if not code.strip():
        return jsonify({"error": "No code provided"}), 400

    if csv_base64:
        try:
            csv_bytes = base64.b64decode(csv_base64)
            SANDBOX_GLOBALS["df"] = pd.read_csv(io.StringIO(csv_bytes.decode()))
        except Exception as e:
            return jsonify({"error": f"CSV decode error: {e}"}), 400

    result_dict = {}
    thread = threading.Thread(target=run_code, args=(code, result_dict), daemon=True)

    start_time = time.time()
    thread.start()
    thread.join(timeout=10)  # longer for 1200 rows

    if thread.is_alive():
        return jsonify({"error": "Execution timed out"}), 408

    result_dict["execution_time"] = round(time.time() - start_time, 4)
    return jsonify(result_dict)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
