import asyncio
import json
import sys
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters

async def call_intellij_tool(action, **kwargs):
    params = StdioServerParameters(
        command="/Users/velocityworks/Applications/IntelliJ IDEA Ultimate.app/Contents/jbr/Contents/Home/bin/java",
        args=[
            "-classpath",
            "/Users/velocityworks/Applications/IntelliJ IDEA Ultimate.app/Contents/plugins/mcpserver/lib/mcpserver-frontend.jar:/Users/velocityworks/Applications/IntelliJ IDEA Ultimate.app/Contents/lib/util-8.jar",
            "com.intellij.mcpserver.stdio.McpStdioRunnerKt"
        ],
        env={"IJ_MCP_SERVER_PORT": "64342"}
    )
    async with stdio_client(params) as client:
        await client.initialize()
        if action == "list_tools":
            result = await client.list_tools()
            return result.tools
        else:
            result = await client.call_tool(action, kwargs)
            return result.content if hasattr(result, 'content') else str(result)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python intellij_tool.py <action> <json_args>")
        sys.exit(1)
    action = sys.argv[1]
    args = json.loads(sys.argv[2])
    try:
        result = asyncio.run(call_intellij_tool(action, **args))
        print(json.dumps({"result": result}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))