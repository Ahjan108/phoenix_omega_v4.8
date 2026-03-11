import SwiftUI
import AppKit

struct DashboardView: View {
    @ObservedObject var state: AppState
    let artifactReader: ArtifactReader
    let scriptRunner: ScriptRunner
    var onSelectObservability: (() -> Void)? = nil
    var onGovernanceRan: (() -> Void)? = nil

    @State private var governanceReport: SystemGovernanceReport?
    @State private var freebiesInfo: ArtifactReader.FreebiesIndexInfo?
    @State private var governanceLogOutput: String = ""
    @State private var governanceRunningScript: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                if state.repoPath.isEmpty {
                    Text("Set repo path in Settings (or toolbar) to see status.")
                        .foregroundColor(.secondary)
                        .padding()
                } else {
                    safetyKillSwitchCard
                    governanceBlockersCard
                    freebiesIndexHealthCard
                    evidenceLinksSection
                    observabilityPhaseCard
                    observabilityCard
                    evidenceCard
                    elevatedCard
                    missingBlockedSection
                    branchProtectionCard
                }
            }
            .padding()
        }
        .background(PhoenixColors.phoenixBackground)
        .onAppear { refresh() }
        .onChange(of: state.refreshTrigger) { _ in refresh() }
    }

    // MARK: - Governance blockers (spec: 3 blockers + next-action + one-click verify)
    private var governanceBlockersCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Governance blockers")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            HStack(alignment: .top, spacing: 8) {
                VStack(alignment: .leading, spacing: 8) {
                    blockerRow(name: "DOCS_INDEX link integrity", slug: "docs_governance", fixCommand: "python3 scripts/ci/check_docs_governance.py")
                    blockerRow(name: "Gate 17 (jsonschema runtime)", slug: "production_gates", fixCommand: "python3 scripts/run_production_readiness_gates.py")
                    blockerRow(name: "Gate 16b (CTA caps)", slug: "production_gates", fixCommand: "python3 scripts/run_production_readiness_gates.py")
                }
                Spacer()
                VStack(alignment: .leading, spacing: 6) {
                    Text("One-click verify").font(.caption).foregroundColor(.secondary)
                    Button("Check docs governance") { runVerifyScript("scripts/ci/check_docs_governance.py", args: ["--check-inventory"]) }
                        .buttonStyle(.borderless)
                        .disabled(governanceRunningScript != nil)
                    Button("Run production gates") { runVerifyScript("scripts/run_production_readiness_gates.py", args: []) }
                        .buttonStyle(.borderless)
                        .disabled(governanceRunningScript != nil)
                    Button("Check system governance") { runVerifyScript("scripts/ci/check_system_governance_status.py", args: []) }
                        .buttonStyle(.borderless)
                        .disabled(governanceRunningScript != nil)
                }
            }
            if governanceRunningScript != nil {
                Text("Running… \(governanceRunningScript ?? "")")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private func blockerRow(name: String, slug: String, fixCommand: String) -> some View {
        let passed = governanceReport?.checks?.first(where: { ($0.slug ?? "") == slug })?.passed ?? nil
        let isPass = passed == true
        return VStack(alignment: .leading, spacing: 2) {
            HStack(spacing: 6) {
                StatusBadge(status: isPass ? "pass" : "fail")
                Text(name).font(.subheadline)
            }
            if passed == false {
                Text("Fix: \(fixCommand)")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
    }

    private func runVerifyScript(_ script: String, args: [String]) {
        governanceRunningScript = script
        governanceLogOutput = ""
        Task {
            do {
                _ = try await scriptRunner.run(
                    repoPath: state.repoPath,
                    scriptPath: script,
                    arguments: args,
                    timeoutSeconds: 180,
                    onOutput: { governanceLogOutput += $0 + "\n" }
                )
                await MainActor.run {
                    governanceRunningScript = nil
                    refresh()
                    onGovernanceRan?()
                }
            } catch {
                await MainActor.run {
                    governanceLogOutput += "\nError: \(error)"
                    governanceRunningScript = nil
                }
            }
        }
    }

    private var freebiesIndexHealthCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Freebies index health")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            if let info = freebiesInfo {
                HStack(alignment: .top, spacing: 12) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Index: \(info.path)").font(.caption)
                        Text("Rows: \(info.rowCount)").font(.caption)
                        if let date = info.lastModified {
                            Text("Last rebuild: \(date, formatter: Self.dateFormatter)").font(.caption)
                        } else {
                            Text("Last rebuild: —").font(.caption)
                        }
                    }
                    Text(info.exists ? "Present" : "Missing")
                        .font(.caption)
                        .foregroundColor(info.exists ? .green : .red)
                }
                Text("Gate 16/16b: Run production gates for result.")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            } else {
                Text("Load repo to see freebies index.")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }
    private static let dateFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateStyle = .short
        f.timeStyle = .short
        return f
    }()

    private var evidenceLinksSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Evidence links")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            HStack(spacing: 12) {
                evidenceLink("system_governance_report.json", path: "artifacts/governance/system_governance_report.json")
                evidenceLink("freebies index", path: "artifacts/freebies/index.jsonl")
                evidenceLink("DOCS_INDEX.md", path: "docs/DOCS_INDEX.md")
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private func evidenceLink(_ label: String, path: String) -> some View {
        Button(action: { openEvidenceFile(path) }) {
            Text(label).font(.caption)
        }
        .buttonStyle(.borderless)
    }

    private func openEvidenceFile(_ relativePath: String) {
        guard !state.repoPath.isEmpty else { return }
        let base = (state.repoPath as NSString).expandingTildeInPath
        let full = (base as NSString).appendingPathComponent(relativePath)
        let url = URL(fileURLWithPath: full)
        guard FileManager.default.fileExists(atPath: url.path) else { return }
        NSWorkspace.shared.open(url)
    }

    @AppStorage("autonomyEnabled") private var autonomyEnabled = false
    @State private var killSwitchAuditLog: [String] = []

    private var safetyKillSwitchCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text("Safety Kill Switch (Autonomy)")
                    .font(.headline)
                    .foregroundColor(PhoenixColors.phoenixBlue)
                Spacer()
                Text(autonomyEnabled ? "ON" : "OFF")
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .foregroundColor(autonomyEnabled ? .green : .red)
                Toggle("", isOn: $autonomyEnabled)
                    .toggleStyle(.switch)
                    .labelsHidden()
                    .onChange(of: autonomyEnabled) { newValue in
                        let entry = "\(ISO8601DateFormatter().string(from: Date())) — \(newValue ? "ON" : "OFF") — toggled from UI"
                        killSwitchAuditLog.append(entry)
                        if killSwitchAuditLog.count > 50 { killSwitchAuditLog.removeFirst() }
                    }
            }
            Text("When OFF, no autonomous loop activity. State changes are logged.")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private var missingBlockedSection: some View {
        Group {
            let items = missingBlockedItems()
            if !items.isEmpty {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Missing / blocked")
                        .font(.headline)
                        .foregroundColor(.orange)
                    ForEach(Array(items.prefix(10).enumerated()), id: \.offset) { _, item in
                        HStack(alignment: .top, spacing: 6) {
                            StatusBadge(status: item.severity == "blocker" ? "fail" : "skip")
                            VStack(alignment: .leading, spacing: 2) {
                                Text(item.source).font(.caption)
                                if !item.fixCommand.isEmpty {
                                    Text("Fix: \(item.fixCommand)").font(.caption2).foregroundColor(.secondary)
                                }
                            }
                        }
                    }
                }
                .padding()
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.orange.opacity(0.08))
                .cornerRadius(8)
            }
        }
    }

    private struct BlockedItem {
        let severity: String
        let source: String
        let fixCommand: String
    }
    private func missingBlockedItems() -> [BlockedItem] {
        var out: [BlockedItem] = []
        if let checks = governanceReport?.checks {
            for c in checks where c.passed == false {
                let slug = c.slug ?? "check"
                let fix: String
                if slug == "docs_governance" { fix = "python3 scripts/ci/check_docs_governance.py" }
                else if slug == "production_gates" { fix = "python3 scripts/run_production_readiness_gates.py" }
                else { fix = "python3 scripts/ci/check_system_governance_status.py" }
                out.append(BlockedItem(severity: "blocker", source: c.name ?? slug, fixCommand: fix))
            }
        }
        for row in state.elevatedFailures.prefix(5) {
            out.append(BlockedItem(severity: "blocker", source: row.signal_id ?? "elevated_failure", fixCommand: "See Observability tab"))
        }
        return out
    }

    private var observabilityPhaseCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Observability phase status (from repo)")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            if let phase = state.observabilityPhaseStatus {
                HStack(spacing: 16) {
                    phaseRow("P1 Observe", phase.p1Observe.rawValue)
                    phaseRow("P2 Document", phase.p2Document.rawValue)
                    phaseRow("P3 Elevate/fix", phase.p3ElevateFix.rawValue)
                    phaseRow("P4 Learn/enhance", phase.p4LearnEnhance.rawValue)
                }
            } else {
                Text("Run collector once to derive phase status.")
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private func phaseRow(_ label: String, _ value: String) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label).font(.caption).foregroundColor(.secondary)
            Text(value).font(.subheadline).fontWeight(.medium)
        }
    }

    private var observabilityCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Observability (POLES)")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            if let snap = state.lastSnapshot {
                HStack(spacing: 16) {
                    StatusBadge(status: "pass")
                    Text("\(snap.passed)")
                    StatusBadge(status: "fail")
                    Text("\(snap.failed)")
                    StatusBadge(status: "skip")
                    Text("\(snap.skipped)")
                }
                Text("Last: \(snap.timestamp)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            } else {
                Text("No snapshot yet. Run Collect signals in Observability tab.")
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private var evidenceCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Evidence log")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            if state.evidenceLogRows.isEmpty {
                Text("No evidence log entries. Run collector in Observability tab.")
                    .foregroundColor(.secondary)
            } else {
                Text("Last \(state.evidenceLogRows.count) entries. See Observability tab for full table.")
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private var elevatedCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Elevated failures")
                .font(.headline)
                .foregroundColor(state.elevatedFailures.isEmpty ? PhoenixColors.phoenixBlue : .red)
            if state.elevatedFailures.isEmpty {
                Text("0 failures — system healthy")
                    .foregroundColor(.secondary)
            } else {
                Text("\(state.elevatedFailures.count) failure(s) in elevated_failures.jsonl")
                    .foregroundColor(.red)
                if let onSelect = onSelectObservability {
                    Button("View in Observability tab", action: onSelect)
                        .font(.caption)
                }
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(state.elevatedFailures.isEmpty ? PhoenixColors.phoenixCardTint : Color.red.opacity(0.08))
        .cornerRadius(8)
    }

    private var branchProtectionCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Branch protection")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            Text("1. Settings → Branches → main: require Core tests")
            Text("2. Notifications: Email for Actions failures")
            Text("3. Watch repo: Custom → Actions")
            Text("4. Keep Production observability scheduled")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private func refresh() {
        guard !state.repoPath.isEmpty else { return }
        governanceReport = artifactReader.loadSystemGovernanceReport(repoPath: state.repoPath)
        freebiesInfo = artifactReader.loadFreebiesIndexInfo(repoPath: state.repoPath)
        state.lastSnapshot = artifactReader.loadLatestSnapshot(repoPath: state.repoPath)
        state.evidenceLogRows = artifactReader.loadEvidenceLog(repoPath: state.repoPath, limit: 20)
        state.elevatedFailures = artifactReader.loadElevatedFailures(repoPath: state.repoPath, limit: 50)
        state.observabilityPhaseStatus = artifactReader.loadObservabilityPhaseStatus(repoPath: state.repoPath)
    }
}
