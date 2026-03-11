import Foundation
import AppKit

/// Launches the Streamlit Executive Dashboard with REPO_PATH and opens the browser.
/// Authority: docs/EXECUTIVE_DASHBOARD_AND_PHOENIXCONTROL_SPEC.md
final class ExecutiveDashboardLauncher {
    static let dashboardPort = 8501
    static let dashboardURL = URL(string: "http://localhost:\(dashboardPort)")!

    enum LaunchError: Error {
        case message(String)
    }

    private var process: Process?

    /// Launch streamlit run dashboard.py with REPO_PATH; open browser on success; on failure return error.
    func launch(repoPath: String, completion: @escaping (Result<Void, LaunchError>) -> Void) {
        let expanded = (repoPath as NSString).expandingTildeInPath
        guard !expanded.isEmpty else {
            completion(.failure(.message("Repo path is empty.")))
            return
        }
        var isDir: ObjCBool = false
        guard FileManager.default.fileExists(atPath: expanded, isDirectory: &isDir), isDir.boolValue else {
            completion(.failure(.message("Repo path does not exist or is not a directory.")))
            return
        }
        let repoURL = URL(fileURLWithPath: expanded)
        let dashboardPy = repoURL.appendingPathComponent("dashboard.py")
        guard FileManager.default.fileExists(atPath: dashboardPy.path) else {
            completion(.failure(.message("dashboard.py not found at repo root. Expected: \(dashboardPy.path)")))
            return
        }

        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        process.arguments = [
            "python3", "-m", "streamlit", "run",
            dashboardPy.path,
            "--server.headless", "true",
            "--server.port", "\(Self.dashboardPort)"
        ]
        process.currentDirectoryURL = repoURL
        var env = ProcessInfo.processInfo.environment
        env["REPO_PATH"] = expanded
        process.environment = env
        process.standardOutput = FileHandle.nullDevice
        process.standardError = FileHandle.nullDevice

        do {
            try process.run()
            self.process = process
            // Give streamlit a moment to bind
            DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) { [weak self] in
                if process.isRunning {
                    NSWorkspace.shared.open(Self.dashboardURL)
                    completion(.success(()))
                } else {
                    self?.process = nil
                    completion(.failure(.message("Executive Dashboard process exited before opening. Check that streamlit is installed: pip install streamlit")))
                }
            }
        } catch {
            completion(.failure(.message("Failed to start Executive Dashboard: \(error.localizedDescription). Ensure streamlit is installed: pip install -r requirements-dashboard.txt")))
        }
    }

    /// Open the dashboard URL in browser (e.g. if already running).
    func openInBrowser() {
        NSWorkspace.shared.open(Self.dashboardURL)
    }
}
