# z-mcp-server (C) — Scaffolding

A minimal C HTTP server exposing dummy MCP "tools" on:

- GET /tools/count  ⇒ `{ "count": 42 }`
- GET /tools/echo?msg=hello ⇒ `{ "echo": "hello" }`
- GET /healthz ⇒ `{ "status": "ok" }`

## Requirements

- gcc
- pthreads
- CivetWeb (https://github.com/civetweb/civetweb)

### Installing Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install libcivetweb-dev build-essential
```

**macOS:**
CivetWeb may not be available via Homebrew. You can build from source:
```bash
git clone https://github.com/civetweb/civetweb.git
cd civetweb
make install
```

## Build & Run

```bash
cd src/c/mcp
make
./mcp-server                                    # Defaults to 127.0.0.1:8080
./mcp-server --host 0.0.0.0 --port 8080       # Custom host/port
```

## Apple M1 Max Optimizations

✅ **Implemented**: This server now includes Apple M1 Max specific optimizations:
- ARM64 architecture-specific compiler flags (`-march=armv8.4-a+fp16+rcpc+dotprod+crypto`)
- Apple M1 CPU tuning (`-mtune=apple-m1 -mcpu=apple-m1`)
- Fast math optimizations (`-ffast-math -funroll-loops -fomit-frame-pointer`)
- Performance core affinity for optimal thread scheduling
- Automatic detection and activation on ARM64 systems

## Next Steps

1. Swap out `/tools/count` and `/tools/echo` handlers with your optimized Z-framework logic.
2. Add new endpoints for Z-framework computations (prime checking, density calculations, etc.).
3. Write unit tests (e.g. with CMocka or Check) and CI in GitHub Actions.
4. Harden TLS (OpenSSL/BoringSSL), auth, and sandboxing as needed.

## Security Features

- JSON escaping prevents injection attacks in echo endpoint
- Port validation ensures valid port ranges (1-65535)
- Graceful error handling for malloc failures
- Safe defaults (localhost binding)