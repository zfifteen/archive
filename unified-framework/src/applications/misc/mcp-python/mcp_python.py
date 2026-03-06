from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/initialize', methods=['POST'])
def initialize():
    return jsonify({
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "bash-server",
            "version": "1.0.0"
        }
    })

@app.route('/tools/list', methods=['GET'])
def tools_list():
    return jsonify({
        "tools": [
            {
                "name": "bash",
                "description": "Execute bash command",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Bash command to execute"}
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "python",
                "description": "Execute Python code",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Python code to execute"}
                    },
                    "required": ["code"]
                }
            },
            {
                "name": "gh",
                "description": "Execute GitHub CLI command",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "args": {"type": "string", "description": "GitHub CLI arguments"}
                    },
                    "required": ["args"]
                }
            },
            {
                "name": "read_file",
                "description": "Read file contents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "write_file",
                "description": "Write file contents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"},
                        "content": {"type": "string", "description": "File content"}
                    },
                    "required": ["path", "content"]
                }
            },
            {
                "name": "list_dir",
                "description": "List directory contents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path"}
                    },
                    "required": ["path"]
                }
            }
        ]
    })

@app.route('/tools/call', methods=['POST'])
def tools_call():
    data = request.json
    tool_name = data.get("name")
    args = data.get("arguments", {})

    try:
        if tool_name == "bash":
            result = subprocess.run(args["command"], shell=True, capture_output=True, text=True)
            output = result.stdout + result.stderr
            return jsonify({
                "content": [{"type": "text", "text": output if output else "(no output)"}],
                "isError": result.returncode != 0
            })

        elif tool_name == "python":
            result = subprocess.run(["python3", "-c", args["code"]], capture_output=True, text=True)
            output = result.stdout + result.stderr
            return jsonify({
                "content": [{"type": "text", "text": output if output else "(no output)"}],
                "isError": result.returncode != 0
            })

        elif tool_name == "gh":
            result = subprocess.run(f"gh {args['args']}", shell=True, capture_output=True, text=True)
            output = result.stdout + result.stderr
            return jsonify({
                "content": [{"type": "text", "text": output if output else "(no output)"}],
                "isError": result.returncode != 0
            })

        elif tool_name == "read_file":
            with open(args["path"], "r") as f:
                content = f.read()
            return jsonify({
                "content": [{"type": "text", "text": content}]
            })

        elif tool_name == "write_file":
            with open(args["path"], "w") as f:
                f.write(args["content"])
            return jsonify({
                "content": [{"type": "text", "text": f"Wrote {len(args['content'])} bytes to {args['path']}"}]
            })

        elif tool_name == "list_dir":
            entries = os.listdir(args["path"])
            output = "\n".join(entries)
            return jsonify({
                "content": [{"type": "text", "text": output}]
            })

    except Exception as e:
        return jsonify({
            "content": [{"type": "text", "text": str(e)}],
            "isError": True
        })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
