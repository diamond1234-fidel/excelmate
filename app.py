from flask import Flask, request, jsonify
import io
import threading
import time
import contextlib
import pandas as pd
import numpy as np

app = Flask(__name__)

# ---- controlled import ----
def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    ALLOWED = {"pandas", "numpy", "time"}
    if name in ALLOWED:
        return __import__(name, globals, locals, fromlist, level)
    raise ImportError(f"Import blocked: {name}")

# ---- safe builtins ----
SAFE_BUILTINS = {
    "print": print,
    "len": len,
    "range": range,
    "min": min,
    "max": max,
    "sum": sum,
    "abs": abs,
    "__import__": safe_import,
}

SANDBOX_GLOBALS = {
    "__builtins__": SAFE_BUILTINS,
    "pd": pd,
    "np": np,
    "time": time,
}

# ---- execution runner ----
def run_code(code, stdout_buffer, stderr_buffer):
    try:
        with contextlib.redirect_stdout(stdout_buffer):
            exec(code, SANDBOX_GLOBALS, {})
    except Exception as e:
        stderr_buffer.write(str(e))

@app.route("/execute", methods=["POST"])
def execute():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")

    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()

    thread = threading.Thread(
        target=run_code,
        args=(code, stdout_buffer, stderr_buffer)
    )

    start = time.time()
    thread.start()
    thread.join(timeout=2)

    if thread.is_alive():
        return jsonify({
            "stdout": stdout_buffer.getvalue(),
            "stderr": "Execution timed out"
        })

    return jsonify({
        "stdout": stdout_buffer.getvalue(),
        "stderr": stderr_buffer.getvalue()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
