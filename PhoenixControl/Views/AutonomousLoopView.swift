import SwiftUI
import AppKit

/// Autonomous loop UI: loop health (continuous/daily/weekly), operations board, promotion queue, run-now actions.
/// Authority: docs/ML_AUTONOMOUS_LOOP_SPEC.md §11, EXECUTIVE_DASHBOARD_AND_PHOENIXCONTROL_SPEC
struct AutonomousLoopView: View {
    @ObservedObject var state: AppState
    let artifactReader: ArtifactReader
    let scriptRunner: ScriptRunner
    @State private var opsBoard: [ArtifactReader.OperationsBoardRow] = []
    @State private var promotionQueue: [ArtifactReader.PromotionQueueRow] = []
    @State private var continuousLastRun: Date?
    @State private var dailyLastRun: Date?
    @State private var weeklyLastRun: Date?
    @State private var logOutput: String = ""
    @State private var runningScript: String?

    private static let dateFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateStyle = .short
        f.timeStyle = .short
        return f
    }()

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Autonomous loop")
                    .font(.title2)
                    .foregroundColor(PhoenixColors.phoenixBlue)
                Text("Loop health, operations board, promotion queue. Data: operations_board.jsonl, promotion_queue.jsonl, weekly_report.json.")
                    .font(.caption)
                    .foregroundColor(.secondary)
                loopHealthCard
                runNowSection
                operationsBoardSection
                promotionQueueSection
                LiveLogView(logText: $logOutput, isRunning: runningScript != nil)
            }
            .padding()
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .background(PhoenixColors.phoenixBackground)
        .onAppear { refresh() }
        .onChange(of: state.refreshTrigger) { _ in refresh() }
        .onChange(of: state.repoPath) { _ in refresh() }
    }

    private var loopHealthCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Loop health (last run)")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            HStack(alignment: .top, spacing: 24) {
                loopStatusRow("Continuous (24/7)", lastRun: continuousLastRun, artifactPath: "artifacts/ml_loop/continuous_candidates.jsonl")
                loopStatusRow("Daily promotion", lastRun: dailyLastRun, artifactPath: "artifacts/ml_loop/promotion_queue.jsonl")
                loopStatusRow("Weekly recalibration", lastRun: weeklyLastRun, artifactPath: "artifacts/ml_loop/weekly_report.json")
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private func loopStatusRow(_ label: String, lastRun: Date?, artifactPath: String) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(label).font(.subheadline)
            if let date = lastRun {
                Text(Self.dateFormatter.string(from: date))
                    .font(.caption)
                    .foregroundColor(.secondary)
            } else {
                Text("No run yet")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
    }

    private var runNowSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Run now")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            HStack(spacing: 12) {
                Button("Continuous loop") { runScript("scripts/ml_loop/run_continuous_loop.py", []) }
                    .disabled(state.repoPath.isEmpty || runningScript != nil)
                Button("Daily promotion") { runScript("scripts/ml_loop/run_daily_promotion.py", []) }
                    .disabled(state.repoPath.isEmpty || runningScript != nil)
                Button("Weekly recalibration") { runScript("scripts/ml_loop/run_weekly_market_recalibration.py", []) }
                    .disabled(state.repoPath.isEmpty || runningScript != nil)
                if runningScript != nil {
                    Button("Cancel") { scriptRunner.cancel() }
                }
            }
            if let name = runningScript {
                Text("Running: \(name)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private var operationsBoardSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Operations board (issue → fix → PR → merged → impact)")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            if opsBoard.isEmpty {
                Text("No operations board data. Path: artifacts/observability/operations_board.jsonl")
                    .font(.caption)
                    .foregroundColor(.secondary)
            } else {
                Table(opsBoard.prefix(20).enumerated().map { (i, r) in IdentifiableBoardRow(id: i, row: r) }) {
                    TableColumn("Signal") { item in Text(item.row.signal_id ?? "—") }
                    TableColumn("Status") { item in Text(item.row.status ?? "—") }
                    TableColumn("Fix") { item in Text((item.row.suggested_fix ?? "—").prefix(40)) }
                    TableColumn("Merged") { item in Text((item.row.merged ?? false) ? "Yes" : "No") }
                }
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private struct IdentifiableBoardRow: Identifiable {
        let id: Int
        let row: ArtifactReader.OperationsBoardRow
    }

    private var promotionQueueSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Promotion queue (gate-passing candidates)")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            if promotionQueue.isEmpty {
                Text("No promotion queue data. Path: artifacts/ml_loop/promotion_queue.jsonl")
                    .font(.caption)
                    .foregroundColor(.secondary)
            } else {
                ForEach(Array(promotionQueue.prefix(15).enumerated()), id: \.offset) { _, r in
                    HStack(spacing: 12) {
                        Text(r.book_id ?? "—")
                        Text(r.source ?? "—")
                        Text(r.decision ?? "—")
                        if let c = r.confidence {
                            Text(String(format: "%.2f", c))
                                .foregroundColor(.secondary)
                        }
                    }
                    .font(.caption)
                }
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private func runScript(_ path: String, _ args: [String]) {
        runningScript = path
        logOutput = ""
        Task {
            do {
                _ = try await scriptRunner.run(
                    repoPath: state.repoPath,
                    scriptPath: path,
                    arguments: args,
                    timeoutSeconds: 600,
                    onOutput: { logOutput += $0 + "\n" }
                )
                await MainActor.run {
                    runningScript = nil
                    refresh()
                }
            } catch {
                await MainActor.run {
                    logOutput += "\nError: \(error)"
                    runningScript = nil
                }
            }
        }
    }

    private func refresh() {
        guard !state.repoPath.isEmpty else { return }
        opsBoard = artifactReader.loadOperationsBoard(repoPath: state.repoPath, limit: 100)
        promotionQueue = artifactReader.loadPromotionQueue(repoPath: state.repoPath, limit: 50)
        continuousLastRun = artifactReader.lastRunTime(repoPath: state.repoPath, relativePath: "artifacts/ml_loop/continuous_candidates.jsonl")
        dailyLastRun = artifactReader.lastRunTime(repoPath: state.repoPath, relativePath: "artifacts/ml_loop/promotion_queue.jsonl")
        weeklyLastRun = artifactReader.lastRunTime(repoPath: state.repoPath, relativePath: "artifacts/ml_loop/weekly_report.json")
    }
}
