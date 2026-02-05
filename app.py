from flask import Flask, request, jsonify
import io
import threading
import time
import contextlib
import traceback
import pandas as pd
import numpy as np

app = Flask(__name__)

# ============================================================
# 1. CONTROLLED IMPORT SYSTEM
# ============================================================
# Only allow specific libraries needed for analytics
ALLOWED_IMPORTS = {
    "pandas",
    "numpy",
    "time",
}

def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    root = name.split(".")[0]
    if root in ALLOWED_IMPORTS:
        return __import__(name, globals, locals, fromlist, level)
    raise ImportError(f"Import blocked: {name}")

# ============================================================
# 2. SAFE BUILTINS (WHITELIST, NOT BLACKLIST)
# ============================================================
# These are common, non-dangerous Python utilities
SAFE_BUILTINS = {
    # basic utilities
    "print": print,
    "len": len,
    "range": range,
    "min": min,
    "max": max,
    "sum": sum,
    "abs": abs,
    "round": round,

    # iteration helpers
    "enumerate": enumerate,
    "zip": zip,
    "sorted": sorted,

    # type constructors
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,

    # controlled import hook
    "__import__": safe_import,
}

# ============================================================
# 3. SANDBOX GLOBALS
# ============================================================
# What user code can "see"
SANDBOX_GLOBALS = {
    "__builtins__": SAFE_BUILTINS,

    # preloaded libraries (faster, predictable)
    "pd": pd,
    "np": np,
    "time": time,
}

# ============================================================
# 4. CODE EXECUTION RUNNER
# ============================================================
def run_code(code, stdout_buffer, stderr_buffer):
    try:
        with contextlib.redirect_stdout(stdout_buffer), \
             contextlib.redirect_stderr(stderr_buffer):
            exec(code, SANDBOX_GLOBALS, {})
    except Exception:
        # full traceback is MUCH better than str(e)
        stderr_buffer.write(traceback.format_exc())

# ============================================================
# 5. EXECUTION ENDPOINT
# ============================================================
@app.route("/execute", methods=["POST"])
def execute():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")

    if not code.strip():
        return jsonify({
            "stdout": "",
            "stderr": "No code provided"
        }), 400

    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()

    thread = threading.Thread(
        target=run_code,
        args=(code, stdout_buffer, stderr_buffer),
        daemon=True
    )

    start_time = time.time()
    thread.start()
    thread.join(timeout=2)  # ⛔ hard execution limit

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

# ============================================================
# 6. SERVER ENTRY POINT
# ============================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
