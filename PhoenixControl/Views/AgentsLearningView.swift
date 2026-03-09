import SwiftUI

/// Agents & Learning tab: recent agent PRs, test impact, learned signals. Data sources TBD.
/// Authority: docs/CONTROL_PLANE_SPEC_PATCH_V1.1.md §4
struct AgentsLearningView: View {
    @ObservedObject var state: AppState
    let githubService: GitHubService

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Agents & learning")
                    .font(.title2)
                    .foregroundColor(PhoenixColors.phoenixBlue)
                Text("Visibility into recent agent PRs, what changed, test impact, learned signals. Data sources: workflow artifacts, PR metadata, EI reports (paths TBD).")
                    .font(.caption)
                    .foregroundColor(.secondary)
                VStack(alignment: .leading, spacing: 8) {
                    Text("Placeholder")
                        .font(.headline)
                    Text("Data contract: GitHub API (PRs, files); optional artifacts/ei_v2/, artifacts/learning/. Refresh: on load / manual; rate-limit aware.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    if !state.workflowRuns.isEmpty {
                        Text("Recent workflow runs: \(state.workflowRuns.count)")
                            .font(.subheadline)
                        ForEach(state.workflowRuns.prefix(5), id: \.id) { run in
                            HStack(spacing: 8) {
                                StatusBadge(status: run.conclusion == "success" ? "pass" : "fail")
                                Text(run.name ?? "?")
                                Text(run.name)
                                    .lineLimit(1)
                                    .truncationMode(.tail)
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
            .padding()
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .background(PhoenixColors.phoenixBackground)
    }
}
