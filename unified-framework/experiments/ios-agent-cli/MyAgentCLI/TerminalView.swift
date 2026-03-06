import SwiftUI
import SwiftTerm

/// TerminalView wraps the SwiftTerm terminal widget for use in SwiftUI
struct TerminalView: UIViewRepresentable {
    let shellSession: ShellSession
    
    func makeUIView(context: Context) -> TerminalViewWrapper {
        let wrapper = TerminalViewWrapper()
        
        // Set up data flow from shell to terminal
        shellSession.onDataReceived = { data in
            wrapper.feed(data: data)
        }
        
        // Set up data flow from terminal to shell
        wrapper.onInput = { text in
            shellSession.sendInput(text)
        }
        
        // Set up window size updates
        wrapper.onSizeChanged = { cols, rows in
            shellSession.setWindowSize(rows: rows, cols: cols)
        }
        
        return wrapper
    }
    
    func updateUIView(_ uiView: TerminalViewWrapper, context: Context) {
        // Updates handled by observation
    }
}

/// Wrapper class that manages the TerminalView from SwiftTerm
class TerminalViewWrapper: UIView {
    private let terminalView: LocalProcessTerminalView
    
    var onInput: ((String) -> Void)?
    var onSizeChanged: ((Int, Int) -> Void)?
    
    override init(frame: CGRect) {
        terminalView = LocalProcessTerminalView(frame: frame)
        super.init(frame: frame)
        
        addSubview(terminalView)
        terminalView.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            terminalView.leadingAnchor.constraint(equalTo: leadingAnchor),
            terminalView.trailingAnchor.constraint(equalTo: trailingAnchor),
            terminalView.topAnchor.constraint(equalTo: topAnchor),
            terminalView.bottomAnchor.constraint(equalTo: bottomAnchor)
        ])
        
        // Configure terminal
        terminalView.terminal.softWrap = false
        
        // Set up terminal delegate
        terminalView.terminalDelegate = self
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    override func layoutSubviews() {
        super.layoutSubviews()
        
        // Notify size changes
        let cols = terminalView.terminal.cols
        let rows = terminalView.terminal.rows
        onSizeChanged?(cols, rows)
    }
    
    func feed(data: Data) {
        terminalView.feed(byteArray: [UInt8](data))
    }
}

extension TerminalViewWrapper: LocalProcessTerminalViewDelegate {
    func sizeChanged(source: LocalProcessTerminalView, newCols: Int, newRows: Int) {
        onSizeChanged?(newCols, newRows)
    }
    
    func setTerminalTitle(source: LocalProcessTerminalView, title: String) {
        // Title updates can be ignored for MVP
    }
    
    func hostCurrentDirectoryUpdate(source: TerminalView, directory: String?) {
        // Directory updates can be ignored for MVP
    }
    
    func send(source: LocalProcessTerminalView, data: ArraySlice<UInt8>) {
        let text = String(bytes: data, encoding: .utf8) ?? ""
        onInput?(text)
    }
}
