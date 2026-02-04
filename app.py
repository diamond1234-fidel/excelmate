from flask import Flask, request, jsonify
import sys
import io

app = Flask(__name__)

@app.route("/execute", methods=["POST"])
def execute():
    print('started')
    code = request.json.get("code", "")
    print('recieved')
    try:
        
        print('trying')
        # Redirect stdout
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()

        # Execute user code
        exec(code, {})

        sys.stdout = old_stdout
        output = mystdout.getvalue()
        
        print('done, sending back')
        return jsonify({"stdout": output, "stderr": ""})
    except Exception as e:
        
        print('error')
        return jsonify({"stdout": "", "stderr": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
