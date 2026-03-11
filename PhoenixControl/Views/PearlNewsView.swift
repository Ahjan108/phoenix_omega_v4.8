import SwiftUI
import AppKit

/// Pearl News Board: hard blockers at top, GO/NO-GO, secrets status, workflow health, rollback proof, actions.
/// Authority: docs/CONTROL_PLANE_SPEC_PATCH_V1.1.md §5, EXECUTIVE_DASHBOARD_AND_PHOENIXCONTROL_SPEC
struct PearlNewsView: View {
    @ObservedObject var state: AppState
    let artifactReader: ArtifactReader
    let scriptRunner: ScriptRunner
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
        .onChange(of: state.refreshTrigger) { _ in refresh() }
        .onChange(of: state.repoPath) { _ in refresh() }
    }

    private var hardBlockersSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Hard blockers")
                .font(.headline)
                .foregroundColor(.red)
            if let info = boardInfo {
                if !info.checklistExists {
                    blockerRow("GO/NO-GO checklist missing", fix: "Create or restore docs/PEARL_NEWS_GO_NO_GO_CHECKLIST.md")
                }
                if !info.evidenceExists {
                    blockerRow("Networked run evidence missing", fix: "Run pipeline and record evidence to artifacts/pearl_news/evaluation/networked_run_evidence.json")
                }
                if info.checklistExists && info.evidenceExists {
                    Text("No hard blockers — checklist and evidence present.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            } else {
                Text("Set repo path and refresh.")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.red.opacity(0.08))
        .cornerRadius(8)
    }

    private func blockerRow(_ label: String, fix: String) -> some View {
        HStack(alignment: .top, spacing: 8) {
            StatusBadge(status: "fail")
            VStack(alignment: .leading, spacing: 2) {
                Text(label).font(.subheadline)
                Text("Fix: \(fix)").font(.caption2).foregroundColor(.secondary)
            }
        }
    }

    private var goNoGoSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("GO/NO-GO checklist")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            if let info = boardInfo {
                HStack(spacing: 12) {
                    StatusBadge(status: info.checklistExists ? "pass" : "fail")
                    Text(info.checklistExists ? "Checklist present" : "Checklist missing")
                    Button("Open checklist") { openPath(info.checklistPath) }
                        .buttonStyle(.borderless)
                }
                .font(.subheadline)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private var secretsAndWorkflowSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Secrets & workflow health")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            HStack(alignment: .top, spacing: 16) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Secrets readiness")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text("WP creds: set in Keychain / env per runbook.")
                        .font(.caption)
                }
                if let info = boardInfo {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Networked run evidence")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text(info.evidenceExists ? "Present" : "Missing")
                            .font(.caption)
                            .foregroundColor(info.evidenceExists ? .green : .red)
                    }
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Rollback proof")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text("Document in checklist (step 7).")
                            .font(.caption)
                    }
                }
            }
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
                if boardInfo?.draftsDirExists == true {
                    Button("Open drafts folder") { openPath("artifacts/pearl_news/drafts") }
                        .buttonStyle(.borderless)
                }
                Button("Open checklist doc") {
                    if let info = boardInfo { openPath(info.checklistPath) }
                }
                .buttonStyle(.borderless)
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
        guard !state.repoPath.isEmpty else { boardInfo = nil; return }
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
