# iOS Agent CLI MVP

A SwiftUI iOS application that provides a local terminal interface with an embedded shell session and a simple agent CLI tool.

## Overview

This experimental iOS app demonstrates a terminal-based agent interface running directly on iOS. It features:

- **Full SwiftUI Terminal UI** - Uses [SwiftTerm](https://github.com/migueldeicaza/SwiftTerm) for VT100/Xterm terminal emulation
- **PTY (Pseudo-Terminal) Session** - Spawns and manages a shell process with proper terminal I/O
- **Agent CLI Script** - A simple JSON-based command interface (`agent-cli`) for building agent tools
- **iOS Sandbox Compatible** - Works within iOS security constraints without jailbreak

## Architecture

```
MyAgentCLI/
├── MyAgentCLIApp.swift      # SwiftUI app entry point
├── TerminalScreen.swift      # Main view with status bar and terminal
├── TerminalView.swift        # SwiftUI wrapper for SwiftTerm
├── ShellSession.swift        # Shell lifecycle and I/O management
├── PTYSession.swift          # Low-level PTY operations
└── Resources/
    └── agent-cli             # JSON-based agent script
```

### Component Details

1. **MyAgentCLIApp.swift** - Standard SwiftUI app lifecycle
2. **TerminalScreen.swift** - Main UI with terminal view, status bar, and connect/reset controls
3. **TerminalView.swift** - Bridges SwiftTerm's UIKit terminal to SwiftUI
4. **ShellSession.swift** - Manages shell process lifecycle, coordinates PTY I/O
5. **PTYSession.swift** - Handles PTY allocation, process spawning via `posix_spawn`
6. **agent-cli** - Shell script that reads JSON commands and returns JSON responses

## Requirements

- **Xcode 15.0+**
- **iOS 16.0+** (Simulator or Device)
- **macOS** for building (Xcode is macOS-only)

## Building the Project

1. **Open in Xcode**
   ```bash
   cd experiments/ios-agent-cli
   open MyAgentCLI.xcodeproj
   ```

2. **Wait for Package Resolution**
   - Xcode will automatically fetch the SwiftTerm dependency
   - This may take a few moments on first open

3. **Select Target**
   - Choose an iOS Simulator or connected device from the scheme selector

4. **Build and Run**
   - Press `Cmd+R` or click the Run button
   - The app will compile and launch

## Usage

### Basic Terminal Usage

When the app launches, you'll see:
- A status bar at the top showing connection status and PID
- A full-screen terminal below
- The shell starts automatically

Try basic commands:
```bash
echo "Hello, iOS Terminal!"
pwd
ls -la
```

### Using agent-cli

The `agent-cli` script is automatically installed to `~/bin/agent-cli` (in the app's Documents directory) and added to `$PATH`.

**Echo command example:**
```bash
agent-cli '{"op":"echo","text":"hello"}'
```

Expected output:
```json
{"ok":true,"result":"hello"}
```

**Test from stdin:**
```bash
echo '{"op":"echo","text":"test"}' | agent-cli
```

### Agent CLI Protocol

The `agent-cli` script implements a simple JSON protocol:

**Request format:**
```json
{
  "op": "command_name",
  "text": "command_argument"
}
```

**Response format (success):**
```json
{
  "ok": true,
  "result": "response_data"
}
```

**Response format (error):**
```json
{
  "ok": false,
  "error": "error_message"
}
```

**Supported Operations:**
- `echo` - Returns the provided text

### Extending agent-cli

To add new commands:

1. Find the agent-cli script in the app's Documents directory:
   ```bash
   cd ~/bin
   cat agent-cli
   ```

2. Add new cases to the script's case statement
3. For development, you can edit it directly on-device or modify the bundled version and rebuild

Example addition:
```bash
case "$OP" in
    "echo")
        # existing echo code...
        ;;
    "reverse")
        # Reverse the text
        REVERSED=$(echo "$TEXT" | rev)
        echo "{\"ok\":true,\"result\":\"$REVERSED\"}"
        ;;
    *)
        echo "{\"ok\":false,\"error\":\"Unknown operation: $OP\"}"
        ;;
esac
```

## Resetting the Session

If the shell crashes or becomes unresponsive:
- Tap the **Reset** button in the status bar
- This will terminate and restart the shell process

## Limitations & Future Work

### Current Limitations

1. **Basic Shell Only** - Currently spawns `/bin/sh` from iOS system
   - Not a full Linux userland (Alpine/iSH integration pending)
   - Limited command set (iOS-provided utilities only)

2. **Simple JSON Parsing** - Uses shell string manipulation
   - Replace with Python/jq for production use
   - Current approach is MVP-friendly but fragile

3. **No Persistent State** - Shell resets on each session
   - Working directory resets to app Documents
   - No command history between sessions

4. **Foreground Only** - Shell terminates when app backgrounds
   - iOS sandbox constraint
   - Cannot run as daemon

### Future Enhancements

- [ ] Integrate iSH Alpine Linux userland for full Unix environment
- [ ] Add Python runtime for better JSON handling and agent scripts
- [ ] Implement session persistence and command history
- [ ] Add file browser and editor integration
- [ ] Support multiple terminal tabs
- [ ] Add agent marketplace for downloadable tools

## Technical Notes

### PTY Implementation

The app uses standard Unix PTY (pseudo-terminal) APIs:
- `posix_openpt()` - Allocate master PTY
- `grantpt()` / `unlockpt()` - Configure slave access
- `posix_spawn()` - Launch shell with stdio redirected to PTY
- `read()` / `write()` - Bidirectional I/O with shell

### Shell Environment

The shell is spawned with:
- `PATH` including `~/bin` for agent-cli
- `HOME` set to app's Documents directory  
- `TERM=xterm-256color` for color support
- Interactive mode (`-i` flag)

### iOS Sandbox Constraints

The app respects iOS sandboxing:
- No jailbreak or entitlements needed
- Shell runs in app's container (~/Documents)
- No access to system directories outside sandbox
- Can only execute binaries from bundle or Documents

## References

This implementation draws from:

- [SwiftTerm](https://github.com/migueldeicaza/SwiftTerm) - Terminal emulator widget
- [SwiftTermApp](https://github.com/migueldeicaza/SwiftTermApp) - Example terminal app
- [iSH](https://github.com/ish-app/ish) - Linux shell on iOS (inspiration for future work)
- [a-shell](https://github.com/holzschu/a-shell) - Another iOS terminal reference

## License

This is experimental code created as part of the unified-framework project. See the main repository LICENSE file for details.

## Contributing

This is an experimental MVP. Contributions welcome:
- Better JSON parsing for agent-cli
- Additional agent commands
- UI improvements
- iSH/Alpine integration

Open issues or PRs in the main unified-framework repository.
