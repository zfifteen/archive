import SwiftUI

/// TerminalScreen is the main view that displays the terminal and status bar
struct TerminalScreen: View {
    @StateObject private var shellSession = ShellSession()
    @State private var showAlert = false
    @State private var alertMessage = ""
    
    var body: some View {
        VStack(spacing: 0) {
            // Status bar
            HStack {
                Text(shellSession.statusMessage)
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Spacer()
                
                if shellSession.isRunning {
                    Button("Reset") {
                        resetSession()
                    }
                    .font(.caption)
                    .buttonStyle(.bordered)
                    .controlSize(.small)
                } else {
                    Button("Connect") {
                        connectSession()
                    }
                    .font(.caption)
                    .buttonStyle(.bordered)
                    .controlSize(.small)
                }
            }
            .padding(8)
            .background(Color(UIColor.systemGray6))
            
            // Terminal view
            if shellSession.isRunning {
                TerminalView(shellSession: shellSession)
                    .background(Color.black)
            } else {
                VStack {
                    Spacer()
                    Text("Terminal Disconnected")
                        .foregroundColor(.secondary)
                    Text("Press Connect to start a shell session")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .padding(.top, 4)
                    Spacer()
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(Color.black)
            }
        }
        .onAppear {
            setupAgentCLI()
            connectSession()
        }
        .alert("Setup Required", isPresented: $showAlert) {
            Button("OK") { }
        } message: {
            Text(alertMessage)
        }
    }
    
    private func connectSession() {
        shellSession.start()
    }
    
    private func resetSession() {
        shellSession.stop()
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            shellSession.start()
        }
    }
    
    /// Copies the agent-cli script to the Documents directory on first launch
    private func setupAgentCLI() {
        guard let documentsURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first else {
            return
        }
        
        let binURL = documentsURL.appendingPathComponent("bin")
        let agentCliURL = binURL.appendingPathComponent("agent-cli")
        
        // Create bin directory if needed
        try? FileManager.default.createDirectory(at: binURL, withIntermediateDirectories: true)
        
        // Copy agent-cli from bundle if not already present
        if !FileManager.default.fileExists(atPath: agentCliURL.path) {
            guard let bundleURL = Bundle.main.url(forResource: "agent-cli", withExtension: nil, subdirectory: "Resources") else {
                alertMessage = "agent-cli script not found in bundle"
                showAlert = true
                return
            }
            
            do {
                try FileManager.default.copyItem(at: bundleURL, to: agentCliURL)
                
                // Make executable
                let attributes = [FileAttributeKey.posixPermissions: 0o755]
                try FileManager.default.setAttributes(attributes, ofItemAtPath: agentCliURL.path)
            } catch {
                alertMessage = "Failed to setup agent-cli: \(error.localizedDescription)"
                showAlert = true
            }
        }
    }
}

struct TerminalScreen_Previews: PreviewProvider {
    static var previews: some View {
        TerminalScreen()
    }
}
