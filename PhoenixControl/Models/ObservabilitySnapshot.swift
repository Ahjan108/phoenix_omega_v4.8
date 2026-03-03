import Foundation

struct ObservabilitySnapshot: Codable {
    let timestamp: String
    let signals: [SignalResult]
    let passed: Int
    let failed: Int
    let skipped: Int
}

struct SignalResult: Codable {
    let signal_id: String
    let category: String?
    let timestamp: String?
    let status: String
    let exit_code: Int?
    let message: String?
    let stdout_tail: String?
    let stderr_tail: String?
}

struct EvidenceLogRow: Codable {
    let timestamp: String?
    let signal_id: String?
    let category: String?
    let status: String?
    let exit_code: Int?
    let message: String?
    let stdout_tail: String?
    let stderr_tail: String?
}

/// Wrapper so we can use EvidenceLogRow in SwiftUI Table (Identifiable).
struct IdentifiableEvidenceRow: Identifiable {
    let id: Int
    let row: EvidenceLogRow
}
