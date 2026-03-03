import SwiftUI
import UniformTypeIdentifiers

struct DocsConfigView: View {
    @ObservedObject var state: AppState
    let scriptRunner: ScriptRunner
    @State private var logOutput: String = ""
    @State private var isRunning: Bool = false

    private var repoURL: URL? {
        guard !state.repoPath.isEmpty else { return nil }
        return URL(fileURLWithPath: (state.repoPath as NSString).expandingTildeInPath)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Docs & config")
                .font(.title2)
                .foregroundColor(PhoenixColors.phoenixBlue)
            if let url = repoURL {
                Group {
                    docLink("DOCS_INDEX", "docs/DOCS_INDEX.md")
                    docLink("Branch protection", "docs/BRANCH_PROTECTION_REQUIREMENTS.md")
                    docLink("Observability spec", "docs/PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md")
                    docLink("Marketing prompts", "docs/MARKETING_DEEP_RESEARCH_PROMPTS.md")
                }
            }
            Button("Run check_docs_governance") {
                runDocsCheck()
            }
            .disabled(state.repoPath.isEmpty || isRunning)
            if isRunning {
                Button("Cancel") { scriptRunner.cancel() }
            }
            LiveLogView(logText: $logOutput, isRunning: isRunning)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixBackground)
    }

    private func docLink(_ label: String, _ path: String) -> some View {
        guard let base = repoURL else { return AnyView(EmptyView()) }
        let fileURL = base.appendingPathComponent(path)
        return AnyView(
            Link(label, destination: fileURL)
                .padding(2)
        )
    }

    private func runDocsCheck() {
        guard !state.repoPath.isEmpty else { return }
        logOutput = ""
        isRunning = true
        Task {
            do {
                _ = try await scriptRunner.run(
                    repoPath: state.repoPath,
                    scriptPath: "scripts/ci/check_docs_governance.py",
                    arguments: [],
                    timeoutSeconds: 120,
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
