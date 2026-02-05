from flask import Flask, request, jsonify
import io
import threading
import time
import contextlib
import pandas as pd
import numpy as np

app = Flask(__name__)

SAFE_BUILTINS = {
    "print": print,
    "len": len,
    "range": range,
    "min": min,
    "max": max,
    "sum": sum,
    "abs": abs,
}

SANDBOX_GLOBALS = {
    "__builtins__": SAFE_BUILTINS,
    "pd": pd,
    "np": np,
    "time": time,
}

def run_code(code, output):
    with contextlib.redirect_stdout(output):
        exec(code, SANDBOX_GLOBALS, {})

@app.route("/execute", methods=["POST"])
def execute():
    code = request.json.get("code", "")

    output = io.StringIO()
    thread = threading.Thread(target=run_code, args=(code, output))

    thread.start()
    thread.join(timeout=2)

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
