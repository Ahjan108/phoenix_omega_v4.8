import SwiftUI

// MARK: - Pipeline options (from list_pipeline_options.py JSON)
struct PipelineOptionsResponse: Codable {
    var arcs: [ArcOption]?
    var angles: [AngleOption]?
    var topics: [String]?
    var personas: [String]?
    var output_formats: [FormatOption]?
    var structural_formats: [String]?
    var runtime_formats: [String]?
}

struct ArcOption: Codable {
    var id: String
    var path: String
}

struct AngleOption: Codable {
    var id: String
    var label: String
}

struct FormatOption: Codable {
    var id: String
    var label: String
}

struct PipelineView: View {
    @ObservedObject var state: AppState
    let scriptRunner: ScriptRunner
    @State private var options: PipelineOptionsResponse?
    @State private var optionsError: String?
    @State private var isLoadingOptions = false

    // Identity
    @State private var topic: String = "anxiety"
    @State private var persona: String = "corporate_managers"
    @State private var series: String = ""
    @State private var installment: String = "1"

    // Arc & story (point of view, beat map, story arc)
    @State private var selectedArcPath: String = ""
    @State private var angle: String = ""
    @State private var seed: String = "pipeline_seed_001"

    // Format (how the book turns out)
    @State private var outputFormat: String = "pocket_guide"
    @State private var structuralFormat: String = ""
    @State private var runtimeFormat: String = ""
    @State private var disableV4Freeze: Bool = false

    // Optional
    @State private var teacher: String = ""
    @State private var author: String = ""
    @State private var narrator: String = ""

    // Output
    @State private var renderBook: Bool = true
    @State private var skipWordCountGate: Bool = false

    @State private var logOutput: String = ""
    @State private var isRunning: Bool = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Run one book (QA)")
                    .font(.title2)
                    .foregroundColor(PhoenixColors.phoenixBlue)
                Text("Choose topic, persona, arc, angle, format, and other knobs to run the pipeline for a single book and QA the result.")
                    .font(.caption)
                    .foregroundColor(.secondary)

                if isLoadingOptions {
                    HStack {
                        ProgressView()
                        Text("Loading options…")
                            .foregroundColor(.secondary)
                    }
                } else if let err = optionsError {
                    Text("Options: \(err)")
                        .foregroundColor(.red)
                        .font(.caption)
                }

                // Identity
                sectionHeader("Identity")
                HStack(spacing: 12) {
                    labeledPicker("Topic", selection: $topic, options: options?.topics ?? [topic])
                    labeledPicker("Persona", selection: $persona, options: options?.personas ?? [persona])
                    labeledField("Series", text: $series, placeholder: "optional")
                    labeledField("Installment", text: $installment, placeholder: "1")
                }

                // Arc & story (beat map, story arc, point of view)
                sectionHeader("Arc & story")
                HStack(spacing: 12) {
                    arcPicker
                    labeledPicker("Angle", selection: $angle, options: angleOptions)
                    labeledField("Seed", text: $seed, placeholder: "pipeline_seed_001")
                }

                // Format (metaphor / shape of book)
                sectionHeader("Format")
                HStack(spacing: 12) {
                    if disableV4Freeze {
                        labeledPicker("Structural", selection: $structuralFormat, options: options?.structural_formats ?? ["F006"])
                        labeledPicker("Runtime", selection: $runtimeFormat, options: options?.runtime_formats ?? ["standard_book"])
                    } else {
                        labeledPicker("Output format", selection: $outputFormat, options: outputFormatOptions)
                    }
                    Toggle("Disable V4 freeze", isOn: $disableV4Freeze)
                        .toggleStyle(.checkbox)
                }

                // Optional
                sectionHeader("Optional")
                HStack(spacing: 12) {
                    labeledField("Teacher", text: $teacher, placeholder: "teacher id")
                    labeledField("Author", text: $author, placeholder: "author id")
                    labeledField("Narrator", text: $narrator, placeholder: "narrator id")
                }

                // Output
                sectionHeader("Output")
                HStack(spacing: 16) {
                    Toggle("Render book", isOn: $renderBook)
                        .toggleStyle(.checkbox)
                    Toggle("Skip word-count gate", isOn: $skipWordCountGate)
                        .toggleStyle(.checkbox)
                }

                HStack {
                    Button("Run one book") {
                        runPipeline()
                    }
                    .buttonStyle(.borderedProminent)
                    .keyboardShortcut(.return, modifiers: .command)
                    .disabled(state.repoPath.isEmpty || isRunning || selectedArcPath.isEmpty)
                    if isRunning {
                        Button("Cancel") { scriptRunner.cancel() }
                    }
                }

                LiveLogView(logText: $logOutput, isRunning: isRunning)
            }
            .padding()
        }
        .background(PhoenixColors.phoenixBackground)
        .onAppear {
            loadOptions()
        }
    }

    private func sectionHeader(_ title: String) -> some View {
        Text(title)
            .font(.headline)
            .foregroundColor(PhoenixColors.phoenixBlue)
    }

    private var arcPicker: some View {
        Group {
            if let arcs = options?.arcs, !arcs.isEmpty {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Arc")
                    Picker("", selection: $selectedArcPath) {
                        Text("Select arc…")
                            .tag("")
                        ForEach(arcs, id: \.path) { arc in
                            Text(arc.id)
                                .tag(arc.path)
                        }
                    }
                    .pickerStyle(.menu)
                    .labelsHidden()
                    .frame(minWidth: 220)
                }
            } else {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Arc path")
                    TextField("config/source_of_truth/master_arcs/…", text: $selectedArcPath)
                        .frame(minWidth: 280)
                }
            }
        }
    }

    private var angleOptions: [String] {
        guard let angles = options?.angles, !angles.isEmpty else { return ["", "WRONG_PROBLEM", "MAP_PROMISE", "HIDDEN_TRUTH", "ONE_LEVER"] }
        return [""] + angles.map { $0.id }
    }

    private var outputFormatOptions: [String] {
        guard let formats = options?.output_formats, !formats.isEmpty else { return ["pocket_guide", "myth_vs_mechanism"] }
        return formats.map { $0.id }
    }

    private func labeledPicker(_ label: String, selection: Binding<String>, options: [String]) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(label)
            Picker("", selection: selection) {
                ForEach(options, id: \.self) { opt in
                    Text(opt.isEmpty ? "(none)" : opt).tag(opt)
                }
            }
            .pickerStyle(.menu)
            .labelsHidden()
            .frame(minWidth: 120)
        }
    }

    private func labeledField(_ label: String, text: Binding<String>, placeholder: String) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(label)
            TextField(placeholder, text: text)
                .frame(width: 100)
        }
    }

    private func loadOptions() {
        guard !state.repoPath.isEmpty else { return }
        isLoadingOptions = true
        optionsError = nil
        var output = ""
        Task {
            do {
                _ = try await scriptRunner.run(
                    repoPath: state.repoPath,
                    scriptPath: "scripts/list_pipeline_options.py",
                    arguments: [],
                    timeoutSeconds: 30,
                    onOutput: { output += $0 }
                )
                await MainActor.run {
                    let trimmed = output.trimmingCharacters(in: .whitespacesAndNewlines)
                    if let data = trimmed.data(using: .utf8),
                       let decoded = try? JSONDecoder().decode(PipelineOptionsResponse.self, from: data) {
                        options = decoded
                        if selectedArcPath.isEmpty, let first = decoded.arcs?.first {
                            selectedArcPath = first.path
                        }
                        if topic.isEmpty, let first = decoded.topics?.first { topic = first }
                        if persona.isEmpty, let first = decoded.personas?.first { persona = first }
                    } else {
                        optionsError = "Could not parse options"
                    }
                    isLoadingOptions = false
                }
            } catch {
                await MainActor.run {
                    optionsError = error.localizedDescription
                    isLoadingOptions = false
                }
            }
        }
    }

    private func runPipeline() {
        guard !state.repoPath.isEmpty else { return }
        guard !selectedArcPath.isEmpty else { return }
        var args: [String] = [
            "--topic", topic,
            "--persona", persona,
            "--arc", selectedArcPath,
            "--seed", seed,
        ]
        if !series.isEmpty { args += ["--series", series] }
        if let inst = Int(installment.trimmingCharacters(in: .whitespaces)), inst > 0 {
            args += ["--installment", "\(inst)"]
        }
        if !angle.isEmpty { args += ["--angle", angle] }
        if disableV4Freeze {
            if !structuralFormat.isEmpty { args += ["--structural-format", structuralFormat] }
            if !runtimeFormat.isEmpty { args += ["--runtime-format", runtimeFormat] }
            args += ["--disable-v4-freeze"]
        } else if !outputFormat.isEmpty {
            args += ["--output-format", outputFormat]
        }
        if !teacher.isEmpty { args += ["--teacher", teacher] }
        if !author.isEmpty { args += ["--author", author] }
        if !narrator.isEmpty { args += ["--narrator", narrator] }
        if renderBook { args += ["--render-book"] }
        if skipWordCountGate { args += ["--skip-word-count-gate"] }

        logOutput = ""
        isRunning = true
        Task {
            do {
                _ = try await scriptRunner.run(
                    repoPath: state.repoPath,
                    scriptPath: "scripts/run_pipeline.py",
                    arguments: args,
                    timeoutSeconds: 600,
                    onOutput: { logOutput += $0 + "\n" }
                )
                await MainActor.run { isRunning = false }
            } catch {
                await MainActor.run {
                    logOutput += "\nError: \(error)"
                    isRunning = false
                }
            }
        }
    }
}
