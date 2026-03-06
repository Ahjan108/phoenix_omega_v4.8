import SwiftUI

/// Shared evidence log table per plan: displays rows with timestamp, signal, category, status, message.
struct EvidenceLogTable: View {
    let title: String
    let rows: [IdentifiableEvidenceRow]
    var highlightFailure: Bool = false

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.headline)
                .foregroundColor(highlightFailure ? .red : .primary)
            if rows.isEmpty {
                Text("No entries.")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .padding(8)
            } else {
                Table(rows) {
                    TableColumn("Time") { item in Text(item.row.timestamp ?? "-") }
                    TableColumn("Signal") { item in Text(item.row.signal_id ?? "-") }
                    TableColumn("Category") { item in Text(item.row.category ?? "-") }
                    TableColumn("Status") { item in StatusBadge(status: item.row.status ?? "?") }
                    TableColumn("Message") { item in Text(item.row.message ?? "-").lineLimit(highlightFailure ? 2 : 1) }
                }
            }
        }
    }
}
