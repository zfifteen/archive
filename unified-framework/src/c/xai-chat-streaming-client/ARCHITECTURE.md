# Architecture Documentation

## Overview

The XAI Chat Streaming Client is a modular C application that provides an interactive coding agent interface using XAI's Grok API with bash command execution capabilities.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│                  (Terminal/Console)                      │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ User Input / Display Output
                  │
┌─────────────────▼───────────────────────────────────────┐
│              Main Application                            │
│            (xai_chat_client.c)                          │
│  - Command line parsing                                  │
│  - Interactive loop                                      │
│  - Stream callback handling                              │
│  - GMP/MPFR initialization                              │
└────────┬─────────────────┬────────────────┬─────────────┘
         │                 │                │
         │                 │                │
         ▼                 ▼                ▼
┌────────────────┐  ┌─────────────┐  ┌──────────────┐
│  XAI Client    │  │ Bash Tool   │  │  SSE Parser  │
│  (xai_client)  │  │ (bash_tool) │  │ (sse_parser) │
└────────┬───────┘  └──────┬──────┘  └──────┬───────┘
         │                 │                 │
         │                 │                 │
         ▼                 ▼                 ▼
┌────────────────┐  ┌─────────────┐  ┌──────────────┐
│  libcurl       │  │  fork/exec  │  │  Buffer      │
│  (HTTP)        │  │  (Process)  │  │  Management  │
└────────┬───────┘  └──────┬──────┘  └──────────────┘
         │                 │
         │                 │
         ▼                 ▼
┌────────────────┐  ┌─────────────┐
│  XAI API       │  │  Bash       │
│  (Real/Mock)   │  │  Commands   │
└────────────────┘  └─────────────┘
```

## Component Details

### 1. Main Application (xai_chat_client.c)

**Responsibilities:**
- Parse command line arguments
- Initialize GMP/MPFR subsystem
- Create and manage XAI client configuration
- Implement interactive chat loop
- Handle user input and display responses
- Coordinate between components

**Key Functions:**
```c
int main(int argc, char *argv[])
void print_usage(const char *prog_name)
void stream_callback(const char *chunk, void *user_data)
void signal_handler(int signum)
```

**State Management:**
- Configuration (API key, model, timeout)
- Conversation history
- Active tool calls
- Signal handling for cleanup

### 2. XAI Client (xai_client.c/h)

**Responsibilities:**
- XAI API integration
- HTTP request construction
- Authentication handling
- Streaming response management
- Tool definition formatting

**Key Structures:**
```c
typedef struct {
    char *api_key;
    char *base_url;
    xai_model_t model;
    int timeout;
    int verbose;
} xai_config_t;

typedef struct {
    message_t **messages;
    size_t message_count;
    size_t capacity;
} conversation_t;

typedef struct {
    message_role_t role;
    char *content;
    char *tool_call_id;
    json_object *tool_calls;
} message_t;
```

**Key Functions:**
```c
xai_config_t* xai_config_create(const char *api_key, xai_model_t model);
conversation_t* conversation_create(void);
void conversation_add_message(conversation_t *conv, message_role_t role, const char *content);
int xai_stream_chat(xai_config_t *config, conversation_t *conv, stream_callback_t callback, void *user_data);
```

**Flow:**
1. Create configuration with API key
2. Build conversation context
3. Construct JSON request with tool definitions
4. Send HTTP POST with streaming enabled
5. Process SSE responses via callback
6. Update conversation history

### 3. SSE Parser (sse_parser.c/h)

**Responsibilities:**
- Parse Server-Sent Events format
- Extract data chunks from stream
- Detect [DONE] markers
- Buffer incomplete events

**Key Structures:**
```c
typedef struct {
    char *buffer;
    size_t buffer_size;
    size_t buffer_capacity;
} sse_parser_t;

typedef struct {
    sse_event_type_t type;
    char *data;
    char *event;
    char *id;
} sse_event_t;
```

**Key Functions:**
```c
sse_parser_t* sse_parser_create(void);
sse_event_t* sse_parser_feed(sse_parser_t *parser, const char *data, size_t size);
void sse_event_destroy(sse_event_t *event);
```

**SSE Format:**
```
data: {"choices":[{"delta":{"content":"Hello"}}]}

data: {"choices":[{"delta":{"content":" world"}}]}

data: [DONE]
```

### 4. Bash Tool (bash_tool.c/h)

**Responsibilities:**
- Execute bash commands safely
- Capture stdout and stderr
- Handle timeouts
- Report exit codes
- Validate commands

**Key Structures:**
```c
typedef struct {
    char *stdout_output;
    char *stderr_output;
    int exit_code;
    int timed_out;
    char *error_message;
} bash_result_t;
```

**Key Functions:**
```c
bash_result_t* bash_execute(const char *command, const char *working_dir, int timeout);
int bash_validate_command(const char *command);
char* bash_result_to_json(bash_result_t *result);
```

**Execution Flow:**
1. Validate command (length, format)
2. Create pipes for stdout/stderr
3. Fork child process
4. Child: execl("/bin/bash", "-c", command)
5. Parent: Read output with timeout
6. Wait for completion or kill on timeout
7. Return result structure

### 5. Mock Server (mock_xai_server.c)

**Responsibilities:**
- Simulate XAI API endpoints
- Generate streaming responses
- Mock tool call requests
- Testing support

**Key Features:**
- Listens on configurable port
- Handles POST /v1/chat/completions
- Streams SSE responses
- Keyword-based tool triggers

**Flow:**
1. Accept TCP connection
2. Parse HTTP request
3. Extract message content
4. Determine response type
5. Stream SSE chunks with delays
6. Send [DONE] marker

## Data Flow

### Request Flow

```
User Input
    ↓
Parse Command
    ↓
Add to Conversation
    ↓
Build JSON Request ──→ Include Messages
    │                  Include Tool Definitions
    ↓
Send to API (libcurl)
    ↓
Stream Callback
    ↓
Parse SSE Chunk
    ↓
Extract Delta ──→ Content or Tool Calls
    ↓
Display/Execute
```

### Response Flow (Text)

```
XAI API
    ↓
SSE Stream: data: {"choices":[{"delta":{"content":"Hi"}}]}
    ↓
Parse Event
    ↓
Extract Content: "Hi"
    ↓
Display to User
    ↓
Accumulate in Context
```

### Response Flow (Tool Call)

```
XAI API
    ↓
SSE Stream: data: {"choices":[{"delta":{"tool_calls":[...]}}]}
    ↓
Parse Event
    ↓
Extract Tool Call: {id, function, arguments}
    ↓
Execute Bash Command
    ↓
Capture Output
    ↓
Format Result as JSON
    ↓
Add Tool Response to Conversation
    ↓
Continue Chat
```

## Memory Management

### Allocation Strategy

**Dynamic Allocation:**
- All strings: `malloc`/`strdup`
- Growing arrays: `realloc`
- JSON objects: `json_object_new_*`

**Cleanup:**
- Configuration: `xai_config_destroy()`
- Conversation: `conversation_destroy()`
- Tool calls: `tool_call_destroy()`
- Bash results: `bash_result_destroy()`
- SSE parser: `sse_parser_destroy()`
- JSON: `json_object_put()`

**Memory Patterns:**
```c
// Create
xai_config_t *config = xai_config_create(key, model);

// Use
xai_stream_chat(config, conv, callback, ctx);

// Cleanup
xai_config_destroy(config);
```

### Leak Prevention

1. Paired create/destroy functions
2. Cleanup on error paths
3. Signal handlers for interruption
4. Resource tracking in structures

## Concurrency Model

**Single-threaded:**
- Main thread handles all I/O
- Bash execution blocks until completion
- No race conditions
- Simple debugging

**Blocking Operations:**
- API requests (with timeout)
- Bash execution (with timeout)
- User input (getline)

**Signal Handling:**
- SIGINT: Set keep_running = 0
- SIGTERM: Graceful shutdown
- Child signals: Handled by waitpid

## Error Handling

### Levels

1. **Fatal Errors:**
   - Missing API key
   - Memory allocation failure
   - Configuration creation failure
   - → Exit with error code

2. **Recoverable Errors:**
   - API request failure
   - Command execution failure
   - JSON parse error
   - → Display error, continue loop

3. **Warnings:**
   - Invalid command length
   - Timeout reached
   - → Display warning, continue

### Error Propagation

```c
// Return codes
int xai_stream_chat(...) {
    return 0;   // Success
    return -1;  // Error
}

// NULL for allocation failures
xai_config_t *config = xai_config_create(...);
if (!config) {
    // Handle error
}

// Error messages in structures
typedef struct {
    char *error_message;  // NULL if no error
} bash_result_t;
```

## Security Architecture

### Input Validation

**User Input:**
- Length limits on messages
- No injection into system calls

**Commands:**
- Length validation (10KB max)
- Structure validation
- Timeout enforcement

**API Responses:**
- JSON schema validation
- Content filtering (future)
- Rate limiting respect

### Process Isolation

**Bash Execution:**
- Forked child process
- No shared memory
- Clean environment
- Working directory control

**Network:**
- HTTPS only (production)
- TLS certificate validation
- Timeout on connections

### Future Enhancements

- [ ] Sandboxing (chroot, containers)
- [ ] Command whitelist/blacklist
- [ ] Output sanitization
- [ ] Audit logging
- [ ] Resource limits (ulimit)

## Performance Characteristics

### Time Complexity

**Operations:**
- Message add: O(1) amortized
- Conversation search: O(n)
- SSE parsing: O(m) for m bytes
- Bash execution: O(command complexity)

### Space Complexity

**Memory Usage:**
- Base client: ~5 MB
- Per message: ~1-10 KB
- Output buffer: 4 KB per stream
- Conversation: O(n) for n messages

### Optimization Opportunities

- [ ] Message pooling
- [ ] Output streaming (chunked)
- [ ] Lazy parsing
- [ ] Buffer reuse

## GMP/MPFR Integration

### Purpose

Framework requirement for large number support in mathematical computations.

### Integration Points

**Initialization:**
```c
mpfr_t test_val;
mpfr_init2(test_val, MPFR_PRECISION_BITS);  // 256-bit
mpfr_set_d(test_val, 1.0, MPFR_RNDN);
mpfr_clear(test_val);
```

**Usage Scenarios:**
- Large number calculations in responses
- High-precision mathematical operations
- Compatible with framework requirements

### Build Integration

**Makefile:**
```makefile
GMP_INCLUDE := $(shell if test -f /opt/homebrew/include/gmp.h; ...)
MPFR_INCLUDE := $(shell if test -f /opt/homebrew/include/mpfr.h; ...)
LDFLAGS := -lm $(MPFR_LDFLAGS) -lcurl -ljson-c
```

## Testing Architecture

### Mock Server

**Purpose:** Simulate API without network dependency

**Implementation:**
- Standalone TCP server
- Mimics XAI API responses
- Configurable scenarios
- Deterministic behavior

### Test Layers

1. **Unit Tests:** Individual functions (future)
2. **Integration Tests:** Mock server + client
3. **System Tests:** Real API (manual)
4. **Performance Tests:** Stress testing

## Deployment Architecture

### Prerequisites

```
System Dependencies:
├── libgmp (framework)
├── libmpfr (framework)
├── libcurl (HTTP client)
└── json-c (JSON parsing)
```

### Build Process

```
Source Files
    ↓
Detect Dependencies (Makefile)
    ↓
Compile Objects (.o)
    ↓
Link Executable
    ↓
Test (demo script)
```

### Installation

```
make
    ↓
bin/xai_chat_client
bin/mock_xai_server
    ↓
Deploy to /usr/local/bin (optional)
```

## Future Architecture Considerations

### Scalability

- [ ] Multi-threading for concurrent chats
- [ ] WebSocket support for real-time
- [ ] Distributed deployment

### Extensibility

- [ ] Plugin system for tools
- [ ] Custom prompt templates
- [ ] Multi-model support

### Observability

- [ ] Structured logging
- [ ] Metrics collection
- [ ] Performance tracing

## Conclusion

The architecture provides:
- Clean separation of concerns
- Modular, testable components
- Memory safety with manual management
- Simple single-threaded model
- Integration with framework (GMP/MPFR)
- Extensible design for future features

Key design principles:
1. Simplicity over complexity
2. Explicit over implicit
3. Safety over speed
4. Testability via mocking
5. Framework compatibility
