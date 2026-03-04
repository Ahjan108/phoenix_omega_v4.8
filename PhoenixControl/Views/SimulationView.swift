import SwiftUI

struct SimulationView: View {
    @ObservedObject var state: AppState
    let scriptRunner: ScriptRunner
    @State private var logOutput: String = ""
    @State private var isRunning: Bool = false

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Button("Run simulation 10k (CI preset)") {
                runScript("scripts/ci/run_simulation_10k.py", args: [])
            }
            .disabled(state.repoPath.isEmpty || isRunning)
            Button("Analyze Pearl Prime sim") {
                runScript("scripts/ci/analyze_pearl_prime_sim.py", args: [])
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
