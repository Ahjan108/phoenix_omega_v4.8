import SwiftUI

struct LiveLogView: View {
    @Binding var logText: String
    var isRunning: Bool

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView(.vertical, showsIndicators: true) {
                Text(logText)
                    .font(.system(.body, design: .monospaced))
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .textSelection(.enabled)
                    .id("bottom")
            }
            .onChange(of: logText) { _, _ in
                withAnimation { proxy.scrollTo("bottom", anchor: .bottom) }
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
