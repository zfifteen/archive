import asyncio
from fastmcp import Client, FastMCP

async def main():
    # Import the server instance (assuming research_server.py defines 'mcp' globally)
    import research_server

    # Test in-memory with Client
    async with Client(research_server.mcp) as client:
        # List tools
        tools = await client.list_tools()
        print("Available tools:", [tool.name for tool in tools])

        # Test compute_zeta_zeros
        result = await client.call_tool("compute_zeta_zeros", {"n": 3})
        print("Zeta zeros (first 3):", result.content[0].text)

        # Test compute_curvature
        result = await client.call_tool("compute_curvature", {"n": 10})
        print("Curvature for n=10:", result.content[0].text)

        # Test geometric_resolution
        result = await client.call_tool("geometric_resolution", {"n": 5, "k": 0.3})
        print("Geometric resolution for n=5:", result.content[0].text)

        # Test resource
        result = await client.read_resource("data://zeta_zeros_sample")
        print("Sample zeta zeros (truncated):", str(result)[:200] + "...")

if __name__ == "__main__":
    asyncio.run(main())