import SwiftUI

enum TabTag: String, CaseIterable, Identifiable {
    case dashboard
    case pipeline
    case simulation
    case tests
    case observability
    case gates
    case pearlNews
    case teacher
    case ci
    case docs
    var id: String { rawValue }
    var title: String {
        switch self {
        case .dashboard: return "Dashboard"
        case .pipeline: return "Pipeline"
        case .simulation: return "Simulation"
        case .tests: return "Tests"
        case .observability: return "Observability"
        case .gates: return "Gates & Release"
        case .pearlNews: return "Pearl News"
        case .teacher: return "Teacher"
        case .ci: return "CI / Workflows"
        case .docs: return "Docs & Config"
        }
    }
    var systemImage: String {
        switch self {
        case .dashboard: return "gauge.medium"
        case .pipeline: return "book"
        case .simulation: return "chart.bar"
        case .tests: return "checkmark.circle"
        case .observability: return "waveform.path.ecg"
        case .gates: return "lock.shield"
        case .pearlNews: return "newspaper"
        case .teacher: return "person.crop.circle"
        case .ci: return "arrow.triangle.2.circlepath"
        case .docs: return "doc.text"
        }
    }
}

struct ContentView: View {
    @ObservedObject var state: AppState
    let artifactReader: ArtifactReader
    let scriptRunner: ScriptRunner
    @State private var selectedTab: TabTag = .dashboard
    @State private var showingPathSheet = false
    @State private var pathInput: String = ""

    var body: some View {
        NavigationSplitView {
            List(TabTag.allCases, selection: $selectedTab) { tab in
                Label(tab.title, systemImage: tab.systemImage)
                    .tag(tab)
            }
            .listStyle(.sidebar)
            .navigationSplitViewColumnWidth(min: 180, ideal: 200)
        } detail: {
            detailContent
                .frame(minWidth: 500, minHeight: 400)
        }
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                HStack(spacing: 8) {
                    Text(state.repoPath.isEmpty ? "Set repo path" : abbreviatedPath(state.repoPath))
                        .lineLimit(1)
                        .truncationMode(.middle)
                        .foregroundColor(state.repoPath.isEmpty ? .red : .primary)
                    Button(action: { pathInput = state.repoPath; showingPathSheet = true }) {
                        Image(systemName: "folder")
                    }
                }
            }
        }
        .sheet(isPresented: $showingPathSheet) {
            pathSheet
        }
    }

    private var detailContent: some View {
        Group {
            switch selectedTab {
            case .dashboard:
                DashboardView(state: state, artifactReader: artifactReader)
            case .pipeline:
                PipelineView(state: state, scriptRunner: scriptRunner)
            case .simulation:
                SimulationView(state: state, scriptRunner: scriptRunner)
            case .tests:
                TestsView(state: state, scriptRunner: scriptRunner)
            case .observability:
                ObservabilityView(state: state, artifactReader: artifactReader, scriptRunner: scriptRunner)
            case .gates:
                GatesReleaseView(state: state, scriptRunner: scriptRunner)
            case .pearlNews:
                PearlNewsView(state: state, scriptRunner: scriptRunner)
            case .teacher:
                TeacherView(state: state, scriptRunner: scriptRunner)
            case .ci:
                CIWorkflowsView(state: state)
            case .docs:
                DocsConfigView(state: state, scriptRunner: scriptRunner)
            }
        }
    }

    private var pathSheet: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Repo path")
                .font(.headline)
            TextField("e.g. /Users/you/phoenix_omega", text: $pathInput)
                .textFieldStyle(.roundedBorder)
            if !pathInput.isEmpty {
                let result = artifactReader.validateRepoPath(pathInput)
                Text(result.message)
                    .font(.caption)
                    .foregroundColor(result.valid ? .green : .red)
            }
            HStack {
                Button("Cancel") { showingPathSheet = false }
                Button("Set") {
                    state.repoPath = pathInput
                    showingPathSheet = false
                }
                .disabled(pathInput.isEmpty)
            }
            .padding(.top, 8)
        }
        .padding(24)
        .frame(width: 420)
    }

    private func abbreviatedPath(_ path: String) -> String {
        let expanded = (path as NSString).expandingTildeInPath
        let home = FileManager.default.homeDirectoryForCurrentUser.path
        if expanded.hasPrefix(home) {
            return "~" + String(expanded.dropFirst(home.count))
        }
        return path
    }
}
