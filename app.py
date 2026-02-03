from flask import Flask, request, jsonify
import sys
import io

app = Flask(__name__)

@app.route("/execute", methods=["POST"])
def execute():
    code = request.json.get("code", "")
    try:
        # Redirect stdout
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()

        # Execute user code
        exec(code, {})

        sys.stdout = old_stdout
        output = mystdout.getvalue()
        return jsonify({"stdout": output, "stderr": ""})
    except Exception as e:
        return jsonify({"stdout": "", "stderr": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
