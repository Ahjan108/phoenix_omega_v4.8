import SwiftUI

struct GatesReleaseView: View {
    @ObservedObject var state: AppState
    let scriptRunner: ScriptRunner
    @State private var logOutput: String = ""
    @State private var isRunning: Bool = false

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Button("Run production readiness gates") {
                runScript("scripts/run_production_readiness_gates.py", args: [])
            }
            .disabled(state.repoPath.isEmpty || isRunning)
            Button("Run prepublish gates") {
                runScript("scripts/ci/run_prepublish_gates.py", args: [])
            }
            .disabled(state.repoPath.isEmpty || isRunning)
            Button("Run rigorous system test") {
                runScript("scripts/ci/run_rigorous_system_test.py", args: [])
            }
            .disabled(state.repoPath.isEmpty || isRunning)
            Button("Run canary 100 books") {
                runScript("scripts/ci/run_canary_100_books.py", args: [])
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

    private func runScript(_ path: String, args: [String]) {
        guard !state.repoPath.isEmpty else { return }
        logOutput = ""
        isRunning = true
        Task {
            do {
                _ = try await scriptRunner.run(
                    repoPath: state.repoPath,
                    scriptPath: path,
                    arguments: args,
                    timeoutSeconds: 600,
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
