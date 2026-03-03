import SwiftUI

struct TestsView: View {
    @ObservedObject var state: AppState
    let scriptRunner: ScriptRunner
    @State private var logOutput: String = ""
    @State private var isRunning: Bool = false

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Button("Run core tests (pytest -m \"not slow\")") {
                runTests(args: ["-m", "not slow"])
            }
            .disabled(state.repoPath.isEmpty || isRunning)
            Button("Run atoms coverage") {
                runTests(args: ["tests/test_atoms_coverage_100_percent.py", "-v"])
            }
            .disabled(state.repoPath.isEmpty || isRunning)
            if isRunning {
                Button("Cancel") { scriptRunner.cancel() }
            }
            LiveLogView(logText: $logOutput, isRunning: isRunning)
        }
        .padding()
        .background(PhoenixColors.phoenixBackground)
    }

    private func runTests(args: [String]) {
        guard !state.repoPath.isEmpty else { return }
        logOutput = ""
        isRunning = true
        Task {
            do {
                _ = try await scriptRunner.run(
                    repoPath: state.repoPath,
                    scriptPath: ScriptRunner.pytestScriptPath,
                    arguments: args,
                    timeoutSeconds: 300,
                    onOutput: { logOutput += $0 + "\n" }
                )
                await MainActor.run { isRunning = false }
            } catch {
                await MainActor.run {
                    logOutput += "\nError: \(error)"
                    isRunning = false
                }
            }
        }
    }
}
