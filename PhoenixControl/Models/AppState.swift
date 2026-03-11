import Foundation
import SwiftUI

final class AppState: ObservableObject {
    @AppStorage("repoPath") var repoPath: String = "" {
        didSet { repoPathValid = nil }
    }
    @Published var lastSnapshot: ObservabilitySnapshot?
    @Published var evidenceLogRows: [EvidenceLogRow] = []
    @Published var elevatedFailures: [EvidenceLogRow] = []
    @Published var observabilityPhaseStatus: ArtifactReader.ObservabilityPhaseStatus?
    /// nil = not run yet, true = pass (tabs enabled), false = block UI with ErrorStateView
    @Published var healthCheckPassed: Bool?
    /// When health check has been run and failed, this is the message to show
    @Published var healthCheckMessage: String?
    /// For toolbar strip: false when repo path invalid after initial pass
    @Published var repoPathValid: Bool?
    @Published var errorMessage: String?
    /// Increment to ask Dashboard/Observability to refresh (e.g. Cmd+R).
    @Published var refreshTrigger: UUID = UUID()
    @Published var workflowRuns: [GitHubService.WorkflowRun] = []
    @Published var productionAlertIssues: [GitHubService.Issue] = []
    @Published var githubStatusMessage: String? // rate-limit, offline, or nil
    /// Set to true from menu command to request Executive Dashboard launch.
    @Published var requestLaunchExecutiveDashboard: Bool = false
}
