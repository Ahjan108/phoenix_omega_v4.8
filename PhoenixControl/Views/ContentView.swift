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
    case completeness
    case approvals
    case systemMetadata
    case agentsLearning
    case manualReview
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
        case .completeness: return "Completeness"
        case .approvals: return "Approvals"
        case .systemMetadata: return "System Metadata"
        case .agentsLearning: return "Agents & Learning"
        case .manualReview: return "Manual Review"
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
        case .completeness: return "chart.pie"
        case .approvals: return "checkmark.seal"
        case .systemMetadata: return "list.bullet.rectangle"
        case .agentsLearning: return "brain.head.profile"
        case .manualReview: return "exclamationmark.triangle.fill"
        }
    }
}

struct ContentView: View {
    @ObservedObject var state: AppState
    let artifactReader: ArtifactReader
    let scriptRunner: ScriptRunner
    let githubService: GitHubService
    let dashboardLauncher: ExecutiveDashboardLauncher
    @State private var selectedTab: TabTag = .dashboard
    @State private var showingPathSheet = false
    @State private var pathInput: String = ""
    @State private var dashboardLaunchError: String?
    @State private var isLaunchingDashboard = false

    private var startupBlocked: Bool {
        guard let passed = state.healthCheckPassed else { return true }
        return !passed
    }

    var body: some View {
        Group {
            if startupBlocked {
                ErrorStateView(
                    severity: .critical,
                    title: "Repo path not set or invalid.",
                    message: state.healthCheckMessage ?? "The app could not validate the repo path, scripts directory, artifacts/observability, or Python 3.",
                    suggestion: "Open Settings and set a valid repo root path that contains scripts/ and where artifacts/observability can exist. Ensure Python 3 is on PATH.",
                    primaryAction: ("Open Settings", { pathInput = state.repoPath; showingPathSheet = true }),
                    secondaryAction: nil
                )
            } else {
                mainContent
            }
        }
        .onAppear { runStartupHealthCheckIfNeeded() }
        .onChange(of: state.repoPath) { _, _ in runStartupHealthCheckIfNeeded() }
        .sheet(isPresented: $showingPathSheet) {
            pathSheet
        }
        .onChange(of: pathInput) { _, _ in
            if !showingPathSheet { return }
            let (valid, _) = artifactReader.validateRepoPath(pathInput)
            state.repoPathValid = valid
        }
        .onChange(of: showingPathSheet) { _, visible in
            if !visible { runStartupHealthCheckIfNeeded() }
        }
        .alert("Error", isPresented: Binding(
            get: { state.errorMessage != nil },
            set: { if !$0 { state.errorMessage = nil } }
        )) {
            Button("OK") { state.errorMessage = nil }
        } message: {
            if let msg = state.errorMessage {
                Text(msg)
            }
        }
    }

    private var mainContent: some View {
        VStack(spacing: 0) {
            if state.repoPathValid == false {
                ToolbarErrorStrip(message: "Repo path is invalid. Update it in Settings.", openSettings: {
                    pathInput = state.repoPath
                    showingPathSheet = true
                })
            }
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
                        Button(action: launchExecutiveDashboard) {
                            Label("Executive Dashboard", systemImage: "chart.bar.doc.horizontal")
                        }
                        .disabled(state.repoPath.isEmpty || isLaunchingDashboard)
                        .help("Launch Streamlit Executive Dashboard and open in browser")
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
            .alert("Executive Dashboard", isPresented: Binding(
                get: { dashboardLaunchError != nil },
                set: { if !$0 { dashboardLaunchError = nil } }
            )) {
                Button("OK") { dashboardLaunchError = nil }
            } message: {
                if let msg = dashboardLaunchError {
                    Text(msg)
                }
            }
        }
    }
    .commands {
        CommandGroup(after: .sidebar) {
            Button("Executive Dashboard") { launchExecutiveDashboard() }
                .keyboardShortcut("e", modifiers: [.command, .shift])
            ForEach(Array(TabTag.allCases.enumerated()), id: \.element) { index, tab in
                Button(tab.title) { selectedTab = tab }
                    .keyboardShortcut(KeyEquivalent(Character(Unicode.Scalar(48 + (index == 9 ? 0 : index + 1))!)), modifiers: .command)
            }
            Button("Refresh") { runStartupHealthCheckIfNeeded(); refreshCurrentTab() }
                .keyboardShortcut("r", modifiers: .command)
        }
    }

    private var detailContent: some View {
        Group {
            switch selectedTab {
            case .dashboard:
                DashboardView(state: state, artifactReader: artifactReader, scriptRunner: scriptRunner, onSelectObservability: { selectedTab = .observability }, onGovernanceRan: { runStartupHealthCheckIfNeeded(); refreshCurrentTab() })
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
                CIWorkflowsView(state: state, githubService: githubService)
            case .docs:
                DocsConfigView(state: state, artifactReader: artifactReader, scriptRunner: scriptRunner)
            case .completeness:
                CompletenessView(state: state, scriptRunner: scriptRunner)
            case .approvals:
                ApprovalsView(state: state, artifactReader: artifactReader)
            case .systemMetadata:
                SystemMetadataView(state: state, artifactReader: artifactReader, scriptRunner: scriptRunner)
            case .agentsLearning:
                AgentsLearningView(state: state, githubService: githubService)
            case .manualReview:
                ManualReviewView(state: state, artifactReader: artifactReader, scriptRunner: scriptRunner)
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

    private func runStartupHealthCheckIfNeeded() {
        if state.repoPath.isEmpty {
            state.healthCheckPassed = false
            state.healthCheckMessage = "Repo path not set."
            state.repoPathValid = false
            return
        }
        let (passed, message) = artifactReader.runStartupHealthCheck(repoPath: state.repoPath)
        state.healthCheckPassed = passed
        state.healthCheckMessage = passed ? nil : message
        state.repoPathValid = passed
    }

    private func refreshCurrentTab() {
        state.refreshTrigger = UUID()
    }

    private func abbreviatedPath(_ path: String) -> String {
        let expanded = (path as NSString).expandingTildeInPath
        let home = FileManager.default.homeDirectoryForCurrentUser.path
        if expanded.hasPrefix(home) {
            return "~" + String(expanded.dropFirst(home.count))
        }
        return path
    }

    private func launchExecutiveDashboard() {
        guard !state.repoPath.isEmpty else { return }
        isLaunchingDashboard = true
        dashboardLauncher.launch(repoPath: state.repoPath) { result in
            DispatchQueue.main.async {
                isLaunchingDashboard = false
                switch result {
                case .success:
                    break
                case .failure(let message):
                    dashboardLaunchError = message
                }
            }
        }
    }
}
