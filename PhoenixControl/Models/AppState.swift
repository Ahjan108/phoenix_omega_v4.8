import Foundation
import SwiftUI

final class AppState: ObservableObject {
    @AppStorage("repoPath") var repoPath: String = ""
    @Published var lastSnapshot: ObservabilitySnapshot?
    @Published var evidenceLogRows: [EvidenceLogRow] = []
    @Published var elevatedFailures: [EvidenceLogRow] = []
    @Published var healthCheckPassed: Bool?
    @Published var errorMessage: String?
}
