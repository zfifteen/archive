#!/bin/bash

# Set the classpath
CP="*:../../../lib/util-8.jar"
MAIN_CLASS="com.intellij.mcpserver.stdio.McpStdioRunnerKt"
PORT="64342"

# Start the MCP server in coproc
coproc MCP {
    cd "/Users/velocityworks/Applications/IntelliJ IDEA Ultimate.app/Contents/plugins/mcpserver/lib"
    export IJ_MCP_SERVER_PORT="$PORT"
    java -cp "$CP" "$MAIN_CLASS"
}

# Function to send message and read response
send_message() {
    local msg="$1"
    echo "$msg" >&${MCP[1]}
    # Read response (assuming single line for simplicity)
    read -t 5 line <&${MCP[0]}
    echo "$line"
}

# Initialize
init_msg='{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "GrokDemo", "version": "1.0"}}}'
response=$(send_message "$init_msg")
echo "Initialize response: $response"

# Send initialized notification
init_notif='{"jsonrpc": "2.0", "method": "initialized", "params": {}}'
send_message "$init_notif" > /dev/null  # Discard

# List tools
tools_msg='{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}'
response=$(send_message "$tools_msg")
echo "Tools list response: $response"

# Close coproc
kill $MCP_PID 2>/dev/null