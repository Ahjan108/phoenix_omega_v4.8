import SwiftUI

/// Completeness tab: scorecard from book_script_content_validation.py --json.
/// Authority: docs/CONTROL_PLANE_SPEC_PATCH_V1.1.md §1
struct CompletenessView: View {
    @ObservedObject var state: AppState
    let scriptRunner: ScriptRunner
    @State private var isRunning = false
    @State private var outputBuffer = ""
    @State private var scorecard: CompletenessScorecard?
    @State private var lastError: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Completeness (content validation)")
                    .font(.title2)
                    .foregroundColor(PhoenixColors.phoenixBlue)
                Text("Data: scripts/book_script_content_validation.py --json. Refresh: on load / manual.")
                    .font(.caption)
                    .foregroundColor(.secondary)
                Button("Run validation (--json)") { runValidation() }
                    .disabled(state.repoPath.isEmpty || isRunning)
                if isRunning {
                    ProgressView().scaleEffect(0.8)
                }
                if let err = lastError {
                    Text(err).foregroundColor(.red).font(.caption)
                }
                if let card = scorecard {
                    completenessCards(card)
                } else if !outputBuffer.isEmpty {
                    Text("Raw output (parse failed or partial):")
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
        .onAppear { if !state.repoPath.isEmpty { runValidation() } }
        .onChange(of: state.refreshTrigger) { _ in if !state.repoPath.isEmpty { runValidation() } }
    }

    private func completenessCards(_ card: CompletenessScorecard) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            if let locs = card.locsLangs?.byLocale {
                ForEach(Array(locs.keys.sorted()), id: \.self) { loc in
                    if let info = locs[loc] {
                        HStack(spacing: 8) {
                            StatusBadge(status: (info["status"] as? String) == "ok" ? "pass" : "fail")
                            Text("Locale \(loc)")
                            Text("\(info["story_ok"] as? Int ?? 0)/\(info["story_total"] as? Int ?? 0) story")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        .padding(6)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(PhoenixColors.phoenixCardTint)
                        .cornerRadius(6)
                    }
                }
            }
            if let teachers = card.teachers?.byTeacher {
                Text("Teachers").font(.headline).foregroundColor(PhoenixColors.phoenixBlue)
                ForEach(Array(teachers.keys.sorted()), id: \.self) { tid in
                    if let info = teachers[tid] {
                        HStack(spacing: 8) {
                            StatusBadge(status: (info["status"] as? String) == "ok" ? "pass" : "fail")
                            Text("Teacher \(tid)")
                        }
                        .padding(6)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(PhoenixColors.phoenixCardTint)
                        .cornerRadius(6)
                    }
                }
            }
            if let sc = card.systemContentInScript {
                HStack(spacing: 8) {
                    StatusBadge(status: (sc["status"] as? String) == "ok" ? "pass" : "fail")
                    Text("System content in script: \(sc["status"] as? String ?? "?")")
                }
                .padding(8)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(PhoenixColors.phoenixCardTint)
                .cornerRadius(6)
            }
        }
    }

    private func runValidation() {
        isRunning = true
        outputBuffer = ""
        lastError = nil
        scorecard = nil
        Task {
            do {
                _ = try await scriptRunner.run(
                    repoPath: state.repoPath,
                    scriptPath: "scripts/book_script_content_validation.py",
                    arguments: ["--json"],
                    timeoutSeconds: 120,
                    onOutput: { outputBuffer += $0 + "\n" }
                )
                await MainActor.run {
                    parseScorecard()
                    isRunning = false
                }
            } catch {
                await MainActor.run {
                    lastError = error.localizedDescription
                    isRunning = false
                }
            }
        }
    }

    private func parseScorecard() {
        let trimmed = outputBuffer.trimmingCharacters(in: .whitespacesAndNewlines)
        guard let data = trimmed.data(using: .utf8) else { return }
        do {
            let raw = try JSONSerialization.jsonObject(with: data) as? [String: Any]
            scorecard = CompletenessScorecard(from: raw ?? [:])
        } catch {
            lastError = "Parse error: \(error.localizedDescription)"
        }
    }
}

/// Parsed output of book_script_content_validation.py --json
struct CompletenessScorecard {
    var locsLangs: LocsLangs?
    var teachers: Teachers?
    var systemContentInScript: [String: Any]?

    struct LocsLangs {
        var byLocale: [String: [String: Any]]?
    }
    struct Teachers {
        var byTeacher: [String: [String: Any]]?
    }

    init(from dict: [String: Any]) {
        if let ll = dict["locs_langs"] as? [String: Any] {
            locsLangs = LocsLangs(byLocale: ll["by_locale"] as? [String: [String: Any]])
        } else {
            locsLangs = nil
        }
        if let te = dict["teachers"] as? [String: Any] {
            teachers = Teachers(byTeacher: te["by_teacher"] as? [String: [String: Any]])
        } else {
            teachers = nil
        }
        systemContentInScript = dict["system_content_in_script"] as? [String: Any]
    }
}
