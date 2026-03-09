import Foundation
import Combine

/// Runs repo scripts with cwd and PYTHONPATH set. Streams stdout/stderr to callback.
final class ScriptRunner: ObservableObject {
    private var process: Process?
    private var outputPipe: Pipe?
    private var errorPipe: Pipe?
    private var cancellables = Set<AnyCancellable>()

    /// Special script path: run pytest with given args (e.g. ["-m", "not slow"]).
    static let pytestScriptPath = "__pytest__"

    /// Allowed script paths relative to repo root (allowlist for safety).
    static let allowedScripts: Set<String> = [
        "scripts/run_pipeline.py",
        "scripts/render_plan_to_txt.py",
        "scripts/run_production_readiness_gates.py",
        "scripts/observability/collect_signals.py",
        "scripts/ci/run_simulation_10k.py",
        "scripts/ci/analyze_pearl_prime_sim.py",
        "scripts/ci/run_prepublish_gates.py",
        "scripts/ci/run_rigorous_system_test.py",
        "scripts/ci/run_canary_100_books.py",
        "scripts/ci/run_teacher_production_gates.py",
        "scripts/ci/check_docs_governance.py",
        "scripts/ci/check_system_governance_status.py",
        "scripts/book_script_content_validation.py",
        "scripts/systems_test/run_systems_test.py",
        "scripts/ml_loop/run_continuous_loop.py",
        "scripts/ml_loop/run_daily_promotion.py",
        "scripts/ml_loop/run_weekly_market_recalibration.py",
        "pearl_news/pipeline/run_article_pipeline.py",
    ]

    /// Allowed executable for running Python scripts.
    static var pythonPath: String { "python3" }

    enum RunError: Error {
        case invalidRepoPath
        case scriptNotAllowed(String)
        case scriptNotFound(String)
        case launchFailed(Error)
        case timeout
        case cancelled
    }

    /// Run a script. scriptPath is relative to repo root (e.g. "scripts/observability/collect_signals.py").
    /// - Parameters:
    ///   - scriptPath: path relative to repo root
    ///   - arguments: e.g. ["--signals", "gate_production_readiness", "--out", "artifacts/observability/signal_snapshot.json"]
    ///   - timeoutSeconds: nil = no timeout
    ///   - onOutput: called with stdout/stderr lines (redacted if secrets present)
    /// - Returns: exit code (or throws)
    func run(
        repoPath: String,
        scriptPath: String,
        arguments: [String] = [],
        timeoutSeconds: Int? = 300,
        onOutput: @escaping (String) -> Void
    ) async throws -> Int32 {
        let repoURL = URL(fileURLWithPath: (repoPath as NSString).expandingTildeInPath)
        guard repoURL.pathExtension.isEmpty else { throw RunError.invalidRepoPath }

        let executable: String
        let processArgs: [String]
        if scriptPath == Self.pytestScriptPath {
            executable = Self.pythonPath
            processArgs = ["-m", "pytest"] + arguments
        } else {
            let scriptURL = repoURL.appendingPathComponent(scriptPath)
            let relative = (scriptPath as NSString).standardizingPath
            guard Self.allowedScripts.contains(relative) || Self.allowedScripts.contains(scriptPath) else {
                throw RunError.scriptNotAllowed(scriptPath)
            }
            guard FileManager.default.fileExists(atPath: scriptURL.path) else {
                throw RunError.scriptNotFound(scriptURL.path)
            }
            executable = Self.pythonPath
            processArgs = [scriptURL.path] + arguments
        }

        return try await withCheckedThrowingContinuation { continuation in
            DispatchQueue.global(qos: .userInitiated).async { [weak self] in
                guard let self = self else { return }
                let process = Process()
                process.executableURL = URL(fileURLWithPath: executable)
                process.arguments = processArgs
                process.currentDirectoryURL = repoURL
                var env = ProcessInfo.processInfo.environment
                env["PYTHONPATH"] = repoURL.path
                process.environment = env

                let outPipe = Pipe()
                let errPipe = Pipe()
                process.standardOutput = outPipe
                process.standardError = errPipe
                self.process = process
                self.outputPipe = outPipe
                self.errorPipe = errPipe

                outPipe.fileHandleForReading.readabilityHandler = { handle in
                    let data = handle.availableData
                    guard !data.isEmpty else { return }
                    if let line = String(data: data, encoding: .utf8) {
                        DispatchQueue.main.async { onOutput(Self.redactSecrets(line)) }
                    }
                }
                errPipe.fileHandleForReading.readabilityHandler = { handle in
                    let data = handle.availableData
                    guard !data.isEmpty else { return }
                    if let line = String(data: data, encoding: .utf8) {
                        DispatchQueue.main.async { onOutput(Self.redactSecrets(line)) }
                    }
                }

                do {
                    try process.run()
                } catch {
                    continuation.resume(throwing: RunError.launchFailed(error))
                    return
                }

                if let timeout = timeoutSeconds, timeout > 0 {
                    DispatchQueue.global().asyncAfter(deadline: .now() + .seconds(Double(timeout))) {
                        if process.isRunning {
                            process.terminate()
                            continuation.resume(throwing: RunError.timeout)
                            return
                        }
                    }
                }

                process.waitUntilExit()
                outPipe.fileHandleForReading.readabilityHandler = nil
                errPipe.fileHandleForReading.readabilityHandler = nil
                self.process = nil
                continuation.resume(returning: process.terminationStatus)
            }
        }
    }

    func cancel() {
        process?.terminate()
    }

    /// Redact common secret patterns from log lines (no secrets in UI).
    static func redactSecrets(_ text: String) -> String {
        var out = text
        // Redact token=, password=, secret= style
        let patterns = [
            #"(?i)(token|password|secret|api_key|apikey)\s*[:=]\s*[\w\-\.]+"#,
            #"ghp_[a-zA-Z0-9]{36}"#,
            #"xoxb-[a-zA-Z0-9\-]+"#,
        ]
        for p in patterns {
            if let regex = try? NSRegularExpression(pattern: p) {
                let range = NSRange(out.startIndex..., in: out)
                out = regex.stringByReplacingMatches(in: out, range: range, withTemplate: "$1=[REDACTED]")
            }
        }
        return out
    }
}
