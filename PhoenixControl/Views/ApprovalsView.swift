import SwiftUI

/// Approvals tab: required approvals (missing|present|approved|expired); red blocker when not approved.
/// Authority: docs/CONTROL_PLANE_SPEC_PATCH_V1.1.md §2
struct ApprovalsView: View {
    @ObservedObject var state: AppState
    let artifactReader: ArtifactReader
    @State private var approvals: [ApprovalState] = []

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Approvals & compliance")
                    .font(.title2)
                    .foregroundColor(PhoenixColors.phoenixBlue)
                Text("Source: pearl_news/governance/, PEARL_NEWS_GO_NO_GO_CHECKLIST. When any approval is not 'approved', launch actions are blocked.")
                    .font(.caption)
                    .foregroundColor(.secondary)
                ForEach(Array(approvals.enumerated()), id: \.offset) { _, a in
                    HStack(alignment: .top, spacing: 12) {
                        StatusBadge(status: a.status == "approved" ? "pass" : "fail")
                        VStack(alignment: .leading, spacing: 4) {
                            Text(a.name).font(.subheadline)
                            Text("Status: \(a.status)").font(.caption).foregroundColor(.secondary)
                            Text("SOT: \(a.sotPath)").font(.caption2).foregroundColor(.secondary)
                        }
                        Spacer()
                    }
                    .padding(10)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(a.status == "approved" ? PhoenixColors.phoenixCardTint : Color.red.opacity(0.08))
                    .cornerRadius(8)
                }
                if approvals.isEmpty {
                    Text("No approval sources loaded. Set repo path and refresh.")
                        .foregroundColor(.secondary)
                        .padding()
                }
            }
            .padding()
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .background(PhoenixColors.phoenixBackground)
        .onAppear { loadApprovals() }
        .onChange(of: state.refreshTrigger) { _, _ in loadApprovals() }
        .onChange(of: state.repoPath) { _, _ in loadApprovals() }
    }

    private func loadApprovals() {
        guard !state.repoPath.isEmpty else { approvals = []; return }
        let base = artifactReader.repoURL(repoPath: state.repoPath)
        var list: [ApprovalState] = []
        let govDir = base.appendingPathComponent("pearl_news/governance")
        let checklistPath = base.appendingPathComponent("docs/PEARL_NEWS_GO_NO_GO_CHECKLIST.md")
        let fm = FileManager.default
        let requiredFiles = ["GOVERNANCE_PAGE.md", "EDITORIAL_STANDARDS.md", "CORRECTIONS_POLICY.md", "CONFLICT_OF_INTEREST_POLICY.md"]
        var allPresent = true
        for name in requiredFiles {
            let url = govDir.appendingPathComponent(name)
            if !fm.fileExists(atPath: url.path) { allPresent = false; break }
        }
        let checklistExists = fm.fileExists(atPath: checklistPath.path)
        let status: String
        if allPresent && checklistExists {
            status = "approved"
        } else if !fm.fileExists(atPath: govDir.path) {
            status = "missing"
        } else {
            status = checklistExists ? "present" : "missing"
        }
        list.append(ApprovalState(
            id: "pearl_news_church_docs",
            name: "Pearl News church / governance docs",
            sotPath: "pearl_news/governance/ + docs/PEARL_NEWS_GO_NO_GO_CHECKLIST.md",
            status: status
        ))
        approvals = list
    }
}

struct ApprovalState {
    let id: String
    let name: String
    let sotPath: String
    let status: String
}
