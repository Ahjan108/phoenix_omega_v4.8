import SwiftUI

/// System Metadata tab: BookSpec/CompiledBook fields, present in plans, in script (from validation --plan).
/// Authority: docs/CONTROL_PLANE_SPEC_PATCH_V1.1.md §3
struct SystemMetadataView: View {
    @ObservedObject var state: AppState
    let artifactReader: ArtifactReader
    let scriptRunner: ScriptRunner
    @State private var selectedPlanPath: String = ""
    @State private var planPaths: [String] = []
    @State private var isRunning = false
    @State private var outputBuffer = ""
    @State private var metadataSummary: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("System metadata inventory")
                    .font(.title2)
                    .foregroundColor(PhoenixColors.phoenixBlue)
                Text("Data: book_script_content_validation.py --plan <path> --json. Select a plan to see metadata vs script.")
                    .font(.caption)
                    .foregroundColor(.secondary)
                HStack(spacing: 8) {
                    Picker("Plan", selection: $selectedPlanPath) {
                        Text("(Select plan)").tag("")
                        ForEach(planPaths, id: \.self) { path in
                            Text((path as NSString).lastPathComponent).tag(path)
                        }
                    }
                    .frame(maxWidth: 280)
                    Button("Run validation") { runWithPlan() }
                        .disabled(state.repoPath.isEmpty || selectedPlanPath.isEmpty || isRunning)
                }
                if isRunning {
                    ProgressView().scaleEffect(0.8)
                }
                if let summary = metadataSummary {
                    Text(summary)
                        .font(.system(.caption, design: .monospaced))
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(8)
                        .background(PhoenixColors.phoenixCardTint)
                        .cornerRadius(6)
                }
                if !outputBuffer.isEmpty && metadataSummary == nil {
                    Text("Output:")
                        .font(.caption)
                    Text(outputBuffer)
                        .font(.system(.caption, design: .monospaced))
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(8)
                        .background(Color.secondary.opacity(0.1))
                        .cornerRadius(6)
                }
            }
            .padding()
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .background(PhoenixColors.phoenixBackground)
        .onAppear { loadPlanPaths() }
        .onChange(of: state.refreshTrigger) { _ in loadPlanPaths() }
        .onChange(of: state.repoPath) { _ in loadPlanPaths() }
    }

    private func loadPlanPaths() {
        guard !state.repoPath.isEmpty else { planPaths = []; return }
        let base = artifactReader.repoURL(repoPath: state.repoPath)
        let plansDir = base.appendingPathComponent("artifacts/systems_test/plans")
        var paths: [String] = []
        if let contents = try? FileManager.default.contentsOfDirectory(at: plansDir, includingPropertiesForKeys: nil) {
            for url in contents where url.pathExtension == "json" {
                paths.append(url.path)
            }
        }
        let fullCatalog = base.appendingPathComponent("artifacts/full_catalog")
        if let contents = try? FileManager.default.contentsOfDirectory(at: fullCatalog, includingPropertiesForKeys: nil) {
            for url in contents where url.pathExtension == "json" {
                paths.append(url.path)
            }
        }
        planPaths = paths.sorted()
        if selectedPlanPath.isEmpty, let first = planPaths.first {
            selectedPlanPath = first
        }
    }

    private func runWithPlan() {
        guard !selectedPlanPath.isEmpty else { return }
        isRunning = true
        outputBuffer = ""
        metadataSummary = nil
        let base = (state.repoPath as NSString).expandingTildeInPath
        let relPath = (selectedPlanPath as NSString).replacingOccurrences(of: base + "/", with: "")
        Task {
            do {
                _ = try await scriptRunner.run(
                    repoPath: state.repoPath,
                    scriptPath: "scripts/book_script_content_validation.py",
                    arguments: ["--plan", relPath, "--json"],
                    timeoutSeconds: 60,
                    onOutput: { outputBuffer += $0 + "\n" }
                )
                await MainActor.run {
                    metadataSummary = outputBuffer.trimmingCharacters(in: .whitespacesAndNewlines)
                    if metadataSummary?.hasPrefix("{") == true {
                        metadataSummary = "JSON output (see raw for full). Plan: \(relPath)"
                    }
                    isRunning = false
                }
            } catch {
                await MainActor.run {
                    outputBuffer += "\nError: \(error)"
                    isRunning = false
                }
            }
        }
    }
}
