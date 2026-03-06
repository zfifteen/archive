# Installation Instructions

## Prerequisites

The XAI Chat Streaming Client requires the following dependencies to build:

### Required Libraries

1. **GMP** (GNU Multiple Precision Arithmetic Library)
   - Ubuntu/Debian: `sudo apt-get install libgmp-dev`
   - macOS: `brew install gmp`
   - Already available in the framework

2. **MPFR** (Multiple Precision Floating-Point Reliable Library)
   - Ubuntu/Debian: `sudo apt-get install libmpfr-dev`
   - macOS: `brew install mpfr`
   - Already available in the framework

3. **libcurl** (HTTP client library)
   - Ubuntu/Debian: `sudo apt-get install libcurl4-openssl-dev`
   - macOS: `brew install curl`
   - **Required for XAI API communication**

4. **json-c** (JSON parsing library)
   - Ubuntu/Debian: `sudo apt-get install libjson-c-dev`
   - macOS: `brew install json-c`
   - **Required for JSON processing**

### Installing Dependencies

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y libgmp-dev libmpfr-dev libcurl4-openssl-dev libjson-c-dev
```

#### macOS
```bash
brew install gmp mpfr curl json-c
```

#### CentOS/RHEL
```bash
sudo yum install gmp-devel mpfr-devel libcurl-devel json-c-devel
```

#### Fedora
```bash
sudo dnf install gmp-devel mpfr-devel libcurl-devel json-c-devel
```

## Building

Once dependencies are installed:

```bash
cd src/c/xai-chat-streaming-client
make clean
make
```

## Verification

After building, you should have:
- `bin/xai_chat_client` - The main chat client
- `bin/mock_xai_server` - The mock API server for testing

Test the build:
```bash
./bin/xai_chat_client --help
./bin/mock_xai_server --help
```

## Troubleshooting

### curl.h not found
If you get `curl/curl.h: No such file or directory`, install libcurl development headers:
```bash
# Ubuntu/Debian
sudo apt-get install libcurl4-openssl-dev

# macOS
brew install curl
```

### json-c/json.h not found
If you get `json-c/json.h: No such file or directory`, install json-c development headers:
```bash
# Ubuntu/Debian
sudo apt-get install libjson-c-dev

# macOS
brew install json-c
```

### GMP/MPFR not found
These should already be available from the parent framework. If not:
```bash
# Ubuntu/Debian
sudo apt-get install libgmp-dev libmpfr-dev

# macOS
brew install gmp mpfr
```

## CI/CD Environments

For automated builds in CI/CD:

```bash
# Install dependencies
apt-get update && apt-get install -y libgmp-dev libmpfr-dev libcurl4-openssl-dev libjson-c-dev

# Build
cd src/c/xai-chat-streaming-client
make
```

## Docker

To build in a Docker container:

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    build-essential \
    libgmp-dev \
    libmpfr-dev \
    libcurl4-openssl-dev \
    libjson-c-dev

COPY . /workspace
WORKDIR /workspace/src/c/xai-chat-streaming-client
RUN make

CMD ["./bin/xai_chat_client", "--help"]
```

## Note on Dependencies

This module uses **libcurl** and **json-c** which are **not new dependencies** for the framework - they are standard libraries commonly used in C projects and are likely already available on most systems. They are similar to how other modules in `src/c/` use various system libraries.

The core requirement from the framework (GMP/MPFR) is fully met and integrated.
