import Foundation

/// GitHub API for workflow runs and production-alert issues. Token stored in Keychain only.
final class GitHubService {
    static let keychainService = "com.phoenixomega.control"
    static let tokenAccount = "github_token"

    var repoOwner: String = ""
    var repoName: String = ""

    enum GitHubError: Error {
        case noToken
        case rateLimited(retryAfterSeconds: Int?)
        case offline
        case invalidResponse(statusCode: Int)
    }

    func setToken(_ token: String) -> Bool {
        guard let data = token.data(using: .utf8) else { return false }
        deleteToken()
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: Self.keychainService,
            kSecAttrAccount as String: Self.tokenAccount,
            kSecValueData as String: data,
        ]
        return SecItemAdd(query as CFDictionary, nil) == errSecSuccess
    }

    func hasToken() -> Bool {
        getToken() != nil
    }

    func removeToken() {
        deleteToken()
    }

    private func getToken() -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: Self.keychainService,
            kSecAttrAccount as String: Self.tokenAccount,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne,
        ]
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        guard status == errSecSuccess, let data = result as? Data, let token = String(data: data, encoding: .utf8) else { return nil }
        return token
    }

    private func deleteToken() {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: Self.keychainService,
            kSecAttrAccount as String: Self.tokenAccount,
        ]
        SecItemDelete(query as CFDictionary)
    }

    struct WorkflowRun: Identifiable {
        let id: Int
        let name: String
        let conclusion: String
        let htmlUrl: String
    }

    struct Issue: Identifiable {
        let id: Int
        let title: String
        let url: String
    }

    func fetchWorkflowRuns(limit: Int = 10) async throws -> [WorkflowRun] {
        guard let token = getToken(), !token.isEmpty else { throw GitHubError.noToken }
        guard !repoOwner.isEmpty, !repoName.isEmpty else { return [] }
        let url = URL(string: "https://api.github.com/repos/\(repoOwner)/\(repoName)/actions/runs?per_page=\(limit)")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/vnd.github+json", forHTTPHeaderField: "Accept")
        request.setValue("2022-11-28", forHTTPHeaderField: "X-GitHub-Api-Version")
        let (data, response): (Data, URLResponse)
        do {
            (data, response) = try await URLSession.shared.data(for: request)
        } catch {
            if (error as NSError).code == NSURLErrorNotConnectedToInternet || (error as NSError).code == NSURLErrorNetworkConnectionLost {
                throw GitHubError.offline
            }
            throw error
        }
        guard let http = response as? HTTPURLResponse else { throw GitHubError.invalidResponse(statusCode: 0) }
        if http.statusCode == 403 {
            let retryAfter = http.value(forHTTPHeaderField: "Retry-After").flatMap(Int.init)
            throw GitHubError.rateLimited(retryAfterSeconds: retryAfter)
        }
        if http.statusCode != 200 { throw GitHubError.invalidResponse(statusCode: http.statusCode) }
        struct RunsResponse: Decodable {
            let workflow_runs: [RunEntry]?
            struct RunEntry: Decodable {
                let id: Int
                let name: String?
                let conclusion: String?
                let html_url: String?
            }
        }
        let decoded = try JSONDecoder().decode(RunsResponse.self, from: data)
        return (decoded.workflow_runs ?? []).prefix(limit).map { r in
            WorkflowRun(
                id: r.id,
                name: r.name ?? "Workflow",
                conclusion: r.conclusion ?? "unknown",
                htmlUrl: r.html_url ?? "https://github.com/\(repoOwner)/\(repoName)/actions"
            )
        }
    }

    func fetchProductionAlertIssues(limit: Int = 10) async throws -> [Issue] {
        guard let token = getToken(), !token.isEmpty else { throw GitHubError.noToken }
        guard !repoOwner.isEmpty, !repoName.isEmpty else { return [] }
        let encoded = "repo:\(repoOwner)/\(repoName) label:production-alert is:open".addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? ""
        let url = URL(string: "https://api.github.com/search/issues?q=\(encoded)&per_page=\(limit)")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/vnd.github+json", forHTTPHeaderField: "Accept")
        request.setValue("2022-11-28", forHTTPHeaderField: "X-GitHub-Api-Version")
        let (data, response): (Data, URLResponse)
        do {
            (data, response) = try await URLSession.shared.data(for: request)
        } catch {
            if (error as NSError).code == NSURLErrorNotConnectedToInternet || (error as NSError).code == NSURLErrorNetworkConnectionLost {
                throw GitHubError.offline
            }
            throw error
        }
        guard let http = response as? HTTPURLResponse else { throw GitHubError.invalidResponse(statusCode: 0) }
        if http.statusCode == 403 {
            let retryAfter = http.value(forHTTPHeaderField: "Retry-After").flatMap(Int.init)
            throw GitHubError.rateLimited(retryAfterSeconds: retryAfter)
        }
        if http.statusCode != 200 { throw GitHubError.invalidResponse(statusCode: http.statusCode) }
        struct SearchResponse: Decodable {
            let items: [IssueEntry]?
            struct IssueEntry: Decodable {
                let id: Int
                let title: String?
                let html_url: String?
            }
        }
        let decoded = try JSONDecoder().decode(SearchResponse.self, from: data)
        return (decoded.items ?? []).prefix(limit).map { i in
            Issue(
                id: i.id,
                title: i.title ?? "Issue",
                url: i.html_url ?? "https://github.com/\(repoOwner)/\(repoName)/issues"
            )
        }
    }
}
