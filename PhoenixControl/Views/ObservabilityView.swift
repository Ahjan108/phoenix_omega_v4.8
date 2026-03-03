import SwiftUI

struct ObservabilityView: View {
    @ObservedObject var state: AppState
    let artifactReader: ArtifactReader
    let scriptRunner: ScriptRunner
    @State private var logOutput: String = ""
    @State private var isRunning: Bool = false
    @State private var lastExitCode: Int32?

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Button("Collect signals") {
                    runCollector()
                }
                .disabled(state.repoPath.isEmpty || isRunning)
                Button("Refresh") {
                    refresh()
                }
                .disabled(state.repoPath.isEmpty)
                if isRunning {
                    Button("Cancel") {
                        scriptRunner.cancel()
                    }
                }
            }
            if let snap = state.lastSnapshot {
                HStack(spacing: 12) {
                    StatusBadge(status: "pass")
                    Text("\(snap.passed)")
                    StatusBadge(status: "fail")
                    Text("\(snap.failed)")
                    StatusBadge(status: "skip")
                    Text("\(snap.skipped)")
                }
            }
            LiveLogView(logText: $logOutput, isRunning: isRunning)
            Divider()
            evidenceTable
            Divider()
            elevatedTable
        }
        .padding()
        .background(PhoenixColors.phoenixBackground)
        .onAppear { refresh() }
    }

    private var identifiableEvidence: [IdentifiableEvidenceRow] {
        Array(state.evidenceLogRows.prefix(100).enumerated().map { IdentifiableEvidenceRow(id: $0.offset, row: $0.element) })
    }

    private var identifiableElevated: [IdentifiableEvidenceRow] {
        Array(state.elevatedFailures.enumerated().map { IdentifiableEvidenceRow(id: $0.offset, row: $0.element) })
    }

    private var evidenceTable: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("Evidence log (last 100)")
                .font(.headline)
            Table(identifiableEvidence) {
                TableColumn("Time") { item in Text(item.row.timestamp ?? "-") }
                TableColumn("Signal") { item in Text(item.row.signal_id ?? "-") }
                TableColumn("Category") { item in Text(item.row.category ?? "-") }
                TableColumn("Status") { item in StatusBadge(status: item.row.status ?? "?") }
                TableColumn("Message") { item in Text(item.row.message ?? "-").lineLimit(1) }
            }
        }
    }

    private var elevatedTable: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("Elevated failures")
                .font(.headline)
                .foregroundColor(.red)
            Table(identifiableElevated) {
                TableColumn("Time") { item in Text(item.row.timestamp ?? "-") }
                TableColumn("Signal") { item in Text(item.row.signal_id ?? "-") }
                TableColumn("Status") { item in StatusBadge(status: item.row.status ?? "fail") }
                TableColumn("Message") { item in Text(item.row.message ?? "-").lineLimit(2) }
            }
        }
    }

    private func runCollector() {
        guard !state.repoPath.isEmpty else { return }
        logOutput = ""
        isRunning = true
        lastExitCode = nil
        Task {
            do {
                let code = try await scriptRunner.run(
                    repoPath: state.repoPath,
                    scriptPath: "scripts/observability/collect_signals.py",
                    arguments: ["--out", "artifacts/observability/signal_snapshot.json"],
                    timeoutSeconds: 600,
                    onOutput: { line in
                        logOutput += line + "\n"
                    }
                )
                await MainActor.run {
                    lastExitCode = code
                    isRunning = false
                    refresh()
                }
            } catch {
                await MainActor.run {
                    logOutput += "\nError: \(error)"
                    isRunning = false
                    refresh()
                }
            }
        }
    }

    private func refresh() {
        guard !state.repoPath.isEmpty else { return }
        state.lastSnapshot = artifactReader.loadLatestSnapshot(repoPath: state.repoPath)
        state.evidenceLogRows = artifactReader.loadEvidenceLog(repoPath: state.repoPath, limit: 100)
        state.elevatedFailures = artifactReader.loadElevatedFailures(repoPath: state.repoPath, limit: 200)
    }
}
