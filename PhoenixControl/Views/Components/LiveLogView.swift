import SwiftUI

struct LiveLogView: View {
    @Binding var logText: String
    var isRunning: Bool
    /// When non-nil and >= 1, show "Exited with code N" header (error state UX spec).
    var exitCode: Int32? = nil

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            if let code = exitCode, code != 0 {
                HStack {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.red)
                    Text("Exited with code \(code)")
                        .font(.subheadline)
                        .foregroundColor(.red)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(8)
                .background(Color.red.opacity(0.1))
            }
            ScrollViewReader { proxy in
                ScrollView(.vertical, showsIndicators: true) {
                    Text(logText)
                        .font(.system(.body, design: .monospaced))
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .textSelection(.enabled)
                        .id("bottom")
                }
                .onChange(of: logText) { _ in
                    withAnimation { proxy.scrollTo("bottom", anchor: .bottom) }
                }
            }
        }
        .frame(minHeight: 120)
        .padding(8)
        .background(Color(white: 0.96))
        .overlay(
            RoundedRectangle(cornerRadius: 6)
                .stroke(PhoenixColors.phoenixBlue.opacity(0.3), lineWidth: 1)
        )
        .overlay(alignment: .topTrailing) {
            if isRunning {
                ProgressView()
                    .scaleEffect(0.7)
                    .padding(8)
            }
        }
    }
}
