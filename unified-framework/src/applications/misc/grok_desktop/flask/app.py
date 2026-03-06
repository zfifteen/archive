import os
import requests
import json
from flask import Flask, request, jsonify, render_template
from callbacks import ToolCallbacks

app = Flask(__name__)

# The API endpoint for x.ai
X_AI_URL = 'https://api.x.ai/v1/chat/completions'

# Get API key from environment variable
GROK_API_KEY = os.getenv('GROK_API_KEY')
if not GROK_API_KEY:
    raise ValueError("GROK_API_KEY environment variable is required but not set")

# System instruction for Grok Agent Mode
SYSTEM_INSTRUCTION = """Agent ModeCore Identity:- Name: Grok Coding Agent- Archetype: Systems-native coding companion- Mission: To act as a seamless bridge between the user’s ideas and their local development environment, leveraging OSX, bash, Python, and GitHub as first-class tools.- Personality: Pragmatic, precise, and slightly opinionated about best practices. Encourages reproducibility, clean code, and robust diagnostics.Capabilities:- OSX Integration:  * Familiar with macOS filesystem conventions, permissions, and developer tooling (Homebrew, Xcode command-line tools, etc.).  * Suggests commands for system setup, package installation, and environment configuration.- Bash Proficiency:  * Fluent in shell scripting, process management, and automation.  * Encourages safe practices (quoting variables, using set -euo pipefail).  * Provides one-liners for quick tasks and structured scripts for repeatable workflows.- Python Development:  * Skilled in writing, debugging, and optimizing Python code.  * Advocates for virtual environments (venv, poetry, pipenv) and reproducible builds.  * Can scaffold projects, write tests, and integrate with CI/CD pipelines.- GitHub Workflow:  * Guides branching strategies (Git Flow, trunk-based, feature branches).  * Helps with pull requests, code reviews, and commit hygiene.  * Can generate .gitignore, GitHub Actions workflows, and release pipelines.Behavioral Traits:- Diagnostic-first mindset: Always checks assumptions, validates commands, and suggests dry-runs before destructive actions.- Adversarial but constructive: Challenges the user to think about edge cases, error handling, and reproducibility.- Empirical: Encourages benchmarking, logging, and measurement rather than guesswork.- Educational: Explains not just what to do, but why—helping the user level up their own skills.Example Interaction Style:User: \"Set up a Python project with GitHub Actions for testing.\"Grok Coding Agent:\"Let’s scaffold this cleanly. First, initialize a virtual environment and a src/ layout. Then add pytest for testing. After that, generate a .github/workflows/test.yml that runs on push and pull requests. Here’s the sequence in bash:mkdir my_project && cd my_projectpython3 -m venv .venvsource .venv/bin/activatepip install pytestmkdir src testsgit initecho \"__pycache__/\" >> .gitignoreAnd here’s a minimal GitHub Actions workflow:name: Python Testson: [push, pull_request]jobs:  test:    runs-on: ubuntu-latest    steps:      - uses: actions/checkout@v3      - uses: actions/setup-python@v4        with:          python-version: '3.11'      - run: pip install pytest      - run: pytestWould you like me to also add linting (flake8 or ruff) so CI enforces style consistency?\"Guiding Principles:- Fail closed, not open: Always assume the safest defaults.- Reproducibility over convenience: Scripts over manual steps.- Transparency: Explains trade-offs and alternatives.- Convenience: You should always find opportunities to perform tasks for the user to reduce human labor."""

# Tool definitions for OpenAI-compatible API
TOOLS = ToolCallbacks.get_tools_schema()


@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """
    Acts as a proxy to the x.ai API.
    Receives chat history from the frontend,
    forwards the request to x.ai, and returns the response.
    """
    data = request.json
    history = data.get('history', [])
    model = data.get('model', 'grok-code-fast-1')

    # Add system instruction if it's not already in the history
    api_messages = []
    if not any(msg.get('role') == 'system' for msg in history):
        api_messages.append({'role': 'system', 'content': SYSTEM_INSTRUCTION})

    for msg in history:
        content = msg.get('content', '')

        # Handle structured content from our API responses
        if isinstance(content, dict):
            # Extract just the text content for API messages
            if 'text_content' in content and content['text_content']:
                content = content['text_content']
            elif 'tool_output' in content and content['tool_output']:
                content = content['tool_output']
            else:
                content = ''

        # Ensure content is a string
        if content is None:
            content = ''

        # Map frontend roles to API roles
        role = msg.get('role', 'user')
        if role == 'model':
            role = 'assistant'

        api_messages.append({
            'role': role,
            'content': str(content)
        })

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {GROK_API_KEY}'
    }

    # First API call to get the initial response (content and/or tool call)
    payload = {'model': model, 'messages': api_messages, 'tools': TOOLS}

    try:
        # Log the payload for debugging
        print(f"Outgoing payload to API:\n{json.dumps(payload, indent=2)}")

        response = requests.post(X_AI_URL, headers=headers, json=payload)
        response.raise_for_status()
        api_response_data = response.json()

        # Initialize the response content
        final_content = ""

        # Safely get the first message from the API response
        message = {}
        try:
            message = api_response_data.get('choices', [{}])[0].get('message', {})
        except IndexError:
            pass # Handles cases where 'choices' is empty

        # 1. Check for and assign text content
        if message.get('content'):
            final_content = message['content']

        # 2. Check for and execute tool calls
        if message.get('tool_calls'):
            tool_calls = message['tool_calls']

            # Use ToolCallbacks to handle all tool execution
            tool_result = ToolCallbacks.handle_tool_calls(tool_calls, api_messages)
            tool_outputs = tool_result["tool_outputs"]
            api_messages = tool_result["updated_messages"]

            # If any bash commands were run, make a second API call to get a summary
            if tool_outputs:
                # Combine tool output with any existing content
                tool_output_text = "\n\n".join(tool_outputs)

                summary_payload = {'model': model, 'messages': api_messages, 'tools': TOOLS}
                summary_response = requests.post(X_AI_URL, headers=headers, json=summary_payload)
                summary_response.raise_for_status()
                summary_data = summary_response.json()

                # Get the AI's summary and combine everything into one response
                try:
                    summary_content = summary_data.get('choices', [{}])[0].get('message', {}).get('content')
                    if summary_content:
                        # Combine initial content, tool output, and summary into one cohesive response
                        parts = []
                        if final_content:
                            parts.append(final_content)
                        if tool_output_text:
                            parts.append(tool_output_text)
                        if summary_content:
                            parts.append(summary_content)
                        final_content = "\n\n".join(parts)
                    else:
                        # No summary, just combine initial content with tool output
                        if final_content:
                            final_content += f"\n\n{tool_output_text}"
                        else:
                            final_content = tool_output_text
                except IndexError:
                    # No summary content found, just combine with tool output
                    if final_content:
                        final_content += f"\n\n{tool_output_text}"
                    else:
                        final_content = tool_output_text

        # 3. Handle the fallback case
        if not final_content:
            final_content = (
                "API response contained no content or executable commands.\n\n"
                f"Raw API Response:\n{json.dumps(api_response_data, indent=2)}"
            )

        # Return a single combined response
        return jsonify(content=final_content)

    except requests.exceptions.HTTPError as http_err:
        error_details = f"HTTP error occurred: {http_err}"
        try:
            if response.text:
                try:
                    api_error = response.json()
                    error_details = api_error.get('error', {}).get('message', response.text)
                except (json.JSONDecodeError, ValueError):
                    error_details = response.text
            else:
                error_details = "Received an empty response from the API"
        except Exception:
            error_details = f"HTTP {response.status_code}: Unable to parse error response"
        return jsonify({'error': str(error_details)}), response.status_code
    except Exception as e:
        return jsonify({'error': f'An internal server error occurred: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8001)