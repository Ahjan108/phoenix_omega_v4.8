import SwiftUI

/// Reusable error state per PHOENIX_OMEGA_ERROR_STATE_UX_SPEC: severity, title, message, suggestion, primary/secondary actions.
struct ErrorStateView: View {
    enum Severity {
        case critical  // red, blocks action
        case warning   // orange
        case info      // blue
        case empty     // gray, neutral
    }

    let severity: Severity
    let title: String
    let message: String
    let suggestion: String
    var primaryAction: (title: String, action: () -> Void)? = nil
    var secondaryAction: (title: String, action: () -> Void)? = nil

    private var accentColor: Color {
        switch severity {
        case .critical: return .red
        case .warning: return .orange
        case .info: return PhoenixColors.phoenixBlue
        case .empty: return .gray
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(title)
                .font(.headline)
                .foregroundColor(accentColor)
            Text(message)
                .font(.subheadline)
                .foregroundColor(.secondary)
            Text(suggestion)
                .font(.subheadline)
                .foregroundColor(.primary)
            HStack(spacing: 12) {
                if let primary = primaryAction {
                    Button(primary.title, action: primary.action)
                        .buttonStyle(.borderedProminent)
                        .tint(accentColor)
                }
                if let secondary = secondaryAction {
                    Button(secondary.title, action: secondary.action)
                }
            }
        }
        .padding(24)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(PhoenixColors.phoenixBackground)
    }
}

/// Persistent strip below toolbar for app-wide issues (e.g. repo path invalid). Dismisses only when resolved.
struct ToolbarErrorStrip: View {
    let message: String
    let openSettings: () -> Void

    var body: some View {
        HStack {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundColor(.orange)
            Text(message)
                .font(.subheadline)
                .foregroundColor(.primary)
            Spacer()
            Button("Open Settings", action: openSettings)
        }
        .padding(.horizontal, 16)
        .frame(height: 36)
        .frame(maxWidth: .infinity)
        .background(Color.orange.opacity(0.15))
    }
}
