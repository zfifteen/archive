import Foundation
import Combine

/// ShellSession manages the lifecycle of a shell process and coordinates between
/// the PTY and the terminal UI
class ShellSession: ObservableObject {
    @Published var isRunning = false
    @Published var statusMessage = "Not connected"
    @Published var pid: pid_t = 0
    
    private var ptySession: PTYSession?
    private var readTimer: Timer?
    
    var onDataReceived: ((Data) -> Void)?
    
    init() {}
    
    /// Starts a new shell session
    func start() {
        guard !isRunning else { return }
        
        do {
            let pty = PTYSession()
            try pty.openPTY()
            
            // Set up environment with agent-cli in path
            var environment: [String: String] = [:]
            
            // Get Documents directory for agent-cli script
            if let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first?.path {
                let binPath = documentsPath + "/bin"
                
                // Add to PATH
                if let existingPath = ProcessInfo.processInfo.environment["PATH"] {
                    environment["PATH"] = binPath + ":" + existingPath
                } else {
                    environment["PATH"] = binPath + ":/usr/bin:/bin"
                }
                
                environment["HOME"] = documentsPath
                environment["TERM"] = "xterm-256color"
            }
            
            try pty.spawnShell(environment: environment)
            
            self.ptySession = pty
            self.pid = pty.childPID
            self.isRunning = true
            self.statusMessage = "Shell running (PID: \(pty.childPID))"
            
            // Start reading from PTY
            startReading()
            
        } catch {
            statusMessage = "Error: \(error.localizedDescription)"
            isRunning = false
        }
    }
    
    /// Stops the shell session
    func stop() {
        readTimer?.invalidate()
        readTimer = nil
        
        ptySession?.terminate()
        ptySession = nil
        
        isRunning = false
        pid = 0
        statusMessage = "Disconnected"
    }
    
    /// Sends input to the shell
    func sendInput(_ text: String) {
        guard let data = text.data(using: .utf8) else { return }
        _ = ptySession?.write(data)
    }
    
    /// Sets the terminal window size
    func setWindowSize(rows: Int, cols: Int) {
        ptySession?.setWindowSize(rows: UInt16(rows), cols: UInt16(cols))
    }
    
    /// Starts a timer to continuously read from the PTY
    private func startReading() {
        // Use 100ms interval (10Hz) to balance responsiveness and CPU usage
        readTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
            self?.readFromPTY()
        }
    }
    
    /// Reads available data from the PTY
    private func readFromPTY() {
        guard let data = ptySession?.read() else { return }
        
        DispatchQueue.main.async {
            self.onDataReceived?(data)
        }
    }
    
    deinit {
        stop()
    }
}
