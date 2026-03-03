import SwiftUI

struct PearlNewsView: View {
    @ObservedObject var state: AppState
    let scriptRunner: ScriptRunner
    @State private var logOutput: String = ""
    @State private var isRunning: Bool = false

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Button("Run article pipeline") {
                runPipeline()
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

    private func runPipeline() {
        guard !state.repoPath.isEmpty else { return }
        logOutput = ""
        isRunning = true
        Task {
            do {
                _ = try await scriptRunner.run(
                    repoPath: state.repoPath,
                    scriptPath: "pearl_news/pipeline/run_article_pipeline.py",
                    arguments: ["--feeds", "pearl_news/config/feeds.yaml", "--out-dir", "artifacts/pearl_news/drafts"],
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
