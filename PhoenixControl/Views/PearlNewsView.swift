import SwiftUI
import AppKit

/// Pearl News Board: hard blockers at top, GO/NO-GO, secrets, workflow health, rollback proof, actions.
/// Authority: docs/CONTROL_PLANE_SPEC_PATCH_V1.1.md §5, EXECUTIVE_DASHBOARD_AND_PHOENIXCONTROL_SPEC
struct PearlNewsView: View {
    @ObservedObject var state: AppState
    let artifactReader: ArtifactReader
    let scriptRunner: ScriptRunner
    /// When non-nil, called to check if WP creds are set (e.g. Keychain); show "Set" / "Not set".
    var wpCredsReady: (() -> Bool)?
    @State private var boardInfo: ArtifactReader.PearlNewsBoardInfo?
    @State private var logOutput: String = ""
    @State private var isRunning: Bool = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Pearl News Board")
                    .font(.title2)
                    .foregroundColor(PhoenixColors.phoenixBlue)
                hardBlockersSection
                goNoGoSection
                secretsAndWorkflowSection
                actionsSection
                LiveLogView(logText: $logOutput, isRunning: isRunning)
            }
            .padding()
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .background(PhoenixColors.phoenixBackground)
        .onAppear { refresh() }
        .onChange(of: state.refreshTrigger) { _, _ in refresh() }
        .onChange(of: state.repoPath) { _, _ in refresh() }
    }

    private var hardBlockersSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Hard blockers")
                .font(.headline)
                .foregroundColor(.red)
            let blockers = collectBlockers()
            if blockers.isEmpty {
                Text("None — OK to run pipeline.")
                    .font(.caption)
                    .foregroundColor(.secondary)
            } else {
                ForEach(Array(blockers.enumerated()), id: \.offset) { _, b in
                    HStack(alignment: .top, spacing: 6) {
                        StatusBadge(status: "fail")
                        Text(b).font(.caption)
                    }
                }
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.red.opacity(0.08))
        .cornerRadius(8)
    }

    private func collectBlockers() -> [String] {
        var out: [String] = []
        if let info = boardInfo {
            if !info.checklistExists {
                out.append("GO/NO-GO checklist missing: \(info.checklistPath)")
            }
            if !info.evidenceExists {
                out.append("Networked run evidence missing: \(info.evidencePath)")
            }
        }
        return out
    }

    private var goNoGoSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("GO/NO-GO checklist")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            if let info = boardInfo {
                HStack(spacing: 12) {
                    StatusBadge(status: info.checklistExists ? "pass" : "fail")
                    Text(info.checklistExists ? "Checklist present" : "Missing")
                        .font(.caption)
                    Button("Open checklist") { openPath(info.checklistPath) }
                        .buttonStyle(.borderless)
                        .font(.caption)
                }
                HStack(spacing: 12) {
                    StatusBadge(status: info.evidenceExists ? "pass" : "fail")
                    Text(info.evidenceExists ? "Networked run evidence present" : "Evidence missing")
                        .font(.caption)
                }
            } else {
                Text("Set repo path and refresh.")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private var secretsAndWorkflowSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Secrets & workflow")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            HStack(spacing: 16) {
                HStack(spacing: 6) {
                    StatusBadge(status: (wpCredsReady?() ?? false) ? "pass" : "skip")
                    Text("WP creds: \((wpCredsReady?() ?? false) ? "Set" : "Not set / N/A")")
                        .font(.caption)
                }
                HStack(spacing: 6) {
                    StatusBadge(status: (boardInfo?.draftsDirExists ?? false) ? "pass" : "skip")
                    Text("Drafts dir: \((boardInfo?.draftsDirExists ?? false) ? "Present" : "—")")
                        .font(.caption)
                }
            }
            Text("Rollback: Verify per GO/NO-GO checklist step 7.")
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private var actionsSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Actions")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            HStack(spacing: 12) {
                Button("Run article pipeline") { runPipeline() }
                    .disabled(state.repoPath.isEmpty || isRunning)
                Button("Open drafts folder") {
                    if let info = boardInfo, !state.repoPath.isEmpty {
                        openPath("artifacts/pearl_news/drafts")
                    }
                }
                .disabled(state.repoPath.isEmpty)
                if isRunning {
                    Button("Cancel") { scriptRunner.cancel() }
                }
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private func openPath(_ relativePath: String) {
        guard !state.repoPath.isEmpty else { return }
        let base = (state.repoPath as NSString).expandingTildeInPath
        let full = (base as NSString).appendingPathComponent(relativePath)
        let url = URL(fileURLWithPath: full)
        guard FileManager.default.fileExists(atPath: url.path) else { return }
        NSWorkspace.shared.open(url)
    }

    private func refresh() {
        guard !state.repoPath.isEmpty else { return }
        boardInfo = artifactReader.loadPearlNewsBoardInfo(repoPath: state.repoPath)
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
                await MainActor.run {
                    isRunning = false
                    refresh()
                }
            } catch {
                await MainActor.run {
                    logOutput += "\nError: \(error)"
                    isRunning = false
                }
            }
        }
    }
}
