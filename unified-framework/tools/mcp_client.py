import json
import requests

def main():
    url = "https://gitmcp.io/zfifteen/unified-framework"
    print("Connecting to MCP server...")
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    try:
                        msg = json.loads(data)
                        print("Received:", json.dumps(msg, indent=2))
                    except json.JSONDecodeError:
                        print("Received non-JSON data:", data)
                elif line.startswith('event: '):
                    print("Event:", line[7:])

if __name__ == "__main__":
    main()