# Z5D MCP Server Docker

This directory contains a Docker setup for running the Z5D MCP (Model Context Protocol) server.

## Building the Image

```bash
docker build -t z5d-mcp-server .
```

## Running with Docker Compose

```bash
docker-compose up
```

This will start the MCP server on port 8000.

## Running Directly

```bash
docker run -p 8000:8000 -e MCP_HOST=0.0.0.0 -e MCP_PORT=8000 -v $(pwd)/../..:/app/data:ro z5d-mcp-server
```

## Usage

The MCP server provides tools for Z Framework development, including primes, hashing, RSA grids, with geometric resolutions.

Connect your MCP client to `http://localhost:8000`.