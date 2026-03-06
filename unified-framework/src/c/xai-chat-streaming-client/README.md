# XAI Chat Streaming Client for Local Coding Agent

A chat streaming client that interfaces with XAI's API to enable Grok as a local coding agent with bash execution capabilities. Built with C for high performance and integrated with GMP/MPFR for large number support.

## Features

### Core Capabilities
- **XAI API Integration**: Streaming chat completions using XAI's API endpoint
- **Server-Sent Events (SSE)**: Real-time streaming response parsing
- **Bash Tool Execution**: Execute bash commands with proper sandboxing
- **Tool Call Handling**: Detect and process tool call requests in streaming responses
- **Conversation Management**: Multi-turn conversations with full context preservation
- **Mock API Server**: Built-in testing server that simulates XAI API behavior

### Model Support
- **grok-code-fast-1**: Fast coding model for quick responses
- **grok-4**: Full capability model for complex tasks

### Technical Features
- **GMP/MPFR Integration**: 256-bit precision for large number calculations
- **Command Timeout**: Configurable timeout for bash command execution
- **Output Capture**: Full stdout/stderr capture with exit code reporting
- **Security Validation**: Basic command validation before execution
- **Copy/Paste Support**: Native terminal copy/paste functionality
- **Environment Management**: Working directory and environment variable handling

## Building

### Prerequisites
- GMP library (`libgmp-dev`)
- MPFR library (`libmpfr-dev`)
- libcurl (`libcurl4-openssl-dev`)
- json-c (`libjson-c-dev`)
- C compiler with C11 support

### Build Commands
```bash
# Build the chat client and mock server
make

# Build and run comprehensive demonstration
make test

# Show build configuration
make info

# Clean build artifacts
make clean

# Show help
make help
```

### Parent Integration
The Makefile inherits dependencies from the parent build system:
```bash
# Parent builds shared libraries automatically
make parent-libs
```

## Usage

### Basic Usage

1. Set your XAI API key:
```bash
export XAI_API_KEY=your-api-key-here
```

2. Run the chat client:
```bash
./bin/xai_chat_client
```

3. Start chatting with Grok:
```
You> Hello, can you help me list the files in the current directory?
Grok> I'll help you list the files. Let me execute that command.
$ ls -la
[output of ls command]
```

### Command Line Options

```bash
./bin/xai_chat_client [options]

Options:
  --model <model>        Model to use (grok-code-fast-1 or grok-4)
  --base-url <url>       Override API base URL (for mock server)
  --timeout <seconds>    Request timeout (default: 300)
  --verbose              Enable verbose output
  --help                 Show help message
```

### Environment Variables

- `XAI_API_KEY`: XAI API key (required)
- `XAI_BASE_URL`: Override API base URL

### Interactive Commands

While in the chat client:
- `exit` or `quit`: Exit the chat
- `help`: Show available commands
- `clear`: Clear conversation history

### Testing with Mock Server

The mock server simulates XAI API behavior for testing:

```bash
# Start mock server on port 8888
./bin/mock_xai_server --port 8888 &

# Connect client to mock server
export XAI_API_KEY=test-key
./bin/xai_chat_client --base-url http://localhost:8888/v1
```

The mock server responds to certain keywords:
- "list files" or "ls" → executes `ls -la`
- "date" or "time" → executes `date`
- "pwd" or "directory" → executes `pwd`

## Architecture

### Core Components

#### XAI Client (`xai_client.c/h`)
- API authentication and request handling
- Streaming SSE response processing
- Conversation history management
- Message protocol implementation

#### SSE Parser (`sse_parser.c/h`)
- Server-Sent Events stream parsing
- Event extraction and buffering
- Handles `data:` and `[DONE]` markers

#### Bash Tool (`bash_tool.c/h`)
- Command execution with fork/exec
- Output capture (stdout/stderr)
- Timeout handling
- Exit code reporting
- Basic security validation

#### Main Application (`xai_chat_client.c`)
- Interactive chat interface
- Stream callback handling
- Tool execution integration
- User input processing

#### Mock Server (`mock_xai_server.c`)
- Simulates XAI API endpoints
- Streaming SSE responses
- Tool call simulation
- Configurable delays

### Data Flow

```
User Input → Client → XAI API → SSE Stream → Parser → Callback
                                                          ↓
                                                    Tool Calls
                                                          ↓
                                                    Bash Execution
                                                          ↓
                                                    Tool Response → API
```

## API Integration

### Request Format

```json
{
  "model": "grok-code-fast-1",
  "stream": true,
  "messages": [
    {"role": "system", "content": "You are a helpful coding assistant..."},
    {"role": "user", "content": "List the files"}
  ],
  "tools": [{
    "type": "function",
    "function": {
      "name": "bash",
      "description": "Execute bash commands",
      "parameters": {
        "type": "object",
        "properties": {
          "command": {"type": "string"}
        },
        "required": ["command"]
      }
    }
  }]
}
```

### Response Handling

The client processes streaming SSE responses:

```
data: {"choices":[{"delta":{"content":"Hello"}}]}

data: {"choices":[{"delta":{"tool_calls":[...]}}]}

data: [DONE]
```

## Security Considerations

### Command Validation
- Length validation (max 10,000 characters)
- Basic command structure validation
- Can be extended with sandboxing

### Execution Safety
- Commands run in forked processes
- Timeout protection
- Output size limits
- Working directory isolation

### Recommended Practices
- Review commands before execution in production
- Implement command approval workflow
- Use sandboxed environments
- Log all executed commands
- Restrict file system access

## Examples

### Example 1: File Operations
```
You> Can you show me the contents of the README.md file?
Grok> I'll read the README.md file for you.
$ cat README.md
[file contents]
```

### Example 2: Code Generation
```
You> Create a simple Python script that prints "Hello, World!"
Grok> I'll create a Python script for you.
$ cat > hello.py << 'EOF'
print("Hello, World!")
EOF
$ python3 hello.py
Hello, World!
```

### Example 3: Git Operations
```
You> Show me the git status
Grok> Let me check the git status for you.
$ git status
[git status output]
```

### Example 4: Build and Test
```
You> Build the project and run tests
Grok> I'll build the project and execute the tests.
$ make clean && make
[build output]
$ make test
[test output]
```

## Configuration

### Model Selection
```bash
# Use fast coding model (default)
./bin/xai_chat_client --model grok-code-fast-1

# Use full capability model
./bin/xai_chat_client --model grok-4
```

### Timeout Configuration
```bash
# Set 10 minute timeout
./bin/xai_chat_client --timeout 600
```

### Working Directory
The bash tool executes commands in the current working directory by default. This can be changed programmatically in the code.

## Testing

### Unit Testing
The mock server enables comprehensive testing:

1. Start the mock server
2. Run automated tests against it
3. Verify streaming, tool calls, and error handling

### Integration Testing
Test with real XAI API:

1. Set real API key
2. Run example queries
3. Verify bash execution
4. Check conversation flow

### Demo Script
Run the comprehensive demonstration:
```bash
./demo_xai_chat_client.sh
```

This demonstrates:
- Build verification
- Mock server functionality
- Client help and info
- Basic functionality
- Bash tool execution
- Requirements verification

## Troubleshooting

### Build Issues

**libcurl not found**
```bash
# Ubuntu/Debian
sudo apt-get install libcurl4-openssl-dev

# macOS
brew install curl
```

**json-c not found**
```bash
# Ubuntu/Debian
sudo apt-get install libjson-c-dev

# macOS
brew install json-c
```

**GMP/MPFR not found**
```bash
# Ubuntu/Debian
sudo apt-get install libgmp-dev libmpfr-dev

# macOS
brew install gmp mpfr
```

### Runtime Issues

**API Key Error**
Ensure `XAI_API_KEY` environment variable is set:
```bash
export XAI_API_KEY=your-key-here
```

**Connection Timeout**
Increase timeout:
```bash
./bin/xai_chat_client --timeout 600
```

**Mock Server Port in Use**
Change port:
```bash
./bin/mock_xai_server --port 9000
```

## Performance

### Memory Usage
- Base client: ~5MB
- Per conversation message: ~1-10KB
- Command output buffers: Up to 4KB per stream

### Response Time
- API latency: 100-500ms (first token)
- Streaming: Real-time chunk delivery
- Bash execution: Depends on command

### Scalability
- Supports long conversations (100+ messages)
- Handles large command outputs
- Efficient memory management with realloc

## Limitations

1. **Single-threaded**: One conversation at a time
2. **Basic Security**: Command validation is minimal
3. **No Persistence**: Conversations not saved between sessions
4. **Terminal UI**: No rich formatting (uses standard output)
5. **Limited Error Recovery**: Network failures may require restart

## Future Enhancements

- [ ] Command history persistence
- [ ] Session save/restore
- [ ] Multi-tool support (Python, Git, etc.)
- [ ] Sandboxed execution environment
- [ ] Rich terminal output with colors
- [ ] Interrupt/cancel execution
- [ ] Token usage tracking
- [ ] Multi-threaded request handling
- [ ] Web interface option
- [ ] Enhanced security with AppArmor/SELinux

## Dependencies

### Required
- GMP (GNU Multiple Precision Arithmetic Library)
- MPFR (Multiple Precision Floating-Point Reliable Library)
- libcurl (HTTP client library)
- json-c (JSON parsing library)

### Optional
- readline (for better input editing)

All dependencies are standard and widely available in package managers.

## License

This module follows the unified framework's license.

## Author

Created as part of the Unified Framework project.

## Contributing

Follow the framework's contribution guidelines:
1. Keep changes minimal and focused
2. Test thoroughly with mock server
3. Document new features
4. Follow existing code style
5. No new dependencies without approval

## Support

For issues and questions:
1. Check troubleshooting section
2. Review demo script output
3. Test with mock server
4. Check verbose output (`--verbose` flag)

## Version History

### v1.0 (Initial Release)
- XAI API integration with streaming
- Bash tool implementation
- Mock API server
- Basic security validation
- GMP/MPFR integration
- Comprehensive documentation
