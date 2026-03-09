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
                .keyboardShortcut(.return, modifiers: .command)
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
            if let phase = state.observabilityPhaseStatus {
                HStack(spacing: 12) {
                    Text("P1: \(phase.p1Observe.rawValue)")
                    Text("P2: \(phase.p2Document.rawValue)")
                    Text("P3: \(phase.p3ElevateFix.rawValue)")
                    Text("P4: \(phase.p4LearnEnhance.rawValue)")
                }
                .font(.caption)
                .foregroundColor(.secondary)
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
            LiveLogView(logText: $logOutput, isRunning: isRunning, exitCode: lastExitCode)
            Divider()
            evidenceTable
            Divider()
            elevatedTable
        }
        .padding()
        .background(PhoenixColors.phoenixBackground)
        .onAppear { refresh() }
        .onChange(of: state.refreshTrigger) { _ in refresh() }
    }

    private var identifiableEvidence: [IdentifiableEvidenceRow] {
        Array(state.evidenceLogRows.prefix(100).enumerated().map { IdentifiableEvidenceRow(id: $0.offset, row: $0.element) })
    }

    private var identifiableElevated: [IdentifiableEvidenceRow] {
        Array(state.elevatedFailures.enumerated().map { IdentifiableEvidenceRow(id: $0.offset, row: $0.element) })
    }

    private var evidenceTable: some View {
        EvidenceLogTable(title: "Evidence log (last 100)", rows: identifiableEvidence, highlightFailure: false)
    }

    private var elevatedTable: some View {
        EvidenceLogTable(title: "Elevated failures", rows: identifiableElevated, highlightFailure: true)
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
                    state.errorMessage = String(describing: error)
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
        state.observabilityPhaseStatus = artifactReader.loadObservabilityPhaseStatus(repoPath: state.repoPath)
    }
}
