import SwiftUI
import UniformTypeIdentifiers

struct DocsConfigView: View {
    @ObservedObject var state: AppState
    let artifactReader: ArtifactReader
    let scriptRunner: ScriptRunner
    @State private var logOutput: String = ""
    @State private var isRunning: Bool = false
    @State private var governanceReport: SystemGovernanceReport?
    @State private var contentReport: ContentCoverageReport?

    private var repoURL: URL? {
        guard !state.repoPath.isEmpty else { return nil }
        return URL(fileURLWithPath: (state.repoPath as NSString).expandingTildeInPath)
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Docs & config")
                    .font(.title2)
                    .foregroundColor(PhoenixColors.phoenixBlue)
                if let url = repoURL {
                    Group {
                        docLink("DOCS_INDEX", "docs/DOCS_INDEX.md")
                        docLink("Branch protection", "docs/BRANCH_PROTECTION_REQUIREMENTS.md")
                        docLink("Observability spec", "docs/PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md")
                        docLink("Marketing prompts", "docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md")
                    }
                }

                governanceAndContentCard

                HStack(spacing: 8) {
                    Button("Run check_docs_governance") { runDocsCheck() }
                        .disabled(state.repoPath.isEmpty || isRunning)
                    Button("Run system governance") { runSystemGovernance() }
                        .disabled(state.repoPath.isEmpty || isRunning)
                    Button("Run content coverage report") { runContentCoverageReport() }
                        .disabled(state.repoPath.isEmpty || isRunning)
                    if isRunning {
                        Button("Cancel") { scriptRunner.cancel() }
                    }
                }
                LiveLogView(logText: $logOutput, isRunning: isRunning)
            }
            .padding()
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .background(PhoenixColors.phoenixBackground)
        .onAppear { loadReports() }
        .onChange(of: state.repoPath) { _, _ in loadReports() }
        .onChange(of: state.refreshTrigger) { _, _ in loadReports() }
    }

    private var governanceAndContentCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Governance & content status")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            if governanceReport != nil || contentReport != nil {
                if let gov = governanceReport {
                    governanceSummaryView(gov)
                } else {
                    Text("Governance: no report yet. Run \"Run system governance\".")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                Divider()
                if let content = contentReport {
                    contentCoverageSummaryView(content)
                } else {
                    Text("Content coverage: no report yet. Run \"Run content coverage report\".")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            } else {
                Text("Run the scripts above to generate reports. Results appear here and in artifacts/.")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private func governanceSummaryView(_ report: SystemGovernanceReport) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            if let summary = report.summary {
                HStack(spacing: 12) {
                    Text("Docs / system governance:")
                        .font(.subheadline)
                        .fontWeight(.medium)
                    StatusBadge(status: (summary.failed ?? 0) == 0 ? "pass" : "fail")
                    Text("\(summary.passed ?? 0)/\(summary.total ?? 0) passed")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            if let checks = report.checks {
                ForEach(Array(checks.enumerated()), id: \.offset) { _, c in
                    HStack(alignment: .top, spacing: 6) {
                        StatusBadge(status: (c.passed ?? false) ? "pass" : "fail")
                        Text(c.name ?? c.slug ?? "?")
                            .font(.caption)
                    }
                }
            }
        }
    }

    private func contentCoverageSummaryView(_ report: ContentCoverageReport) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 12) {
                Text("Content coverage (book prose):")
                    .font(.subheadline)
                    .fontWeight(.medium)
                StatusBadge(status: (report.summary_ok ?? false) ? "pass" : "fail")
            }
            row("Atoms STORY", report.story_coverage_ok)
            row("Atoms non-STORY", report.non_story_coverage_ok)
            row("Plan coverage (K-table + pools)", report.plan_coverage_ok)
            if let failed = report.teachers_failed, !failed.isEmpty {
                HStack(alignment: .top, spacing: 6) {
                    StatusBadge(status: "fail")
                    Text("Teacher readiness: \(failed.count) failed — \(failed.prefix(3).joined(separator: ", "))\(failed.count > 3 ? "…" : "")")
                        .font(.caption)
                }
            } else if report.teacher_readiness != nil {
                row("Teacher readiness", true)
            }
            if let errors = report.plan_coverage_errors, !errors.isEmpty, errors.count <= 5 {
                Text(errors.prefix(3).joined(separator: "\n"))
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .lineLimit(3)
            } else if let errors = report.plan_coverage_errors, !errors.isEmpty {
                Text("\(errors.count) plan coverage errors — see artifacts/content_coverage_report.json")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
    }

    private func row(_ label: String, _ ok: Bool?) -> some View {
        HStack(alignment: .top, spacing: 6) {
            StatusBadge(status: (ok ?? false) ? "pass" : "fail")
            Text(label)
                .font(.caption)
        }
    }

    private func docLink(_ label: String, _ path: String) -> some View {
        guard let base = repoURL else { return AnyView(EmptyView()) }
        let fileURL = base.appendingPathComponent(path)
        return AnyView(
            Link(label, destination: fileURL)
                .padding(2)
        )
    }

    private func loadReports() {
        guard !state.repoPath.isEmpty else { return }
        governanceReport = artifactReader.loadSystemGovernanceReport(repoPath: state.repoPath)
        contentReport = artifactReader.loadContentCoverageReport(repoPath: state.repoPath)
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
                    arguments: ["--check-inventory"],
                    timeoutSeconds: 120,
                    onOutput: { logOutput += $0 + "\n" }
                )
                await MainActor.run {
                    isRunning = false
                    loadReports()
                }
            } catch {
                await MainActor.run {
                    logOutput += "\nError: \(error)"
                    isRunning = false
                }
            }
        }
    }

    private func runSystemGovernance() {
        guard !state.repoPath.isEmpty else { return }
        logOutput = ""
        isRunning = true
        Task {
            do {
                _ = try await scriptRunner.run(
                    repoPath: state.repoPath,
                    scriptPath: "scripts/ci/check_system_governance_status.py",
                    arguments: [],
                    timeoutSeconds: 180,
                    onOutput: { logOutput += $0 + "\n" }
                )
                await MainActor.run {
                    isRunning = false
                    loadReports()
                }
            } catch {
                await MainActor.run {
                    logOutput += "\nError: \(error)"
                    isRunning = false
                }
            }
        }
    }

    private func runContentCoverageReport() {
        guard !state.repoPath.isEmpty else { return }
        logOutput = ""
        isRunning = true
        Task {
            do {
                _ = try await scriptRunner.run(
                    repoPath: state.repoPath,
                    scriptPath: "scripts/ci/content_coverage_report.py",
                    arguments: [],
                    timeoutSeconds: 300,
                    onOutput: { logOutput += $0 + "\n" }
                )
                await MainActor.run {
                    isRunning = false
                    loadReports()
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
