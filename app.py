from flask import Flask, request, jsonify
import sys
import io
import threading
import pandas as pd
import numpy as np
import time

app = Flask(__name__)

# Allowed builtins ONLY
SAFE_BUILTINS = {
    "print": print,
    "len": len,
    "range": range,
    "min": min,
    "max": max,
    "sum": sum,
    "abs": abs,
}

# Allowed globals
SANDBOX_GLOBALS = {
    "__builtins__": SAFE_BUILTINS,
    "pd": pd,
    "np": np,
    "time": time,
}

def run_code(code, output):
    sys.stdout = output
    exec(code, SANDBOX_GLOBALS, {})

@app.route("/execute", methods=["POST"])
def execute():
    code = request.json.get("code", "")

    output = io.StringIO()
    thread = threading.Thread(target=run_code, args=(code, output))

    start = time.time()
    thread.start()
    thread.join(timeout=2)  # ⛔ hard time limit

    sys.stdout = sys.__stdout__

    if thread.is_alive():
        return jsonify({
            "stdout": output.getvalue(),
            "stderr": "Execution timed out"
        })

    return jsonify({
        "stdout": output.getvalue(),
        "stderr": ""
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
