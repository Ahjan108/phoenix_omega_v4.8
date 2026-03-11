import SwiftUI

@main
struct PhoenixControlApp: App {
    @StateObject private var state = AppState()
    private let artifactReader = ArtifactReader()
    @StateObject private var scriptRunner = ScriptRunner()
    private let githubService = GitHubService()
    private let dashboardLauncher = ExecutiveDashboardLauncher()

    var body: some Scene {
        WindowGroup {
            ContentView(
                state: state,
                artifactReader: artifactReader,
                scriptRunner: scriptRunner,
                githubService: githubService,
                dashboardLauncher: dashboardLauncher
            )
            .frame(minWidth: 700, minHeight: 500)
        }
        .commands {
            CommandGroup(replacing: .newItem) {}
            CommandGroup(after: .sidebar) {
                Button("Executive Dashboard") { state.requestLaunchExecutiveDashboard = true }
                    .keyboardShortcut("e", modifiers: [.command, .shift])
                Button("Refresh") { state.refreshTrigger = UUID() }
                    .keyboardShortcut("r", modifiers: .command)
            }
        }
    }
}
