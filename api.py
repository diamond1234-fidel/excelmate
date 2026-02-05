from flask import Flask, request, jsonify
import base64, subprocess, uuid

app = Flask(__name__)

@app.route("/execute", methods=["POST"])
def execute():
    data = request.get_json() or {}
    code = data.get("code", "")
    csv_str = data.get("csv", "")  # base64 string
    runs = data.get("runs", 1)

    if not code.strip():
        return jsonify({"stdout": "", "stderr": "No code provided"}), 400

    # Spawn a Docker container for this request
    container_name = f"sandbox-{uuid.uuid4().hex[:8]}"
    cmd = [
        "docker", "run", "--rm",
        "-e", f"CODE={code}",
        "-e", f"CSV={csv_str}",
        "-e", f"RUNS={runs}",
        "my-worker-image"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        output = result.stdout.strip()
        return jsonify(json.loads(output))
    except subprocess.TimeoutExpired:
        return jsonify({"stdout": "", "stderr": "Execution timed out"}), 408
    except Exception as e:
        return jsonify({"stdout": "", "stderr": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
