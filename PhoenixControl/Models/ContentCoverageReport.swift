import Foundation

/// From artifacts/content_coverage_report.json
struct ContentCoverageReport: Codable {
    let story_coverage_ok: Bool?
    let story_message: String?
    let non_story_coverage_ok: Bool?
    let non_story_message: String?
    let plan_coverage_ok: Bool?
    let plan_coverage_errors: [String]?
    let teacher_readiness: [String: TeacherReadinessDetail]?
    let teachers_failed: [String]?
    let summary_ok: Bool?
}

struct TeacherReadinessDetail: Codable {
    let ok: Bool?
    let detail: String?
}
