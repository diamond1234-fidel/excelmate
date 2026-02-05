import os, io, base64, pandas as pd, numpy as np, json, time, traceback

# Read code and CSV from environment
code = os.environ.get("CODE", "")
csv_base64 = os.environ.get("CSV", "")
runs = int(os.environ.get("RUNS", "1"))

stdout_list = []
stderr_list = []
times = []

# Load CSV in memory if provided
df = None
if csv_base64:
    try:
        csv_bytes = base64.b64decode(csv_base64)
        df = pd.read_csv(io.StringIO(csv_bytes.decode()))
    except Exception as e:
        stderr_list.append("CSV Load Error: " + str(e))

# Sandbox builtins
SAFE_BUILTINS = {
    "print": print, "len": len, "range": range, "min": min, "max": max,
    "sum": sum, "abs": abs, "round": round, "enumerate": enumerate,
    "zip": zip, "sorted": sorted, "int": int, "float": float,
    "str": str, "bool": bool,
}

globals_dict = {"__builtins__": SAFE_BUILTINS, "pd": pd, "np": np, "time": time, "df": df}

for _ in range(runs):
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    start = time.time()
    try:
        exec(code, globals_dict)
    except Exception:
        stderr_buffer.write(traceback.format_exc())
    times.append(time.time() - start)
    stdout_list.append(stdout_buffer.getvalue())
    stderr_list.append(stderr_buffer.getvalue())

print(json.dumps({
    "stdout": stdout_list,
    "stderr": stderr_list,
    "avg_time": round(sum(times)/len(times), 4)
}))
