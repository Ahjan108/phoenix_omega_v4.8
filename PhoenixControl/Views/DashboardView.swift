import SwiftUI

struct DashboardView: View {
    @ObservedObject var state: AppState
    let artifactReader: ArtifactReader

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                if state.repoPath.isEmpty {
                    Text("Set repo path in Settings (or toolbar) to see status.")
                        .foregroundColor(.secondary)
                        .padding()
                } else {
                    observabilityCard
                    evidenceCard
                    elevatedCard
                    branchProtectionCard
                }
            }
            .padding()
        }
        .background(PhoenixColors.phoenixBackground)
        .onAppear { refresh() }
    }

    private var observabilityCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Observability (POLES)")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            if let snap = state.lastSnapshot {
                HStack(spacing: 16) {
                    StatusBadge(status: "pass")
                    Text("\(snap.passed)")
                    StatusBadge(status: "fail")
                    Text("\(snap.failed)")
                    StatusBadge(status: "skip")
                    Text("\(snap.skipped)")
                }
                Text("Last: \(snap.timestamp)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            } else {
                Text("No snapshot yet. Run Collect signals in Observability tab.")
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private var evidenceCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Evidence log")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            if state.evidenceLogRows.isEmpty {
                Text("No evidence log entries. Run collector in Observability tab.")
                    .foregroundColor(.secondary)
            } else {
                Text("Last \(state.evidenceLogRows.count) entries. See Observability tab for full table.")
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private var elevatedCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Elevated failures")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            Text("\(state.elevatedFailures.count) failure(s) in elevated_failures.jsonl")
                .foregroundColor(state.elevatedFailures.isEmpty ? .secondary : .red)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private var branchProtectionCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Branch protection")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            Text("1. Settings → Branches → main: require Core tests")
            Text("2. Notifications: Email for Actions failures")
            Text("3. Watch repo: Custom → Actions")
            Text("4. Keep Production observability scheduled")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private func refresh() {
        guard !state.repoPath.isEmpty else { return }
        state.lastSnapshot = artifactReader.loadLatestSnapshot(repoPath: state.repoPath)
        state.evidenceLogRows = artifactReader.loadEvidenceLog(repoPath: state.repoPath, limit: 20)
        state.elevatedFailures = artifactReader.loadElevatedFailures(repoPath: state.repoPath, limit: 50)
    }
}
