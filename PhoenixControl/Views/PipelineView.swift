import SwiftUI

struct PipelineView: View {
    @ObservedObject var state: AppState
    let scriptRunner: ScriptRunner
    @State private var topic: String = "anxiety"
    @State private var persona: String = "gen_alpha_students"
    @State private var logOutput: String = ""
    @State private var isRunning: Bool = false

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 8) {
                Text("Topic")
                TextField("topic", text: $topic)
                    .frame(width: 140)
                Text("Persona")
                TextField("persona", text: $persona)
                    .frame(width: 160)
            }
            HStack {
                Button("Run pipeline") {
                    runPipeline()
                }
                .disabled(state.repoPath.isEmpty || isRunning)
                if isRunning {
                    Button("Cancel") { scriptRunner.cancel() }
                }
            }
            LiveLogView(logText: $logOutput, isRunning: isRunning)
        }
        .padding()
        .background(PhoenixColors.phoenixBackground)
    }

    private func runPipeline() {
        guard !state.repoPath.isEmpty else { return }
        logOutput = ""
        isRunning = true
        Task {
            do {
                _ = try await scriptRunner.run(
                    repoPath: state.repoPath,
                    scriptPath: "scripts/run_pipeline.py",
                    arguments: ["--topic", topic, "--persona", persona, "--render-book"],
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
