import SwiftUI
import FactorGoLCore

struct ContentView: View {
    @StateObject var viewModel = SimulationViewModel()

    var body: some View {
        VStack {
            HStack {
                VStack(alignment: .leading) {
                    TextField("Semiprime N", value: $viewModel.n, format: .number)
                        .textFieldStyle(.roundedBorder)
                    HStack {
                        Text("Grid Size:")
                        Slider(value: Binding(get: { Double(viewModel.gridSize) }, set: { viewModel.gridSize = Int($0) }), in: 64...512, step: 1)
                        Text("\(viewModel.gridSize)")
                    }
                    HStack {
                        Text("Max Gens:")
                        Slider(value: Binding(get: { Double(viewModel.maxGens) }, set: { viewModel.maxGens = Int($0) }), in: 100...5000, step: 100)
                        Text("\(viewModel.maxGens)")
                    }
                    HStack {
                        Text("Chaos Threshold:")
                        Slider(value: $viewModel.chaosThreshold, in: 0.1...0.5, step: 0.1)
                        Text(String(format: "%.1f", viewModel.chaosThreshold))
                    }
                    HStack {
                        Text("Encoding:")
                        Picker("", selection: $viewModel.encodingStrategy) {
                            Text("Binary Fractal").tag(0)
                            Text("Residue Waves").tag(1)
                            Text("Dimensional Seeds").tag(2)
                        }
                        .pickerStyle(.segmented)
                    }
                }
                VStack {
                    Button(viewModel.isRunning ? "Stop" : "Start") {
                        if viewModel.isRunning {
                            viewModel.stopSimulation()
                        } else {
                            viewModel.startSimulation()
                        }
                    }
                    Button("Reset") {
                        viewModel.reset()
                    }
                }
            }
            .padding()

            // GoL grid view
            GoLMetalView(viewModel: viewModel)
                .frame(height: 400)

            HStack {
                VStack(alignment: .leading) {
                    Text("Generation: \(viewModel.generation)")
                    Text("Population: \(viewModel.population)")
                    Text("Entropy: \(String(format: "%.3f", viewModel.entropy))")
                    Text("Signals: \(viewModel.signals.count)")
                }
                Spacer()
                VStack(alignment: .trailing) {
                    if !viewModel.signals.isEmpty {
                        let periods = viewModel.signals.compactMap { $0.period }.map { String($0) }
                        if !periods.isEmpty {
                            Text("Detected Periods: \(periods.joined(separator: ", "))")
                        } else {
                            Text("Signals detected (periods pending)")
                        }
                    } else {
                        Text("No signals detected")
                    }
                }
            }
            .padding()
        }
        .frame(width: 800, height: 600)
    }
}