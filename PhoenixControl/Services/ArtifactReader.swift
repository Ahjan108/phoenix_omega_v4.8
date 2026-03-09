import Foundation

/// Reads observability artifacts from repo path: snapshot, evidence_log.jsonl, elevated_failures.jsonl.
final class ArtifactReader {
    private let fileManager = FileManager.default

    /// Resolved repo root URL (expands tilde).
    func repoURL(repoPath: String) -> URL {
        URL(fileURLWithPath: (repoPath as NSString).expandingTildeInPath)
    }

    /// Latest signal snapshot from artifacts/observability/signal_snapshot*.json
    func loadLatestSnapshot(repoPath: String) -> ObservabilitySnapshot? {
        let observabilityDir = repoURL(repoPath: repoPath).appendingPathComponent("artifacts/observability")
        guard let contents = try? fileManager.contentsOfDirectory(at: observabilityDir, includingPropertiesForKeys: [.contentModificationDateKey], options: .skipsHiddenFiles) else { return nil }
        let snapshots = contents.filter { $0.lastPathComponent.hasPrefix("signal_snapshot") && $0.pathExtension == "json" }
        guard let latest = snapshots.sorted(by: { a, b in
            ((try? a.resourceValues(forKeys: [.contentModificationDateKey]).contentModificationDate) ?? .distantPast) >
            ((try? b.resourceValues(forKeys: [.contentModificationDateKey]).contentModificationDate) ?? .distantPast)
        }).first else { return nil }
        guard let data = try? Data(contentsOf: latest) else { return nil }
        return try? JSONDecoder().decode(ObservabilitySnapshot.self, from: data)
    }

    /// Parse JSONL file into rows. Returns last `limit` lines (tail).
    func loadEvidenceLog(repoPath: String, limit: Int = 500) -> [EvidenceLogRow] {
        let path = repoURL(repoPath: repoPath).appendingPathComponent("artifacts/observability/evidence_log.jsonl")
        return loadJSONL(path: path, limit: limit)
    }

    func loadElevatedFailures(repoPath: String, limit: Int = 200) -> [EvidenceLogRow] {
        let path = repoURL(repoPath: repoPath).appendingPathComponent("artifacts/observability/elevated_failures.jsonl")
        return loadJSONL(path: path, limit: limit)
    }

    /// System governance report from artifacts/governance/system_governance_report.json
    func loadSystemGovernanceReport(repoPath: String) -> SystemGovernanceReport? {
        let path = repoURL(repoPath: repoPath).appendingPathComponent("artifacts/governance/system_governance_report.json")
        guard let data = try? Data(contentsOf: path) else { return nil }
        return try? JSONDecoder().decode(SystemGovernanceReport.self, from: data)
    }

    /// Content coverage report from artifacts/content_coverage_report.json
    func loadContentCoverageReport(repoPath: String) -> ContentCoverageReport? {
        let path = repoURL(repoPath: repoPath).appendingPathComponent("artifacts/content_coverage_report.json")
        guard let data = try? Data(contentsOf: path) else { return nil }
        return try? JSONDecoder().decode(ContentCoverageReport.self, from: data)
    }

    /// Freebies index health for Governance/Executive spec: path, row count, last modified.
    struct FreebiesIndexInfo {
        let path: String
        let rowCount: Int
        let lastModified: Date?
        let exists: Bool
    }
    func loadFreebiesIndexInfo(repoPath: String) -> FreebiesIndexInfo {
        let base = repoURL(repoPath: repoPath)
        let path = base.appendingPathComponent("artifacts/freebies/index.jsonl")
        let pathStr = "artifacts/freebies/index.jsonl"
        guard fileManager.fileExists(atPath: path.path) else {
            return FreebiesIndexInfo(path: pathStr, rowCount: 0, lastModified: nil, exists: false)
        }
        var count = 0
        if let content = try? String(contentsOf: path, encoding: .utf8) {
            count = content.split(separator: "\n", omittingEmptySubsequences: true).count
        }
        var mtime: Date?
        if let attrs = try? fileManager.attributesOfItem(atPath: path.path) {
            mtime = attrs[.modificationDate] as? Date
        }
        return FreebiesIndexInfo(path: pathStr, rowCount: count, lastModified: mtime, exists: true)
    }

    // MARK: - Pearl News Board
    struct PearlNewsBoardInfo {
        let checklistPath: String
        let checklistExists: Bool
        let evidencePath: String
        let evidenceExists: Bool
        let draftsDirExists: Bool
    }
    func loadPearlNewsBoardInfo(repoPath: String) -> PearlNewsBoardInfo {
        let base = repoURL(repoPath: repoPath)
        let checklist = base.appendingPathComponent("docs/PEARL_NEWS_GO_NO_GO_CHECKLIST.md")
        let evidence = base.appendingPathComponent("artifacts/pearl_news/evaluation/networked_run_evidence.json")
        let drafts = base.appendingPathComponent("artifacts/pearl_news/drafts")
        return PearlNewsBoardInfo(
            checklistPath: "docs/PEARL_NEWS_GO_NO_GO_CHECKLIST.md",
            checklistExists: fileManager.fileExists(atPath: checklist.path),
            evidencePath: "artifacts/pearl_news/evaluation/networked_run_evidence.json",
            evidenceExists: fileManager.fileExists(atPath: evidence.path),
            draftsDirExists: fileManager.fileExists(atPath: drafts.path)
        )
    }

    // MARK: - Autonomous loop (operations board, promotion queue, weekly report)
    struct OperationsBoardRow: Codable {
        let timestamp: String?
        let signal_id: String?
        let status: String?
        let suggested_fix: String?
        let pr_url: String?
        let merged: Bool?
        let impact: String?
    }
    func loadOperationsBoard(repoPath: String, limit: Int = 100) -> [OperationsBoardRow] {
        let path = repoURL(repoPath: repoPath).appendingPathComponent("artifacts/observability/operations_board.jsonl")
        return loadGenericJSONL(path: path, limit: limit)
    }

    struct PromotionQueueRow: Codable {
        let ts: String?
        let book_id: String?
        let source: String?
        let decision: String?
        let confidence: Double?
    }
    func loadPromotionQueue(repoPath: String, limit: Int = 50) -> [PromotionQueueRow] {
        let path = repoURL(repoPath: repoPath).appendingPathComponent("artifacts/ml_loop/promotion_queue.jsonl")
        return loadGenericJSONL(path: path, limit: limit)
    }

    func loadWeeklyReport(repoPath: String) -> [String: Any]? {
        let path = repoURL(repoPath: repoPath).appendingPathComponent("artifacts/ml_loop/weekly_report.json")
        guard let data = try? Data(contentsOf: path) else { return nil }
        return try? JSONSerialization.jsonObject(with: data) as? [String: Any]
    }

    /// Last run time for a script/artifact path (mtime of file or dir).
    func lastRunTime(repoPath: String, relativePath: String) -> Date? {
        let url = repoURL(repoPath: repoPath).appendingPathComponent(relativePath)
        guard let attrs = try? fileManager.attributesOfItem(atPath: url.path) else { return nil }
        return attrs[.modificationDate] as? Date
    }

    private func loadGenericJSONL<T: Decodable>(path: URL, limit: Int) -> [T] {
        guard let content = try? String(contentsOf: path, encoding: .utf8) else { return [] }
        let lines = content.split(separator: "\n", omittingEmptySubsequences: true)
        let decoder = JSONDecoder()
        var rows: [T] = []
        for line in lines.suffix(limit) {
            guard let data = String(line).data(using: .utf8),
                  let row = try? decoder.decode(T.self, from: data) else { continue }
            rows.append(row)
        }
        return rows
    }

    private func loadJSONL(path: URL, limit: Int) -> [EvidenceLogRow] {
        guard let content = try? String(contentsOf: path, encoding: .utf8) else { return [] }
        let lines = content.split(separator: "\n", omittingEmptySubsequences: true)
        let decoder = JSONDecoder()
        var rows: [EvidenceLogRow] = []
        for line in lines.suffix(limit) {
            guard let data = String(line).data(using: .utf8),
                  let row = try? decoder.decode(EvidenceLogRow.self, from: data) else { continue }
            rows.append(row)
        }
        return rows
    }

    /// Validate repo path: exists, contains scripts/ and artifacts (or key dirs).
    func validateRepoPath(_ path: String) -> (valid: Bool, message: String) {
        let expanded = (path as NSString).expandingTildeInPath
        guard !expanded.isEmpty else { return (false, "Repo path is empty") }
        var isDir: ObjCBool = false
        guard fileManager.fileExists(atPath: expanded, isDirectory: &isDir), isDir.boolValue else {
            return (false, "Path does not exist or is not a directory")
        }
        let url = URL(fileURLWithPath: expanded)
        let scripts = url.appendingPathComponent("scripts")
        let artifacts = url.appendingPathComponent("artifacts")
        guard fileManager.fileExists(atPath: scripts.path) else { return (false, "Missing scripts/ directory") }
        return (true, "OK")
    }

    /// Startup health check per plan: repo path set, dir exists, scripts/ present, artifacts/observability present or creatable, Python 3 resolvable.
    /// Returns (passed, message). Steps 1–4 must pass before tabs are enabled.
    func runStartupHealthCheck(repoPath: String) -> (passed: Bool, message: String) {
        guard !repoPath.isEmpty else { return (false, "Repo path not set.") }
        let expanded = (repoPath as NSString).expandingTildeInPath
        var isDir: ObjCBool = false
        guard fileManager.fileExists(atPath: expanded, isDirectory: &isDir), isDir.boolValue else {
            return (false, "Repo path not found or is not a directory.")
        }
        let url = URL(fileURLWithPath: expanded)
        let scripts = url.appendingPathComponent("scripts")
        guard fileManager.fileExists(atPath: scripts.path) else {
            return (false, "Missing scripts/ directory.")
        }
        let observabilityDir = url.appendingPathComponent("artifacts/observability")
        if !fileManager.fileExists(atPath: observabilityDir.path) {
            do {
                try fileManager.createDirectory(at: observabilityDir, withIntermediateDirectories: true)
            } catch {
                return (false, "artifacts/observability/ missing and could not be created.")
            }
        }
        guard checkPython3Resolvable() else {
            return (false, "Python 3 not found on PATH.")
        }
        return (true, "OK")
    }

    private func checkPython3Resolvable() -> Bool {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        process.arguments = ["python3", "--version"]
        process.standardOutput = FileHandle.nullDevice
        process.standardError = FileHandle.nullDevice
        do {
            try process.run()
            process.waitUntilExit()
            return process.terminationStatus == 0
        } catch {
            return false
        }
    }

    /// Real POLES phase status derived from repo files/runs (not static text).
    struct ObservabilityPhaseStatus {
        var p1Observe: PhaseState   // collector exists, snapshot present
        var p2Document: PhaseState  // evidence_log.jsonl has entries
        var p3ElevateFix: PhaseState // elevated_failures.jsonl + collector auto-fix
        var p4LearnEnhance: PhaseState // weekly trend / baseline learning automation

        enum PhaseState: String {
            case done = "Done"
            case partial = "Partial"
            case notYet = "Not yet"
        }
    }

    func loadObservabilityPhaseStatus(repoPath: String) -> ObservabilityPhaseStatus {
        let base = repoURL(repoPath: repoPath)
        let obsDir = base.appendingPathComponent("artifacts/observability")
        let collectorExists = fileManager.fileExists(atPath: base.appendingPathComponent("scripts/observability/collect_signals.py").path)
        let snapshot = loadLatestSnapshot(repoPath: repoPath)
        let evidenceRows = loadEvidenceLog(repoPath: repoPath, limit: 1)
        let elevatedRows = loadElevatedFailures(repoPath: repoPath, limit: 1)
        let evidenceFileExists = fileManager.fileExists(atPath: obsDir.appendingPathComponent("evidence_log.jsonl").path)
        let elevatedFileExists = fileManager.fileExists(atPath: obsDir.appendingPathComponent("elevated_failures.jsonl").path)
        // P4: no weekly trend / baseline learning automation in repo yet
        let p4AutomationExists = fileManager.fileExists(atPath: base.appendingPathComponent("scripts/observability/weekly_trend_report.py").path)
            || fileManager.fileExists(atPath: base.appendingPathComponent("scripts/observability/baseline_learning.py").path)

        let p1: ObservabilityPhaseStatus.PhaseState = (collectorExists && snapshot != nil) ? .done : (collectorExists ? .partial : .notYet)
        let p2: ObservabilityPhaseStatus.PhaseState = evidenceFileExists ? (evidenceRows.isEmpty ? .partial : .done) : .notYet
        let p3: ObservabilityPhaseStatus.PhaseState = (elevatedFileExists || (snapshot?.failed ?? 0) > 0) ? .partial : (collectorExists ? .partial : .notYet)
        let p4: ObservabilityPhaseStatus.PhaseState = p4AutomationExists ? .partial : .notYet

        return ObservabilityPhaseStatus(p1Observe: p1, p2Document: p2, p3ElevateFix: p3, p4LearnEnhance: p4)
    }
}
