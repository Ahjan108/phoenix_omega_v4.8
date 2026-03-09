import SwiftUI
import AppKit

// MARK: - Models

struct ManualReviewEntry: Identifiable, Decodable, Hashable {
    let id = UUID()
    let section_id: String
    let locale: String
    let book_id: String?
    let batch_id: String?
    let hard_gate_failures: Int
    let aggregate_score_best: Double?
    let loops_run: Int?
    let queued_at: String?
    let packet_path: String?

    enum CodingKeys: String, CodingKey {
        case section_id, locale, book_id, batch_id
        case hard_gate_failures, aggregate_score_best
        case loops_run, queued_at, packet_path
    }
}

// MARK: - ManualReviewView

struct ManualReviewView: View {
    @ObservedObject var state: AppState
    let artifactReader: ArtifactReader
    let scriptRunner: ScriptRunner

    @State private var entries: [ManualReviewEntry] = []
    @State private var selectedEntry: ManualReviewEntry?
    @State private var packetText: String = ""
    @State private var loadError: String?
    @State private var isRunning: Bool = false
    @State private var logOutput: String = ""
    @State private var lastRefreshed: Date?

    var body: some View {
        HSplitView {
            // Left: queue list
            queuePanel
                .frame(minWidth: 280, idealWidth: 340, maxWidth: 400)

            // Right: detail / re-run panel
            detailPanel
                .frame(minWidth: 360)
        }
        .background(PhoenixColors.phoenixBackground)
        .onAppear { loadQueue() }
    }

    // MARK: - Queue Panel

    private var queuePanel: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Header
            HStack {
                Label("Manual Review Queue", systemImage: "exclamationmark.triangle.fill")
                    .font(.headline)
                    .foregroundColor(entries.isEmpty ? .secondary : .orange)
                Spacer()
                if !entries.isEmpty {
                    Text("\(entries.count)")
                        .font(.caption.bold())
                        .foregroundColor(.white)
                        .padding(.horizontal, 7)
                        .padding(.vertical, 3)
                        .background(entries.filter { $0.hard_gate_failures > 0 }.isEmpty ? Color.orange : Color.red)
                        .clipShape(Capsule())
                }
                Button(action: loadQueue) {
                    Image(systemName: "arrow.clockwise")
                }
                .buttonStyle(.borderless)
                .help("Refresh queue from artifacts/audiobook/manual_review_queue.json")
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 10)
            .background(PhoenixColors.phoenixCardTint.opacity(0.6))

            if let err = loadError {
                VStack(spacing: 8) {
                    Image(systemName: "doc.questionmark")
                        .font(.largeTitle)
                        .foregroundColor(.secondary)
                    Text(err)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .padding()
            } else if entries.isEmpty {
                VStack(spacing: 8) {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.largeTitle)
                        .foregroundColor(.green)
                    Text("Queue is empty")
                        .font(.subheadline.bold())
                    Text("All sections passed or no runs yet.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .padding()
            } else {
                List(entries, selection: $selectedEntry) { entry in
                    queueRow(entry)
                        .tag(entry)
                }
                .listStyle(.inset)
                .onChange(of: selectedEntry) { newEntry in
                    if let e = newEntry { loadPacket(e) }
                }
            }

            if let refreshed = lastRefreshed {
                Text("Refreshed \(refreshed.formatted(date: .omitted, time: .shortened))")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .padding([.horizontal, .bottom], 8)
            }
        }
    }

    @ViewBuilder
    private func queueRow(_ entry: ManualReviewEntry) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack(spacing: 6) {
                // Severity badge
                if entry.hard_gate_failures > 0 {
                    Text("\(entry.hard_gate_failures) HARD")
                        .font(.caption2.bold())
                        .foregroundColor(.white)
                        .padding(.horizontal, 5)
                        .padding(.vertical, 2)
                        .background(Color.red)
                        .clipShape(RoundedRectangle(cornerRadius: 4))
                }
                Text(entry.locale)
                    .font(.caption.bold())
                    .foregroundColor(PhoenixColors.phoenixBlue)
            }
            Text(entry.section_id)
                .font(.caption)
                .lineLimit(1)
            HStack(spacing: 8) {
                if let score = entry.aggregate_score_best {
                    Label(String(format: "%.2f", score), systemImage: "chart.bar.xaxis")
                        .font(.caption2)
                        .foregroundColor(score < 0.5 ? .red : score < 0.75 ? .orange : .secondary)
                }
                if let loops = entry.loops_run {
                    Label("\(loops) loops", systemImage: "arrow.clockwise")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
                if let book = entry.book_id {
                    Text(book)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                        .lineLimit(1)
                }
            }
        }
        .padding(.vertical, 4)
    }

    // MARK: - Detail Panel

    private var detailPanel: some View {
        VStack(alignment: .leading, spacing: 0) {
            if let entry = selectedEntry {
                // Entry header
                VStack(alignment: .leading, spacing: 6) {
                    HStack {
                        VStack(alignment: .leading, spacing: 2) {
                            Text(entry.section_id)
                                .font(.title3.bold())
                            HStack(spacing: 10) {
                                Text(entry.locale)
                                    .font(.caption.bold())
                                    .foregroundColor(PhoenixColors.phoenixBlue)
                                if let book = entry.book_id {
                                    Text("book: \(book)")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }
                                if let batch = entry.batch_id {
                                    Text("batch: \(batch)")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }
                            }
                        }
                        Spacer()
                        severityBadge(entry)
                    }

                    HStack(spacing: 16) {
                        if let score = entry.aggregate_score_best {
                            statPill(label: "Best score", value: String(format: "%.3f", score),
                                     color: score < 0.5 ? .red : score < 0.75 ? .orange : .green)
                        }
                        statPill(label: "Hard failures", value: "\(entry.hard_gate_failures)",
                                 color: entry.hard_gate_failures > 0 ? .red : .green)
                        if let loops = entry.loops_run {
                            statPill(label: "Loops run", value: "\(loops)", color: .secondary)
                        }
                        if let queued = entry.queued_at {
                            statPill(label: "Queued", value: String(queued.prefix(10)), color: .secondary)
                        }
                    }
                }
                .padding(12)
                .background(PhoenixColors.phoenixCardTint)

                Divider()

                // Re-run controls
                HStack(spacing: 10) {
                    Button("Re-run section") { rerunSection(entry) }
                        .disabled(state.repoPath.isEmpty || isRunning)
                    Button("Open artifacts folder") { openArtifacts(entry) }
                        .disabled(entry.packet_path == nil || state.repoPath.isEmpty)
                    Spacer()
                    if isRunning {
                        ProgressView().scaleEffect(0.8)
                        Button("Cancel") { scriptRunner.cancel(); isRunning = false }
                    }
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 8)

                Divider()

                // Packet / log viewer
                VStack(alignment: .leading, spacing: 0) {
                    Text(packetText.isEmpty ? "Select an entry to view its review packet." : "Review packet — best_draft + defect_history:")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .padding(.horizontal, 12)
                        .padding(.top, 8)

                    ScrollView {
                        Text(logOutput.isEmpty ? packetText : logOutput)
                            .font(.system(.caption, design: .monospaced))
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(12)
                            .textSelection(.enabled)
                    }
                    .background(Color.black.opacity(0.04))
                }

            } else {
                VStack(spacing: 12) {
                    Image(systemName: "arrow.left.circle")
                        .font(.largeTitle)
                        .foregroundColor(.secondary)
                    Text("Select a section from the queue to review its artifact packet and re-run options.")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                        .frame(maxWidth: 320)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .padding()
            }
        }
    }

    @ViewBuilder
    private func severityBadge(_ entry: ManualReviewEntry) -> some View {
        if entry.hard_gate_failures > 0 {
            Label("\(entry.hard_gate_failures) hard gate failure\(entry.hard_gate_failures == 1 ? "" : "s")", systemImage: "xmark.shield.fill")
                .font(.caption.bold())
                .foregroundColor(.white)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color.red)
                .clipShape(RoundedRectangle(cornerRadius: 6))
        } else {
            Label("Scored gate only", systemImage: "exclamationmark.triangle")
                .font(.caption.bold())
                .foregroundColor(.white)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color.orange)
                .clipShape(RoundedRectangle(cornerRadius: 6))
        }
    }

    @ViewBuilder
    private func statPill(label: String, value: String, color: Color) -> some View {
        VStack(spacing: 1) {
            Text(value)
                .font(.caption.bold())
                .foregroundColor(color)
            Text(label)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(PhoenixColors.phoenixCardTint)
        .clipShape(RoundedRectangle(cornerRadius: 6))
    }

    // MARK: - Data Loading

    private func loadQueue() {
        guard !state.repoPath.isEmpty else {
            loadError = "Set repo path in toolbar to load the manual review queue."
            return
        }
        let queueURL = artifactReader.repoURL(repoPath: state.repoPath)
            .appendingPathComponent("artifacts/audiobook/manual_review_queue.json")
        guard let data = try? Data(contentsOf: queueURL) else {
            entries = []
            loadError = "Queue file not found.\nPath: artifacts/audiobook/manual_review_queue.json\n\nRun the audiobook pipeline to generate entries."
            lastRefreshed = Date()
            return
        }
        do {
            let decoded = try JSONDecoder().decode([ManualReviewEntry].self, from: data)
            // Sort: hard_gate_failures desc, then aggregate_score asc (most broken first)
            entries = decoded.sorted {
                if $0.hard_gate_failures != $1.hard_gate_failures {
                    return $0.hard_gate_failures > $1.hard_gate_failures
                }
                return ($0.aggregate_score_best ?? 1.0) < ($1.aggregate_score_best ?? 1.0)
            }
            loadError = nil
            lastRefreshed = Date()
        } catch {
            loadError = "Failed to parse queue: \(error.localizedDescription)"
            lastRefreshed = Date()
        }
    }

    private func loadPacket(_ entry: ManualReviewEntry) {
        logOutput = ""
        guard !state.repoPath.isEmpty else { return }
        let baseURL = artifactReader.repoURL(repoPath: state.repoPath)

        var text = "=== SECTION: \(entry.section_id) | LOCALE: \(entry.locale) ===\n\n"

        // Try to load best_draft.txt
        let packetBase: URL
        if let pp = entry.packet_path {
            packetBase = baseURL.appendingPathComponent(pp)
        } else {
            packetBase = baseURL
                .appendingPathComponent("artifacts/audiobook")
                .appendingPathComponent(entry.book_id ?? "unknown")
                .appendingPathComponent(entry.locale)
                .appendingPathComponent(entry.section_id)
        }

        if let draft = try? String(contentsOf: packetBase.appendingPathComponent("best_draft.txt")) {
            text += "--- BEST DRAFT ---\n\(draft)\n\n"
        }
        if let summary = try? String(contentsOf: packetBase.appendingPathComponent("review_summary.txt")) {
            text += "--- REVIEW SUMMARY ---\n\(summary)\n\n"
        }
        if let history = try? String(contentsOf: packetBase.appendingPathComponent("defect_history.json")) {
            text += "--- DEFECT HISTORY ---\n\(history)\n"
        }

        packetText = text.isEmpty ? "No packet files found at expected path.\nExpected: \(packetBase.path)" : text
    }

    private func rerunSection(_ entry: ManualReviewEntry) {
        guard !state.repoPath.isEmpty else { return }
        logOutput = "Starting re-run for \(entry.section_id) [\(entry.locale)]...\n"
        isRunning = true

        Task {
            do {
                var args = [
                    "--section-id", entry.section_id,
                    "--locale", entry.locale,
                    "--batch-id", "rerun_\(Int(Date().timeIntervalSince1970))",
                ]
                if let book = entry.book_id { args += ["--book-id", book] }

                _ = try await scriptRunner.run(
                    repoPath: state.repoPath,
                    scriptPath: "scripts/audiobook_script/run_comparator_loop.py",
                    arguments: args,
                    timeoutSeconds: 300,
                    onOutput: { line in
                        Task { @MainActor in logOutput += line + "\n" }
                    }
                )
                await MainActor.run {
                    logOutput += "\n✓ Re-run complete. Refreshing queue...\n"
                    isRunning = false
                    loadQueue()
                }
            } catch {
                await MainActor.run {
                    logOutput += "\n✗ Re-run failed: \(error)\n"
                    isRunning = false
                }
            }
        }
    }

    private func openArtifacts(_ entry: ManualReviewEntry) {
        guard !state.repoPath.isEmpty else { return }
        let baseURL = artifactReader.repoURL(repoPath: state.repoPath)
        let packetBase: URL
        if let pp = entry.packet_path {
            packetBase = baseURL.appendingPathComponent(pp)
        } else {
            packetBase = baseURL
                .appendingPathComponent("artifacts/audiobook")
                .appendingPathComponent(entry.book_id ?? "unknown")
                .appendingPathComponent(entry.locale)
                .appendingPathComponent(entry.section_id)
        }
        NSWorkspace.shared.open(packetBase)
    }
}
