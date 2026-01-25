// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "FactorGoL",
    platforms: [.macOS(.v14)],
    targets: [
        .target(
            name: "FactorGoLCore",
            dependencies: [],
            path: "Sources",
            exclude: ["FactorGoLCLI", "FactorGoLApp"]
        ),
        .executableTarget(
            name: "FactorGoLCLI",
            dependencies: ["FactorGoLCore"],
            path: "Sources/FactorGoLCLI"
        ),
        .executableTarget(
            name: "FactorGoLApp",
            dependencies: ["FactorGoLCore"],
            path: "Sources/FactorGoLApp"
        )
    ]
)