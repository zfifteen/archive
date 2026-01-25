import SwiftUI

struct GoLMetalView: View {
    @ObservedObject var viewModel: SimulationViewModel

    var body: some View {
        if let grid = viewModel.currentGrid, viewModel.gridSize > 0 {
            Canvas { context, size in
                // Capture gridSize once to avoid inconsistencies from concurrent updates
                let gridSize = viewModel.gridSize
                let cellSize = min(size.width / CGFloat(gridSize), size.height / CGFloat(gridSize))
                let expectedSize = gridSize * gridSize
                
                // Bounds check: ensure grid size matches expected size
                guard grid.count == expectedSize else {
                    return
                }
                
                for y in 0..<gridSize {
                    for x in 0..<gridSize {
                        let idx = y * gridSize + x
                        let color: Color = grid[idx] == 1 ? .black : .white
                        let rect = CGRect(x: CGFloat(x) * cellSize, y: CGFloat(y) * cellSize, width: cellSize, height: cellSize)
                        context.fill(Path(rect), with: .color(color))
                    }
                }
            }
            .border(Color.gray)
        } else {
            Text("No grid to display")
                .font(.title)
        }
    }
}