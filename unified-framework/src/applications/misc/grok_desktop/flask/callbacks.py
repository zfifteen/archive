import json
import subprocess
from typing import Dict, List, Any, Optional


class ToolCallbacks:
    """Handles all tool execution callbacks for the Grok chat application"""

    @staticmethod
    def get_tools_schema() -> List[Dict]:
        """Returns the OpenAI-compatible tools schema"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "bash",
                    "description": "Execute bash command on the server",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Bash command to execute"
                            }
                        },
                        "required": ["command"]
                    }
                }
            }
        ]

    @staticmethod
    def execute_bash_command(command: str) -> Dict[str, Any]:
        """Execute a bash command safely and return the result"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60 * 5  # 5 minute timeout
            )
            output = result.stdout + result.stderr
            return {
                "success": result.returncode == 0,
                "output": output if output else "(no output)",
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "Command timed out after 5 minutes",
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "output": f"Error executing command: {str(e)}",
                "return_code": -1
            }

    @staticmethod
    def format_tool_output(command: str, result: Dict[str, Any]) -> str:
        """Format tool execution output for frontend display"""
        return (
            f"--- Bash Command Execution ---\n"
            f"$ {command}\n\n"
            f"Exit Code: {result['return_code']}\n"
            f"--- Output ---\n{result['output']}"
        )

    @staticmethod
    def handle_tool_calls(tool_calls: List[Dict], api_messages: List[Dict]) -> Dict[str, Any]:
        """Process all tool calls and return formatted results"""
        tool_outputs = []

        # Add the assistant's request to use a tool to the conversation history
        assistant_message = {
            'role': 'assistant',
            'tool_calls': tool_calls
        }
        api_messages.append(assistant_message)

        for tool_call in tool_calls:
            if tool_call.get('function', {}).get('name') == 'bash':
                try:
                    args = json.loads(tool_call['function']['arguments'])
                    command = args.get('command')

                    if command:
                        result = ToolCallbacks.execute_bash_command(command)

                        # Add the tool's result to the conversation for the next API call
                        api_messages.append({
                            'role': 'tool',
                            'tool_call_id': tool_call['id'],
                            'content': result['output']
                        })

                        # Format the output for immediate display on the frontend
                        formatted_output = ToolCallbacks.format_tool_output(command, result)
                        tool_outputs.append(formatted_output)

                except Exception as e:
                    tool_outputs.append(f"--- Error executing bash command: {str(e)} ---")

        return {
            "tool_outputs": tool_outputs,
            "updated_messages": api_messages
        }