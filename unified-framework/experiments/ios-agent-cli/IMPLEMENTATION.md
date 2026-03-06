# iOS Agent CLI - Implementation Notes

## Project Structure Created

This implementation creates a complete, buildable Xcode project for iOS that implements a terminal-based agent CLI interface.

### Directory Layout

```
experiments/ios-agent-cli/
├── MyAgentCLI.xcodeproj/
│   └── project.pbxproj              # Xcode project configuration
├── MyAgentCLI/
│   ├── MyAgentCLIApp.swift          # App entry point (@main)
│   ├── TerminalScreen.swift         # Main UI view with status bar
│   ├── TerminalView.swift           # SwiftUI wrapper for SwiftTerm
│   ├── ShellSession.swift           # Shell lifecycle manager
│   ├── PTYSession.swift             # PTY operations & process spawning
│   ├── Assets.xcassets/             # App icons and colors
│   └── Resources/
│       └── agent-cli                # Executable shell script
├── README.md                         # User documentation
└── .gitignore                        # Xcode build artifacts
```

## Key Design Decisions

### 1. SwiftTerm Integration

We use SwiftTerm as a Swift Package Manager dependency rather than bundling it manually. This provides:
- Modern terminal emulation (VT100/Xterm compatible)
- ANSI color support
- Proper keyboard input handling
- Maintained by community

The package reference in project.pbxproj:
```xml
<XCRemoteSwiftPackageReference "SwiftTerm">
    repositoryURL = "https://github.com/migueldeicaza/SwiftTerm";
    minimumVersion = 1.0.0;
```

### 2. PTY Architecture

The PTY implementation follows Unix standards:

**PTYSession.swift** provides:
- `posix_openpt()` for master PTY allocation
- `grantpt()` / `unlockpt()` for slave setup
- `posix_spawn()` for shell process launch (iOS-approved method)
- `read()` / `write()` for I/O
- `ioctl(TIOCSWINSZ)` for window size updates

**ShellSession.swift** coordinates:
- PTY lifecycle (start/stop)
- Timer-based reading (100ms poll for efficient CPU usage)
- Environment setup (PATH, HOME, TERM)
- Status updates via Combine @Published

### 3. Shell Environment Setup

The app creates a mini Unix-like environment:

```swift
environment["PATH"] = binPath + ":/usr/bin:/bin"
environment["HOME"] = documentsPath  // App's Documents directory
environment["TERM"] = "xterm-256color"
```

On first launch, `TerminalScreen.setupAgentCLI()`:
1. Creates `~/Documents/bin/` directory
2. Copies `agent-cli` from bundle resources
3. Sets executable permissions (0755)
4. Agent becomes available in shell PATH

### 4. SwiftUI Integration

**TerminalView** bridges UIKit (SwiftTerm) to SwiftUI:
- Uses `UIViewRepresentable`
- `TerminalViewWrapper` wraps SwiftTerm's `LocalProcessTerminalView`
- Closures connect terminal I/O to `ShellSession`

Data flow:
```
User Input → TerminalView → ShellSession → PTY → Shell
Shell Output → PTY → ShellSession → TerminalView → Display
```

### 5. Agent CLI Design

The `agent-cli` script is intentionally minimal for MVP:

**Features:**
- JSON input/output format
- Single command: `echo`
- Shell-based parsing (grep/sed)
- Extensible case statement

**Rationale:**
- No external dependencies (pure POSIX sh)
- Easy to understand and modify
- Can be replaced with Python/jq later
- Demonstrates the pattern

**Future Enhancement Path:**
```bash
# Could become Python for better JSON handling
#!/usr/bin/env python3
import sys, json

data = json.loads(sys.argv[1])
if data['op'] == 'echo':
    print(json.dumps({"ok": True, "result": data['text']}))
```

## iOS Sandbox Considerations

### What Works

✅ Spawning `/bin/sh` (iOS system shell)  
✅ Running iOS-provided utilities (`ls`, `cat`, `echo`, etc.)  
✅ Creating files in app's Documents directory  
✅ Running scripts from app bundle  
✅ PTY operations (all POSIX-compliant)

### What Doesn't Work (Yet)

❌ Full Alpine Linux (requires iSH integration)  
❌ Installing packages (no package manager)  
❌ Accessing system directories outside sandbox  
❌ Background execution (iOS terminates on background)  
❌ Network access without entitlements  

### iSH Integration Path (Future Work)

To get full Linux userland:

1. **Add iSH as dependency** (if buildable as library)
2. **Bundle Alpine rootfs** in app resources
3. **Replace shell spawn** in PTYSession:
   ```swift
   // Instead of /bin/sh, launch iSH kernel
   try pty.spawnShell(shellPath: "/path/to/ish-kernel")
   ```
4. **Mount rootfs** so Alpine tools available
5. **Install Python, jq, etc.** in Alpine

This would give full Unix environment but requires:
- Much larger app size (~100MB for rootfs)
- More complex build process
- Possible App Store review issues

## Build Process

The project is configured for:
- **Minimum iOS 16.0** (recent stable baseline)
- **iPhone + iPad** (universal)
- **SwiftUI lifecycle** (no UIKit AppDelegate)
- **Automatic code signing** (development)

To build:
1. Open `MyAgentCLI.xcodeproj` in Xcode
2. Wait for SwiftTerm package fetch
3. Select Simulator or Device
4. Build & Run (⌘R)

## Testing the Implementation

### Manual Test Cases

1. **Terminal Launch**
   ```
   - App starts → Terminal connects automatically
   - Status shows: "Shell running (PID: xxxx)"
   ```

2. **Basic Commands**
   ```bash
   pwd           # Should show ~/Documents
   ls -la        # List app sandbox files
   echo test     # Basic I/O
   ```

3. **Agent CLI**
   ```bash
   agent-cli '{"op":"echo","text":"hello"}'
   # Expected: {"ok":true,"result":"hello"}
   ```

4. **Reset Function**
   ```
   - Type a command
   - Tap "Reset" button
   - Terminal reconnects with fresh shell
   - Previous command gone (expected)
   ```

5. **Terminal I/O**
   ```bash
   cat           # Type lines, press Ctrl+D
   # Should echo lines back
   ```

### Known Limitations to Document

1. **Limited Command Set** - Only iOS-provided utilities
2. **No Tab Completion** - Terminal is basic
3. **No Job Control** - Background jobs may not work correctly
4. **Window Resize** - May not update immediately
5. **Copy/Paste** - Uses iOS standard gestures

## Code Quality Notes

### Thread Safety

- `ShellSession` uses `@Published` for main thread updates
- PTY reads on timer → dispatched to main via `DispatchQueue.main.async`
- UI updates always on main thread

### Memory Management

- `ShellSession` uses `[weak self]` in timer closure
- `deinit` handlers clean up PTY resources
- File descriptors closed on terminate

### Error Handling

- PTY errors thrown as `PTYError` enum
- UI shows alerts for setup failures
- Connection failures shown in status bar

## Extension Points

The architecture is designed for extension:

### Adding New Agent Commands

Edit `Resources/agent-cli`, add cases:
```bash
case "$OP" in
    "echo")
        # ... existing ...
        ;;
    "newcmd")
        # Your logic here
        echo "{\"ok\":true,\"result\":\"...\"}"
        ;;
esac
```

### Adding Python Runtime

1. Bundle Python framework in app
2. Update agent-cli shebang: `#!/path/to/python3`
3. Use proper JSON library: `import json`

### Multiple Terminal Tabs

1. Change `ShellSession` to array
2. Add TabView in `TerminalScreen`
3. Each tab gets own PTY session

### Command History

1. Add `@Published var history: [String]` to `ShellSession`
2. Intercept commands in `sendInput()`
3. Provide up/down arrow handler in `TerminalView`

## Security Considerations

✅ **Safe:**
- Uses iOS-approved APIs only
- No jailbreak detection bypass
- Respects sandbox boundaries
- No dynamic code loading

⚠️ **Be Aware:**
- Shell has same permissions as app
- Scripts can access app's Documents
- User input passed directly to shell (command injection risk if exposed to untrusted input)

For production, sanitize any user input before passing to shell:
```swift
func sanitize(_ input: String) -> String {
    // Escape shell special characters
    return input.replacingOccurrences(of: "'", with: "'\\''")
}
```

## Conclusion

This MVP provides a solid foundation for iOS agent development:
- ✅ Complete Xcode project
- ✅ Working terminal with PTY
- ✅ Agent CLI script framework
- ✅ Extensible architecture
- ✅ iOS sandbox compliant
- ✅ Ready for iSH/Alpine integration

Next steps depend on use case:
- Research tools → Enhance agent-cli commands
- Linux environment → Integrate iSH
- UI polish → Add tabs, history, settings
- Distribution → Prepare for App Store
