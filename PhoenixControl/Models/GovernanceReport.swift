import Foundation

/// From artifacts/governance/system_governance_report.json
struct SystemGovernanceReport: Codable {
    let timestamp: String?
    let repo_root: String?
    let fix_applied: Bool?
    let checks: [GovernanceCheck]?
    let summary: GovernanceSummary?
}

struct GovernanceCheck: Codable {
    let slug: String?
    let name: String?
    let passed: Bool?
    let detail: String?
    let fix_applied: Bool?
    let output: String?
}

struct GovernanceSummary: Codable {
    let total: Int?
    let passed: Int?
    let failed: Int?
    let fixes_applied: Int?
}
