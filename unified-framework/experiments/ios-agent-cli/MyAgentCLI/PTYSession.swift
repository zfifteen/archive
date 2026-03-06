import Foundation

/// PTYSession manages a pseudo-terminal (PTY) for spawning and communicating with a shell process.
/// This provides the low-level PTY infrastructure needed for terminal emulation.
class PTYSession {
    private(set) var masterFD: Int32 = -1
    private(set) var slaveFD: Int32 = -1
    private(set) var childPID: pid_t = -1
    
    var isRunning: Bool {
        return childPID > 0 && masterFD >= 0
    }
    
    /// Opens a new PTY master/slave pair
    func openPTY() throws {
        var master: Int32 = -1
        var slave: Int32 = -1
        
        // Open PTY master
        master = posix_openpt(O_RDWR | O_NOCTTY)
        guard master >= 0 else {
            throw PTYError.openFailed("posix_openpt failed")
        }
        
        // Grant access to slave
        guard grantpt(master) == 0 else {
            close(master)
            throw PTYError.openFailed("grantpt failed")
        }
        
        // Unlock slave
        guard unlockpt(master) == 0 else {
            close(master)
            throw PTYError.openFailed("unlockpt failed")
        }
        
        // Get slave path
        guard let slaveName = ptsname(master) else {
            close(master)
            throw PTYError.openFailed("ptsname failed")
        }
        
        // Open slave
        slave = open(slaveName, O_RDWR | O_NOCTTY)
        guard slave >= 0 else {
            close(master)
            throw PTYError.openFailed("open slave failed")
        }
        
        self.masterFD = master
        self.slaveFD = slave
    }
    
    /// Spawns a shell process attached to the PTY
    func spawnShell(shellPath: String = "/bin/sh", environment: [String: String] = [:]) throws {
        guard masterFD >= 0, slaveFD >= 0 else {
            throw PTYError.spawnFailed("PTY not opened")
        }
        
        // Prepare environment
        var env = ProcessInfo.processInfo.environment
        for (key, value) in environment {
            env[key] = value
        }
        let envArray = env.map { "\($0.key)=\($0.value)" }
        
        // Create C-style arrays for posix_spawn
        let cArgs: [UnsafeMutablePointer<CChar>?] = [
            strdup(shellPath),
            strdup("-i"), // Interactive shell
            nil
        ]
        
        let cEnv: [UnsafeMutablePointer<CChar>?] = envArray.map { strdup($0) } + [nil]
        
        defer {
            // Use free() for memory allocated with strdup()
            cArgs.forEach { if let ptr = $0 { free(ptr) } }
            cEnv.forEach { if let ptr = $0 { free(ptr) } }
        }
        
        // Set up file actions to redirect stdio to slave PTY
        var fileActions: posix_spawn_file_actions_t?
        posix_spawn_file_actions_init(&fileActions)
        posix_spawn_file_actions_adddup2(&fileActions, slaveFD, STDIN_FILENO)
        posix_spawn_file_actions_adddup2(&fileActions, slaveFD, STDOUT_FILENO)
        posix_spawn_file_actions_adddup2(&fileActions, slaveFD, STDERR_FILENO)
        posix_spawn_file_actions_addclose(&fileActions, masterFD)
        
        // Spawn the process
        var pid: pid_t = 0
        let result = posix_spawn(&pid, shellPath, &fileActions, nil, cArgs, cEnv)
        
        posix_spawn_file_actions_destroy(&fileActions)
        
        guard result == 0 else {
            throw PTYError.spawnFailed("posix_spawn failed with error: \(result)")
        }
        
        self.childPID = pid
        
        // Close slave FD in parent process
        close(slaveFD)
        slaveFD = -1
    }
    
    /// Reads data from the PTY master (output from the shell)
    func read(maxLength: Int = 4096) -> Data? {
        guard masterFD >= 0 else { return nil }
        
        var buffer = [UInt8](repeating: 0, count: maxLength)
        let bytesRead = Darwin.read(masterFD, &buffer, maxLength)
        
        guard bytesRead > 0 else { return nil }
        
        return Data(buffer.prefix(bytesRead))
    }
    
    /// Writes data to the PTY master (input to the shell)
    func write(_ data: Data) -> Bool {
        guard masterFD >= 0 else { return false }
        
        let result = data.withUnsafeBytes { ptr -> Int in
            Darwin.write(masterFD, ptr.baseAddress, data.count)
        }
        
        return result == data.count
    }
    
    /// Sets the window size for the PTY
    func setWindowSize(rows: UInt16, cols: UInt16) {
        guard masterFD >= 0 else { return }
        
        var size = winsize()
        size.ws_row = rows
        size.ws_col = cols
        ioctl(masterFD, TIOCSWINSZ, &size)
    }
    
    /// Terminates the shell process
    func terminate() {
        if childPID > 0 {
            kill(childPID, SIGTERM)
            
            // Wait for process to exit
            var status: Int32 = 0
            waitpid(childPID, &status, WNOHANG)
            
            childPID = -1
        }
        
        if masterFD >= 0 {
            close(masterFD)
            masterFD = -1
        }
        
        if slaveFD >= 0 {
            close(slaveFD)
            slaveFD = -1
        }
    }
    
    deinit {
        terminate()
    }
}

enum PTYError: Error, LocalizedError {
    case openFailed(String)
    case spawnFailed(String)
    
    var errorDescription: String? {
        switch self {
        case .openFailed(let msg):
            return "PTY open failed: \(msg)"
        case .spawnFailed(let msg):
            return "Shell spawn failed: \(msg)"
        }
    }
}
