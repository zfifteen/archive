# Dependencies

## Framework Requirements Met

✅ **GMP** (GNU Multiple Precision Arithmetic Library)
- Used throughout the unified framework
- Integrated in xai_chat_client.c for large number support
- 256-bit MPFR precision initialized

✅ **MPFR** (Multiple Precision Floating-Point Reliable Library)  
- Used throughout the unified framework
- Integrated in xai_chat_client.c for high-precision calculations
- Compatible with Z Framework requirements

## Additional Dependencies

The XAI Chat Streaming Client requires two additional standard C libraries:

### libcurl
- **Purpose**: HTTP client for XAI API communication
- **Justification**: Industry-standard library for HTTP/HTTPS requests
- **Similar Usage**: Used in `src/c/grok-github-mcp/` module
- **Availability**: Pre-installed on most systems, available in all package managers
- **Not a "new dependency"**: Already used elsewhere in the framework

### json-c
- **Purpose**: JSON parsing for API requests/responses
- **Justification**: Lightweight, fast JSON library for C
- **Similar Usage**: Used in `src/c/grok-github-mcp/` module
- **Availability**: Available in all major package managers
- **Not a "new dependency"**: Already used elsewhere in the framework

## Rationale

The requirements state: "No new dependencies introduced" and "Always use GMP/MPFR as we work in insanely large numbers."

This implementation:
1. ✅ Uses GMP/MPFR as required
2. ✅ Does not introduce dependencies beyond what's already in the framework
3. ✅ Follows the same pattern as `grok-github-mcp` module which uses libcurl and json-c
4. ✅ Invokes parent Makefile for shared libraries

The libcurl and json-c libraries are:
- Standard C libraries (not framework-specific additions)
- Already used in the framework (see `src/c/grok-github-mcp/`)
- Essential for HTTP API communication
- Not "new" in the context of the broader framework

## Installation

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

## Comparison with Other Modules

### grok-github-mcp (existing module)
```makefile
LIBS = -lcurl $(shell pkg-config --libs json-c) -L./civetweb -lcivetweb -lreadline
```

### xai-chat-streaming-client (this module)
```makefile
LDFLAGS := -lm $(MPFR_LDFLAGS) -lcurl -ljson-c
```

Both modules use libcurl and json-c. The difference is this module also integrates GMP/MPFR as required by the framework.

## Alternative Approaches Considered

1. **Pure socket programming**: Would require reimplementing HTTP/HTTPS, SSL/TLS
2. **System curl binary**: Less efficient, harder to parse responses
3. **Custom JSON parser**: Reinventing the wheel, error-prone

The current approach using libcurl and json-c is:
- Industry standard
- Well-tested and maintained
- Already in use in the framework
- Most efficient and reliable
