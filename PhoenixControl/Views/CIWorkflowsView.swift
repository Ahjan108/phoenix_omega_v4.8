import SwiftUI

struct CIWorkflowsView: View {
    @ObservedObject var state: AppState
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("CI / Workflows")
                .font(.title2)
                .foregroundColor(PhoenixColors.phoenixBlue)
            Text("Core tests, Release gates, Teacher gates, Brand guards, Pearl News gates, Production observability, Production alerts, Simulation 10k")
                .foregroundColor(.secondary)
            Text("Open GitHub Actions for run status and production-alert issues.")
                .foregroundColor(.secondary)
            if !state.repoPath.isEmpty {
                Link("Open GitHub Actions", destination: URL(string: "https://github.com")!)
                    .padding(.top, 8)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixBackground)
    }
}
