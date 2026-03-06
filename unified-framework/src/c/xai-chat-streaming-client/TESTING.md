# Testing Guide

## Overview

The XAI Chat Streaming Client includes comprehensive testing capabilities through a mock API server and demonstration script.

## Quick Start

```bash
# Build everything
make

# Run full demonstration
./demo_xai_chat_client.sh

# Or use the make target
make test
```

## Test Components

### 1. Mock API Server

The mock server simulates XAI API behavior for testing without requiring an actual API key.

**Start the mock server:**
```bash
./bin/mock_xai_server --port 8888
```

**Features:**
- Simulates streaming SSE responses
- Returns tool call requests for specific keywords
- Configurable port
- Realistic response delays (50ms per chunk)

**Keyword Triggers:**
- "list files" or "ls" → Tool call for `ls -la`
- "date" or "time" → Tool call for `date`
- "pwd" or "directory" → Tool call for `pwd`

### 2. Client Testing with Mock Server

**Basic test:**
```bash
# Terminal 1: Start mock server
./bin/mock_xai_server --port 8888

# Terminal 2: Connect client
export XAI_API_KEY=test-key
./bin/xai_chat_client --base-url http://localhost:8888/v1
```

**Automated test:**
```bash
# Start mock server in background
./bin/mock_xai_server --port 8888 &
MOCK_PID=$!

# Run client tests
export XAI_API_KEY=test-key
echo "hello" | timeout 5 ./bin/xai_chat_client --base-url http://localhost:8888/v1

# Cleanup
kill $MOCK_PID
```

### 3. Demonstration Script

The demo script performs comprehensive validation:

```bash
./demo_xai_chat_client.sh
```

**What it tests:**
1. Implementation verification (files present)
2. Build verification (compiles successfully)
3. Mock server functionality
4. Client help and info
5. Integration features
6. Requirements verification

**Output:**
- ✅ marks successful tests
- ❌ marks failed tests
- Colored output for readability
- Summary at end

## Test Scenarios

### Scenario 1: Basic Text Response

**Test:**
```bash
You> Hello, how are you?
Grok> I'm a mock XAI server. I received your message and I'm here to help!
```

**Expected:**
- Streaming response appears word by word
- No tool calls
- Message added to conversation history

### Scenario 2: File Listing

**Test:**
```bash
You> Can you list the files in the current directory?
Grok> [executing bash command]
$ ls -la
[output of ls command]
```

**Expected:**
- Tool call detected
- Command executed
- Output displayed
- Tool response added to conversation

### Scenario 3: Date/Time

**Test:**
```bash
You> What's the current date and time?
Grok> [executing bash command]
$ date
[current date/time]
```

**Expected:**
- Tool call for date command
- Current timestamp displayed

### Scenario 4: Working Directory

**Test:**
```bash
You> Show me the current working directory
Grok> [executing bash command]
$ pwd
[current directory path]
```

**Expected:**
- pwd command executed
- Path displayed

### Scenario 5: Conversation History

**Test:**
```bash
You> Hello
Grok> Hi there!
You> What did I just say?
Grok> You said "Hello"
```

**Expected:**
- Previous messages remembered
- Context maintained

### Scenario 6: Error Handling

**Test:**
```bash
You> [invalid command that times out]
```

**Expected:**
- Timeout handled gracefully
- Error message displayed
- Client remains responsive

## Integration Testing

### With Real XAI API

**Prerequisites:**
- Valid XAI API key
- Internet connection

**Test:**
```bash
export XAI_API_KEY=your-real-api-key
./bin/xai_chat_client --model grok-code-fast-1
```

**Manual test cases:**
1. Simple greeting
2. Code generation request
3. File operation request
4. Multi-turn conversation
5. Long-running command

### With Parent Framework

**Test GMP/MPFR integration:**
```bash
# The client initializes MPFR on startup
./bin/xai_chat_client --verbose
# Should show no errors about GMP/MPFR
```

**Test parent build integration:**
```bash
cd ..
make shared
cd xai-chat-streaming-client
make parent-libs
# Should invoke parent successfully
```

## Performance Testing

### Response Time

**Measure streaming latency:**
```bash
time echo "hello" | timeout 5 ./bin/xai_chat_client --base-url http://localhost:8888/v1
```

**Expected:**
- First chunk: < 100ms
- Subsequent chunks: 50ms intervals
- Total time: < 5 seconds

### Memory Usage

**Monitor memory:**
```bash
# Start client in background
./bin/xai_chat_client &
CLIENT_PID=$!

# Check memory usage
ps aux | grep $CLIENT_PID

# Expected: ~5MB base memory
```

### Stress Testing

**Multiple messages:**
```bash
for i in {1..10}; do
    echo "Message $i" | timeout 5 ./bin/xai_chat_client --base-url http://localhost:8888/v1
done
```

**Expected:**
- No memory leaks
- Consistent response times
- No crashes

## Security Testing

### Command Validation

**Test invalid commands:**
```bash
# Test length limit (10,000 chars)
python3 -c "print('x' * 20000)" > /tmp/long_cmd.txt
# Client should reject

# Test empty command
echo "" | ./bin/xai_chat_client
# Should handle gracefully
```

### Timeout Handling

**Test long-running command:**
```bash
# Set short timeout
# Command: sleep 120
# Expected: Timeout after configured time
```

### Output Limits

**Test large output:**
```bash
# Command: cat /dev/urandom | head -c 1000000
# Expected: Handle large output properly
```

## Regression Testing

### After Code Changes

**Run full test suite:**
```bash
make clean
make
./demo_xai_chat_client.sh
```

**Check for:**
- Build warnings
- Memory leaks (valgrind)
- Segmentation faults
- Logic errors

### Valgrind Testing

**Memory leak detection:**
```bash
valgrind --leak-check=full ./bin/xai_chat_client --help
```

**Expected:**
- No memory leaks
- No invalid memory access
- Clean exit

## Continuous Integration

### CI Pipeline

```yaml
# Example GitHub Actions workflow
- name: Install dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y libgmp-dev libmpfr-dev libcurl4-openssl-dev libjson-c-dev

- name: Build
  run: |
    cd src/c/xai-chat-streaming-client
    make clean
    make

- name: Test
  run: |
    cd src/c/xai-chat-streaming-client
    ./demo_xai_chat_client.sh
```

## Test Coverage

### Current Coverage

- ✅ API client initialization
- ✅ Configuration management
- ✅ Conversation creation/destruction
- ✅ Message handling
- ✅ SSE parsing
- ✅ Tool call detection
- ✅ Bash execution
- ✅ Timeout handling
- ✅ Mock server responses
- ✅ Help/info display
- ⚠️  Real API integration (manual)
- ⚠️  Network error handling (manual)
- ⚠️  Rate limiting (manual)

### Future Test Additions

- [ ] Unit tests for individual functions
- [ ] Network failure simulation
- [ ] Rate limit handling
- [ ] Malformed JSON handling
- [ ] Concurrent request handling
- [ ] Session persistence
- [ ] Command history

## Debugging

### Enable Verbose Mode

```bash
./bin/xai_chat_client --verbose
```

**Shows:**
- Request JSON
- Response chunks
- Tool call details
- Debug messages

### GDB Debugging

```bash
gdb ./bin/xai_chat_client
(gdb) run --base-url http://localhost:8888/v1
(gdb) break xai_stream_chat
(gdb) continue
```

### Log Analysis

**Enable logging:**
```bash
./bin/xai_chat_client --verbose 2>&1 | tee client.log
```

**Check for:**
- API errors
- Parsing errors
- Memory issues
- Unexpected behavior

## Troubleshooting Tests

### Mock Server Not Starting

**Issue:** Port already in use
**Solution:**
```bash
# Find process using port
lsof -i :8888
# Kill it or use different port
./bin/mock_xai_server --port 9000
```

### Client Connection Timeout

**Issue:** Can't connect to mock server
**Solution:**
```bash
# Check server is running
ps aux | grep mock_xai_server
# Check port matches
netstat -an | grep 8888
```

### Build Failures

**Issue:** Missing dependencies
**Solution:**
```bash
# Install missing libraries
sudo apt-get install libcurl4-openssl-dev libjson-c-dev
```

## Test Results Format

Expected output from demo script:

```
🚀 Starting XAI Chat Streaming Client demonstration...

=== PHASE 1: IMPLEMENTATION VERIFICATION ===
✅ New folder under 'src/c/': xai-chat-streaming-client
✅ All artifacts contained in new folder
...

=== PHASE 8: REQUIREMENTS VERIFICATION ===
✅ REQUIREMENT CHECKLIST:
1. ✅ New folder under 'src/c/'
2. ✅ All artifacts contained
...

🎯 XAI Chat Streaming Client demonstration complete!
```

## Conclusion

The testing infrastructure provides:
- Automated testing via mock server
- Manual testing with real API
- Performance benchmarking
- Security validation
- Integration verification
- CI/CD compatibility

Run `make test` to execute the full test suite.
