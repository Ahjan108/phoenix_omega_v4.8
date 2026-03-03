import SwiftUI

struct StatusBadge: View {
    let status: String

    var color: Color {
        switch status.lowercased() {
        case "pass": return .green
        case "fail": return .red
        case "skip", "passive": return .gray
        default: return .orange
        }
    }

    var icon: String {
        switch status.lowercased() {
        case "pass": return "checkmark.circle.fill"
        case "fail": return "xmark.circle.fill"
        case "skip", "passive": return "minus.circle.fill"
        default: return "questionmark.circle.fill"
        }
    }

    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: icon)
                .foregroundColor(color)
            Text(status)
                .font(.caption)
                .foregroundColor(color)
        }
    }
}
