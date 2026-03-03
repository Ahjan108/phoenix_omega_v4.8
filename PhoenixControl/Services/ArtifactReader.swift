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
}
