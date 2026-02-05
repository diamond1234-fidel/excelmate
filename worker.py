from flask import Flask, request, jsonify
import io, threading, time, contextlib, traceback
import pandas as pd
import numpy as np
import base64

app = Flask(__name__)

def run_sandbox(code, df, stdout_buf, stderr_buf):
    SAFE_BUILTINS = {
        "print": print, "len": len, "range": range,
        "min": min, "max": max, "sum": sum, "abs": abs, "round": round,
        "enumerate": enumerate, "zip": zip, "sorted": sorted,
        "int": int, "float": float, "str": str, "bool": bool,
    }
    globals_dict = {"__builtins__": SAFE_BUILTINS, "pd": pd, "np": np, "time": time, "df": df}
    try:
        exec(code, globals_dict)
    except Exception:
        stderr_buf.write(traceback.format_exc())

@app.route("/execute", methods=["POST"])
def execute():
    data = request.get_json() or {}
    code = data.get("code", "")
    csv_base64 = data.get("csv", "")
    runs = min(int(data.get("runs", 1)), 3)  # max 3 runs for safety

    df = None
    if csv_base64:
        try:
            csv_bytes = base64.b64decode(csv_base64)
            df = pd.read_csv(io.StringIO(csv_bytes.decode()))
        except Exception as e:
            return jsonify({"stdout": "", "stderr": "CSV Error: "+str(e)}), 400

    stdout_list = []
    stderr_list = []
    times = []

    for _ in range(runs):
        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()
        start = time.time()
        thread = threading.Thread(target=run_sandbox, args=(code, df, stdout_buf, stderr_buf))
        thread.start()
        thread.join(timeout=2)  # ⏱ 2-second hard limit
        if thread.is_alive():
            stderr_buf.write("Execution timed out\n")
        times.append(time.time()-start)
        stdout_list.append(stdout_buf.getvalue())
        stderr_list.append(stderr_buf.getvalue())

    return jsonify({
        "stdout": stdout_list,
        "stderr": stderr_list,
        "avg_time": round(sum(times)/len(times), 4)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
