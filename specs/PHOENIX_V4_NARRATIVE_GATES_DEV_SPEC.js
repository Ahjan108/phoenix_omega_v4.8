const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, PageNumber, PageBreak, LevelFormat, TabStopType, TabStopPosition
} = require('docx');

// ─── CONSTANTS ───────────────────────────────────────────────────
const PAGE_WIDTH = 12240;
const MARGIN = 1440;
const CONTENT_WIDTH = PAGE_WIDTH - MARGIN * 2; // 9360

const COLORS = {
  primary: "1B3A4B",
  accent: "D4763C",
  muted: "6B7280",
  light_bg: "F3F4F6",
  white: "FFFFFF",
  border: "D1D5DB",
  code_bg: "F9FAFB",
  warn_bg: "FFF7ED",
  warn_border: "F59E0B",
  success_bg: "F0FDF4",
  success_border: "22C55E",
  error_bg: "FEF2F2",
  error_border: "EF4444",
};

const border = (color = COLORS.border) => ({
  style: BorderStyle.SINGLE, size: 1, color
});
const borders = (color) => ({
  top: border(color), bottom: border(color), left: border(color), right: border(color)
});
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

// ─── HELPERS ─────────────────────────────────────────────────────
function heading(text, level = HeadingLevel.HEADING_1) {
  return new Paragraph({ heading: level, children: [new TextRun({ text, bold: true })] });
}

function para(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 120, ...(opts.spacing || {}) },
    children: [new TextRun({ text, size: 22, font: "Arial", ...opts })]
  });
}

function boldPara(label, text) {
  return new Paragraph({
    spacing: { after: 120 },
    children: [
      new TextRun({ text: label, size: 22, font: "Arial", bold: true }),
      new TextRun({ text, size: 22, font: "Arial" }),
    ]
  });
}

function code(text) {
  return new Paragraph({
    spacing: { after: 80 },
    shading: { fill: COLORS.code_bg, type: ShadingType.CLEAR },
    children: [new TextRun({ text, size: 20, font: "Courier New" })]
  });
}

function codeBlock(lines) {
  return lines.map(l => new Paragraph({
    spacing: { after: 0 },
    shading: { fill: COLORS.code_bg, type: ShadingType.CLEAR },
    indent: { left: 240 },
    children: [new TextRun({ text: l, size: 18, font: "Courier New" })]
  }));
}

function calloutBox(title, body, bgColor, borderColor) {
  return new Table({
    width: { size: CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths: [CONTENT_WIDTH],
    rows: [new TableRow({
      children: [new TableCell({
        borders: {
          top: { style: BorderStyle.SINGLE, size: 1, color: borderColor },
          bottom: { style: BorderStyle.SINGLE, size: 1, color: borderColor },
          left: { style: BorderStyle.SINGLE, size: 6, color: borderColor },
          right: { style: BorderStyle.SINGLE, size: 1, color: borderColor },
        },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 120, bottom: 120, left: 200, right: 200 },
        width: { size: CONTENT_WIDTH, type: WidthType.DXA },
        children: [
          new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: title, size: 22, bold: true, font: "Arial", color: borderColor })] }),
          new Paragraph({ children: [new TextRun({ text: body, size: 20, font: "Arial" })] }),
        ]
      })]
    })]
  });
}

function tableRow(cells, isHeader = false, headerColor = COLORS.primary) {
  return new TableRow({
    children: cells.map((text, i) => new TableCell({
      borders: borders(COLORS.border),
      shading: isHeader ? { fill: headerColor, type: ShadingType.CLEAR } : undefined,
      margins: cellMargins,
      width: { size: Math.floor(CONTENT_WIDTH / cells.length), type: WidthType.DXA },
      children: [new Paragraph({
        children: [new TextRun({
          text, size: 20, font: "Arial",
          bold: isHeader,
          color: isHeader ? "FFFFFF" : "111827",
        })]
      })]
    }))
  });
}

function simpleTable(headers, rows) {
  const colWidth = Math.floor(CONTENT_WIDTH / headers.length);
  return new Table({
    width: { size: CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths: headers.map(() => colWidth),
    rows: [
      tableRow(headers, true),
      ...rows.map(r => tableRow(r))
    ]
  });
}

function spacer(pts = 200) {
  return new Paragraph({ spacing: { after: pts }, children: [] });
}

function bullet(text, ref = "bullets", level = 0) {
  return new Paragraph({
    numbering: { reference: ref, level },
    children: [new TextRun({ text, size: 22, font: "Arial" })]
  });
}

function numberedItem(text, ref = "numbers", level = 0) {
  return new Paragraph({
    numbering: { reference: ref, level },
    children: [new TextRun({ text, size: 22, font: "Arial" })]
  });
}

// ─── DOCUMENT CONTENT ────────────────────────────────────────────

function buildTitlePage() {
  return [
    spacer(600),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 200 },
      children: [new TextRun({ text: "PHOENIX OMEGA V4", size: 56, bold: true, font: "Arial", color: COLORS.primary })]
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 100 },
      children: [new TextRun({ text: "Narrative Intelligence Upgrade", size: 36, font: "Arial", color: COLORS.accent })]
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 80 },
      children: [new TextRun({ text: "Dev Spec: Gates, Arcs, Exercises & Tests", size: 28, font: "Arial", color: COLORS.muted })]
    }),
    spacer(200),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      border: { top: { style: BorderStyle.SINGLE, size: 2, color: COLORS.accent, space: 8 } },
      spacing: { before: 200, after: 100 },
      children: [new TextRun({ text: "SpiritualTech Systems", size: 24, font: "Arial", color: COLORS.muted })]
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: "February 2026  \u2022  Authoritative  \u2022  Implementation-Ready", size: 20, font: "Arial", color: COLORS.muted })]
    }),
    new Paragraph({ children: [new PageBreak()] }),
  ];
}

function buildOverview() {
  return [
    heading("1. Overview"),
    para("This spec covers four workstreams that upgrade Phoenix V4 from \u201Cstructurally correct\u201D to \u201Cnarrative intelligence engine.\u201D Each workstream is self-contained, ordered by dependency, and includes implementation details grounded in the existing codebase."),
    spacer(80),

    simpleTable(
      ["Workstream", "What It Does", "Priority"],
      [
        ["WS-1: Narrative Gates", "5 CI gates enforcing emotional escalation, cost gradients, callbacks, identity shifts, and macro-cadence", "P0 \u2014 Highest"],
        ["WS-2: Arc Blueprint Library", "10 parameterized arc templates covering all active persona\u00D7topic combinations", "P0"],
        ["WS-3: Exercise Approval + K-Tables", "Promote 11 exercise stubs to approved; write K-tables for F001\u2013F015", "P1"],
        ["WS-4: Regression Test Suite", "Full pipeline coverage: assembly compiler, slot resolver, validator chain, wave orchestrator", "P1"],
      ]
    ),
    spacer(100),

    calloutBox(
      "NON-NEGOTIABLE",
      "None of these workstreams introduce runtime prose generation. All changes enforce structure on pre-approved human-authored content. The golden rule holds: if runtime writes text, the system is broken.",
      COLORS.warn_bg, COLORS.warn_border
    ),
    spacer(100),

    heading("1.1 Current State (Audit Summary)", HeadingLevel.HEADING_2),
    para("The following gaps were identified against the V4 Narrative Amplification Addendum (v4_system_up_spec.txt) and the V4.5 Complete Format Spec:"),

    simpleTable(
      ["Area", "Spec Promise", "Actual State"],
      [
        ["Narrative Gates", "5 CI gates (mechanism, cost, callback, identity, cadence)", "0 implemented; metadata fields absent from atoms"],
        ["Arc Blueprints", "Per persona\u00D7topic\u00D7format arcs", "2 arcs total (gen_z anxiety F002, nyc_exec self_worth F006)"],
        ["Exercises", "11 canonical types, approved pool", "11 stubs in candidate/; approved/ is empty (.gitkeep)"],
        ["K-Tables", "Per-format pool depth validation", "Only F006 has a K-table"],
        ["Test Coverage", "Pipeline regression tests", "2 test files (emotional_curve_golden, format_selector)"],
      ]
    ),
    new Paragraph({ children: [new PageBreak()] }),
  ];
}

function buildWS1() {
  return [
    heading("2. Workstream 1: Narrative Gates"),
    para("Implements the five narrative intelligence gates from the V4 Narrative Amplification Addendum. Each gate adds metadata fields to the atom/scene schema, a validator module in phoenix_v4/qa/, and a CI entry point."),
    spacer(80),

    // ── 2.1 Schema Changes ──
    heading("2.1 Atom Schema Extensions", HeadingLevel.HEADING_2),
    para("Add the following fields to atom metadata. These fields are OPTIONAL during migration (existing atoms default to safe values) but REQUIRED for newly authored atoms."),
    spacer(60),

    heading("2.1.1 CANONICAL.txt Header Extension", HeadingLevel.HEADING_3),
    para("Each atom block in CANONICAL.txt gains new metadata lines after the existing path: and BAND: lines:"),
    ...codeBlock([
      "## RECOGNITION v01",
      "---",
      "path: story_atoms/nyc_executives/anchored/anxiety/false_alarm/recognition/micro/v01.txt",
      "BAND: 2",
      "MECHANISM_DEPTH: 1",
      "COST_TYPE: social",
      "COST_INTENSITY: 2",
      "IDENTITY_STAGE: pre_awareness",
      "CALLBACK_ID: email_spike",
      "CALLBACK_PHASE: setup",
      "---",
    ]),
    spacer(80),

    heading("2.1.2 Field Definitions", HeadingLevel.HEADING_3),
    simpleTable(
      ["Field", "Type", "Values", "Default (existing atoms)"],
      [
        ["MECHANISM_DEPTH", "int 1\u20134", "1=surface, 2=behavioral, 3=nervous_system, 4=identity", "1"],
        ["COST_TYPE", "enum", "social | internal | opportunity | identity", "social"],
        ["COST_INTENSITY", "int 1\u20135", "1=mild discomfort, 5=crisis-level cost", "2"],
        ["IDENTITY_STAGE", "enum", "pre_awareness | destabilization | experimentation | self_claim", "pre_awareness"],
        ["CALLBACK_ID", "string", "Free-form slug (e.g. email_spike, mirror_moment)", "null (no callback)"],
        ["CALLBACK_PHASE", "enum", "setup | escalation | return", "null"],
      ]
    ),
    spacer(100),

    calloutBox(
      "MIGRATION STRATEGY",
      "Existing 68 atom files default to depth=1, cost_type=social, cost_intensity=2, identity_stage=pre_awareness, no callbacks. A tagging script (tools/tag_existing_atoms.py) should be run ONCE by a content lead to assign accurate values. Gates run in WARN mode until >80% of atoms are tagged, then switch to FAIL mode.",
      COLORS.success_bg, COLORS.success_border
    ),
    spacer(100),

    // ── 2.2 Gate Implementations ──
    heading("2.2 Gate 1: Mechanism Escalation", HeadingLevel.HEADING_2),
    boldPara("File: ", "phoenix_v4/qa/mechanism_escalation_gate.py"),
    boldPara("Purpose: ", "Enforce that mechanism_depth increases across the arc. Books must not feel flat in insight."),
    spacer(60),

    heading("Rule", HeadingLevel.HEADING_3),
    para("For a compiled plan with N chapters, compute max(mechanism_depth) per chapter from selected STORY atoms:"),
    ...codeBlock([
      "max_depth_per_chapter = [",
      "    max(atom.mechanism_depth for atom in chapter_story_atoms)",
      "    for chapter in compiled_plan.chapters",
      "]",
    ]),
    spacer(60),

    simpleTable(
      ["Phase", "Chapters", "Required Depth"],
      [
        ["Early", "1 to N//3", "\u22651 (surface allowed)"],
        ["Mid", "N//3+1 to 2*N//3", "\u22652 (must reach behavioral)"],
        ["Late", "2*N//3+1 to N", "\u22653 (must reach nervous_system); at least one depth=4 by final third"],
      ]
    ),
    spacer(60),

    heading("Fail Conditions", HeadingLevel.HEADING_3),
    bullet("Depth plateaus (no increase) after midpoint"),
    bullet("Depth decreases in late-stage chapters"),
    bullet("No depth=4 (identity-level) mechanism in final third"),
    bullet("Max depth across entire book < 3"),
    spacer(60),

    heading("Interface", HeadingLevel.HEADING_3),
    ...codeBlock([
      "def validate_mechanism_escalation(",
      "    plan: CompiledBook,",
      "    atom_metadata: dict[str, dict],  # atom_id -> {mechanism_depth, ...}",
      ") -> ValidationResult:",
      "    \"\"\"Returns ValidationResult(valid, errors, warnings).\"\"\"",
    ]),
    spacer(100),

    // ── Gate 2 ──
    heading("2.3 Gate 2: Cost Gradient", HeadingLevel.HEADING_2),
    boldPara("File: ", "phoenix_v4/qa/cost_gradient_gate.py"),
    boldPara("Purpose: ", "Enforce escalating emotional cost. Narratives need increasing stakes, not flat tension."),
    spacer(60),

    heading("Rule", HeadingLevel.HEADING_3),
    para("Compute avg(cost_intensity) per chapter from STORY + SCENE atoms:"),
    ...codeBlock([
      "avg_cost_per_chapter = [",
      "    mean(atom.cost_intensity for atom in chapter_atoms)",
      "    for chapter in compiled_plan.chapters",
      "]",
    ]),
    spacer(60),

    simpleTable(
      ["Phase", "Required avg(cost_intensity)"],
      [
        ["Chapters 1\u20132", "1\u20132"],
        ["Chapters 3 to mid", "2\u20134"],
        ["Mid to near-end", "4\u20135"],
        ["Final chapter", "Resolution without erasing cost history (no drop below 2)"],
      ]
    ),
    spacer(60),

    heading("Fail Conditions", HeadingLevel.HEADING_3),
    bullet("Highest cost occurs before midpoint (premature peak)"),
    bullet("No high-intensity cost (>=4) before identity shift chapter"),
    bullet("Cost drops to 1 in final third (pain erased)"),
    bullet("Average cost across book < 2.5"),
    spacer(100),

    // ── Gate 3 ──
    heading("2.4 Gate 3: Callback Integrity", HeadingLevel.HEADING_2),
    boldPara("File: ", "phoenix_v4/qa/callback_integrity_gate.py"),
    boldPara("Purpose: ", "Enforce symbolic continuity. Setups must return; threads must close."),
    spacer(60),

    heading("Rule", HeadingLevel.HEADING_3),
    para("Scan all atoms in the compiled plan for callback_id and callback_phase:"),
    bullet("Every callback_id with phase=setup must have a corresponding phase=return later in the book"),
    bullet("Every phase=return must have a prior phase=setup"),
    bullet("Maximum 2 unclosed symbolic threads at book end"),
    spacer(60),

    heading("Arc Plan Requirement", HeadingLevel.HEADING_3),
    para("Arc blueprints gain an optional field:"),
    ...codeBlock([
      "arc_requirements:",
      "  requires_callback: true",
      "  callback_min_count: 2  # minimum distinct callback threads",
    ]),
    spacer(60),

    heading("Fail Conditions", HeadingLevel.HEADING_3),
    bullet("Setup exists without return (orphaned thread)"),
    bullet("Return exists without setup (ungrounded payoff)"),
    bullet("More than 2 unclosed threads at end of book"),
    bullet("Arc requires callbacks but compiled plan has 0 callback_ids"),
    spacer(100),

    // ── Gate 4 ──
    heading("2.5 Gate 4: Identity Shift", HeadingLevel.HEADING_2),
    boldPara("File: ", "phoenix_v4/qa/identity_shift_gate.py"),
    boldPara("Purpose: ", "Enforce monotonic identity progression. Readers remember identity shifts; the arc must build to them."),
    spacer(60),

    heading("Identity Stage Progression", HeadingLevel.HEADING_3),
    simpleTable(
      ["Phase", "Required identity_stage"],
      [
        ["Early (ch 1 to N//4)", "pre_awareness"],
        ["Early-Mid (N//4 to N//2)", "destabilization"],
        ["Late-Mid (N//2 to 3*N//4)", "experimentation"],
        ["Final (3*N//4 to N)", "self_claim (subtle, not grandiose)"],
      ]
    ),
    spacer(60),

    heading("Rule", HeadingLevel.HEADING_3),
    para("Identity stage progression must be monotonic (no regression). The stage ordinal is: pre_awareness=0, destabilization=1, experimentation=2, self_claim=3."),
    ...codeBlock([
      "STAGE_ORD = {",
      "    'pre_awareness': 0, 'destabilization': 1,",
      "    'experimentation': 2, 'self_claim': 3",
      "}",
      "max_stage_per_chapter = [",
      "    max(STAGE_ORD[a.identity_stage] for a in ch_atoms)",
      "    for ch_atoms in chapters",
      "]",
      "# Must be non-decreasing",
    ]),
    spacer(60),

    heading("Fail Conditions", HeadingLevel.HEADING_3),
    bullet("No experimentation before final quarter of book"),
    bullet("Final chapter lacks any self_claim atom"),
    bullet("Identity shift happens too early (self_claim before midpoint)"),
    bullet("Regression: higher stage followed by lower stage"),
    spacer(100),

    // ── Gate 5 ──
    heading("2.6 Gate 5: Macro-Cadence Wave", HeadingLevel.HEADING_2),
    boldPara("File: ", "phoenix_v4/qa/macro_cadence_gate.py"),
    boldPara("Purpose: ", "Enforce emotional rhythm at the chapter level. Prevent reader exhaustion or emotional monotony."),
    spacer(60),

    heading("Chapter Intensity Profile", HeadingLevel.HEADING_3),
    para("Each chapter declares (derived from arc + atom metadata):"),
    ...codeBlock([
      "chapter_profile:",
      "  emotional_intensity: 1-5  # from arc emotional_curve",
      "  regulation_support: low | medium | high  # from exercise presence + type",
    ]),
    spacer(60),

    heading("Rules", HeadingLevel.HEADING_3),
    bullet("No 3 consecutive chapters at intensity=5 (burnout risk)"),
    bullet("Every intensity=4 or intensity=5 chapter must be followed within 2 chapters by a chapter with regulation_support >= medium"),
    bullet("At least one chapter with regulation_support=high in the second half of the book"),
    bullet("Intensity must not be monotonically increasing with zero relief (need at least one dip after midpoint)"),
    spacer(60),

    heading("Regulation Support Derivation", HeadingLevel.HEADING_3),
    simpleTable(
      ["Condition", "regulation_support"],
      [
        ["Chapter has EXERCISE slot + exercise type is downregulation/grounding/breath", "high"],
        ["Chapter has EXERCISE slot (any type)", "medium"],
        ["Chapter has no EXERCISE slot", "low"],
      ]
    ),
    spacer(60),

    heading("Fail Conditions", HeadingLevel.HEADING_3),
    bullet("3+ consecutive intensity=5 chapters"),
    bullet("High-intensity chapter not followed by regulation within 2 chapters"),
    bullet("No regulation_support=high in second half"),
    bullet("Monotonic intensity increase from ch 1 to final ch with zero dips"),
    spacer(100),

    // ── 2.7 Metadata Loader ──
    heading("2.7 Metadata Loader", HeadingLevel.HEADING_2),
    boldPara("File: ", "phoenix_v4/qa/atom_metadata_loader.py"),
    para("All five gates need atom metadata. This shared module loads CANONICAL.txt files and parses the extended header fields into a dict[atom_id, metadata_dict]. The assembly_compiler.py already uses _parse_canonical_txt(); extend it to parse the new fields and expose them via the PoolIndex."),
    spacer(60),

    ...codeBlock([
      "def load_atom_metadata(atoms_root: Path, persona: str, topic: str) -> dict:",
      "    \"\"\"Returns {atom_id: {mechanism_depth, cost_type, cost_intensity,",
      "     identity_stage, callback_id, callback_phase, band, ...}}\"\"\"",
    ]),
    spacer(100),

    // ── 2.8 Tagging Tool ──
    heading("2.8 Atom Tagging Tool", HeadingLevel.HEADING_2),
    boldPara("File: ", "tools/tag_existing_atoms.py"),
    para("CLI tool for content leads to tag existing CANONICAL.txt atoms with the new metadata fields. Reads each atom block, shows the prose, and prompts for values. Can also run in batch mode with a CSV input."),
    spacer(60),

    ...codeBlock([
      "python tools/tag_existing_atoms.py \\",
      "  --atoms-dir atoms/nyc_executives/anxiety \\",
      "  --mode interactive",
      "",
      "python tools/tag_existing_atoms.py \\",
      "  --atoms-dir atoms/ \\",
      "  --csv tags.csv \\",
      "  --mode batch",
    ]),
    spacer(100),

    // ── 2.9 CI Integration ──
    heading("2.9 CI Integration", HeadingLevel.HEADING_2),
    para("Add a unified gate runner that executes all five narrative gates on a compiled plan:"),
    ...codeBlock([
      "# tools/ci/run_narrative_gates.py",
      "python -m tools.ci.run_narrative_gates \\",
      "  --plan artifacts/compiled/plan_001.json \\",
      "  --atoms-root atoms/ \\",
      "  --mode warn  # warn | fail",
    ]),
    spacer(60),

    para("The --mode flag controls behavior: warn logs errors but exits 0; fail exits non-zero on any gate failure. Default to warn until atom tagging is >80% complete, then switch to fail."),
    spacer(60),

    calloutBox(
      "GATE ORDERING",
      "Gates run in dependency order: (1) Mechanism Escalation, (2) Cost Gradient, (3) Callback Integrity, (4) Identity Shift, (5) Macro-Cadence. A failure in an earlier gate does not skip later gates; all errors are collected and reported together.",
      COLORS.light_bg, COLORS.muted
    ),

    new Paragraph({ children: [new PageBreak()] }),
  ];
}

function buildWS2() {
  return [
    heading("3. Workstream 2: Arc Blueprint Library"),
    para("The system currently has 2 arc blueprints. The wave orchestrator is designed to balance 60 books per wave, which means arc variety is critical. This workstream creates 10 parameterized arc templates that cover all active persona\u00D7topic combinations."),
    spacer(80),

    heading("3.1 Arc Template Design", HeadingLevel.HEADING_2),
    para("Rather than authoring one arc per persona\u00D7topic\u00D7format triple (which would require hundreds), we create parameterized templates that accept persona and topic as inputs and produce concrete arcs."),
    spacer(60),

    heading("3.1.1 Template Structure", HeadingLevel.HEADING_3),
    para("Each arc template YAML contains fixed structural elements and parameterized persona/topic slots:"),
    ...codeBlock([
      "# config/source_of_truth/master_arcs/templates/standard_escalation.yaml",
      "template_id: standard_escalation",
      "description: \"Classic escalation arc: recognition -> cost -> mechanism -> identity shift\"",
      "compatible_formats: [F001, F002, F003, F006, F007, F010, F011, F014]",
      "compatible_tiers: [A, B]",
      "chapter_count_range: [7, 30]",
      "",
      "# Fixed structural shape (normalized to 10 phases, scaled to actual chapter_count)",
      "emotional_curve_template: [1, 2, 2, 3, 3, 4, 4, 5, 3, 2]",
      "emotional_role_template:",
      "  - recognition",
      "  - destabilization",
      "  - destabilization",
      "  - reframe",
      "  - destabilization",
      "  - reframe",
      "  - destabilization",
      "  - stabilization",
      "  - reframe",
      "  - integration",
      "",
      "reflection_strategy_cycle: [didactic, socratic, narrative_embedded]",
      "",
      "# Parameterized (filled at arc generation time)",
      "motif_bank:",
      "  anxiety: {primary_symbol: alarm, recurring_image: chest_and_phone, tonal_signature: restrained_clarity}",
      "  depression: {primary_symbol: weight, recurring_image: bed_and_ceiling, tonal_signature: slow_witness}",
      "  boundaries: {primary_symbol: door, recurring_image: threshold_moment, tonal_signature: quiet_firmness}",
      "  grief_topic: {primary_symbol: absence, recurring_image: empty_chair, tonal_signature: tender_witness}",
      "  # ... per topic",
      "",
      "cost_chapter_position: 0.75  # fraction of chapter_count (rounded)",
      "resolution_type: internal_shift_only",
    ]),
    spacer(100),

    heading("3.1.2 Arc Generation Script", HeadingLevel.HEADING_3),
    boldPara("File: ", "tools/arc_generator.py"),
    para("Takes a template + persona + topic + format + chapter_count and produces a concrete arc YAML:"),
    ...codeBlock([
      "python tools/arc_generator.py \\",
      "  --template standard_escalation \\",
      "  --persona gen_z_professionals \\",
      "  --topic anxiety \\",
      "  --format F002 \\",
      "  --chapter-count 30 \\",
      "  --out config/source_of_truth/master_arcs/gen_z_professionals__anxiety__overwhelm__F002.yaml",
    ]),
    spacer(60),

    para("The generator scales the 10-phase template to the actual chapter count using linear interpolation, assigns motifs from the template\u2019s motif_bank, computes cost_chapter_index, and fills the reflection_strategy_sequence by cycling the template\u2019s cycle."),
    spacer(100),

    heading("3.2 The 10 Required Templates", HeadingLevel.HEADING_2),
    simpleTable(
      ["Template ID", "Arc Shape", "Best For", "Compatible Formats"],
      [
        ["standard_escalation", "Recognition \u2192 cost \u2192 mechanism \u2192 identity shift", "Anxiety, depression, burnout", "F001\u2013F003, F006, F007, F010, F011, F014"],
        ["slow_burn", "Low tension building to single high-intensity crisis, then landing", "Grief, compassion fatigue", "F004, F006, F009, F013"],
        ["wave_cycle", "3 peaks with recovery valleys between each", "Boundaries, self-worth, courage", "F001, F002, F008"],
        ["rupture_repair", "Early rupture \u2192 failed repair \u2192 successful repair", "Relationship topics, trust", "F009, F011, F014"],
        ["descent_return", "Steady descent into pain \u2192 bottom \u2192 gradual return", "Depression, financial stress", "F004, F006, F013"],
        ["sprint_intensity", "High intensity from ch 2, brief recovery, sustained", "Short formats, rescue kits", "F003, F005, F015"],
        ["spiral_recognition", "Repeated pattern exposure with increasing clarity each cycle", "Anxiety spirals, shame loops", "F001, F002, F007"],
        ["somatic_ladder", "Body-first: sensation \u2192 emotion \u2192 thought \u2192 identity", "Somatic-focused topics", "F004, F006, F015"],
        ["parts_dialogue", "Internal parts emerge, conflict, negotiate, integrate", "IFS-aligned content", "F009, F014"],
        ["micro_precision", "Single mechanism, single cost, single shift. No waste.", "Capsules, resets, micro-books", "F005, F012, F015"],
      ]
    ),
    spacer(100),

    heading("3.3 Concrete Arc Targets", HeadingLevel.HEADING_2),
    para("Using the 10 templates, generate concrete arcs for all active persona\u00D7topic combinations. Current active matrix:"),
    spacer(60),

    simpleTable(
      ["Persona", "Active Topics", "Priority Arcs to Generate"],
      [
        ["nyc_executives", "anxiety, boundaries, compassion_fatigue, courage, depression, financial_stress, grief, self_worth", "8 arcs (one per topic, standard_book format)"],
        ["educators", "anxiety, boundaries, compassion_fatigue, courage, depression, financial_stress", "6 arcs"],
        ["gen_z_professionals", "anxiety, depression, financial_stress", "3 arcs + expand to 6 topics"],
        ["healthcare_rns", "depression, financial_stress", "2 arcs + expand to 4 topics"],
        ["gen_alpha_students", "depression, financial_stress", "2 arcs + expand to 4 topics"],
      ]
    ),
    spacer(60),

    boldPara("Target: ", "21 concrete arcs minimum (one per active persona\u00D7topic), generated from the 10 templates. This gives the wave orchestrator enough variety to balance 60-book waves."),
    spacer(60),

    heading("3.4 Validation", HeadingLevel.HEADING_2),
    para("Extend validate_arc_alignment.py to validate generated arcs against the template constraints:"),
    bullet("emotional_curve length matches chapter_count"),
    bullet("emotional_role_sequence contains all required stages (recognition through integration)"),
    bullet("cost_chapter_index falls within the template\u2019s position range"),
    bullet("motif fields are non-empty"),
    bullet("Template compatibility: format must be in compatible_formats list"),

    new Paragraph({ children: [new PageBreak()] }),
  ];
}

function buildWS3() {
  return [
    heading("4. Workstream 3: Exercise Approval + K-Tables"),
    spacer(60),

    heading("4.1 Exercise Stub Promotion", HeadingLevel.HEADING_2),
    para("11 canonical exercise type stubs exist in SOURCE_OF_TRUTH/exercises_v4/candidate/_stubs/. Each must be expanded into full approved exercises following the canonical 4-section structure."),
    spacer(60),

    heading("4.1.1 The 11 Canonical Types", HeadingLevel.HEADING_3),
    simpleTable(
      ["Stub File", "Exercise Type", "Cadence Role", "Min Variants Needed"],
      [
        ["00_breath_regulation.yaml", "breath_regulation", "grounding", "3"],
        ["01_grounding_orientation.yaml", "grounding_orientation", "grounding", "3"],
        ["02_body_awareness_scan.yaml", "body_awareness_scan", "grounding", "2"],
        ["03_somatic_release_discharge.yaml", "somatic_release", "release", "2"],
        ["04_nervous_system_downregulation.yaml", "downregulation", "regulation", "3"],
        ["05_nervous_system_upregulation.yaml", "upregulation", "activation", "2"],
        ["06_vagal_stimulation_sound.yaml", "vagal_stimulation", "regulation", "2"],
        ["07_self_contact_touch.yaml", "self_contact", "grounding", "2"],
        ["08_emotional_processing_completion.yaml", "emotional_processing", "release", "2"],
        ["09_embodied_intention_direction.yaml", "embodied_intention", "integration", "2"],
        ["10_integration_return_to_baseline.yaml", "integration", "integration", "3"],
      ]
    ),
    spacer(80),

    boldPara("Total minimum: ", "26 approved exercise variants across 11 types."),
    spacer(60),

    heading("4.1.2 Authoring Requirements (Per Exercise)", HeadingLevel.HEADING_3),
    para("Each exercise YAML must contain all 4 sections with these constraints:"),
    spacer(40),

    simpleTable(
      ["Section", "Min Words", "Voice", "Must Contain", "Must NOT Contain"],
      [
        ["intro", "60", "2nd person, present", "validation phrase", "promises, fixing language"],
        ["guided_practice", "80", "2nd person, imperative", "\u22653 somatic imperatives (notice, soften, feel)", "advice, persuasion"],
        ["aha_noticing", "40", "2nd person", "\"you might notice\" + body reference", "outcome claims"],
        ["integration", "40", "2nd person", "open ending", "resolution language (healed, fixed, cured)"],
      ]
    ),
    spacer(60),

    heading("4.1.3 Approval Pipeline", HeadingLevel.HEADING_3),
    para("The exercise authoring contract (exercise_yaml_helper.txt) and existing overlay_substitution.py define the quality gates. The pipeline is:"),
    spacer(40),

    numberedItem("Author writes exercise YAML in candidate/ following schema from phoenix_rebuild_spec.txt \u00A72"),
    numberedItem("Run exercise lint: python -m tools.exercise_lint.lint_exercise <file>"),
    numberedItem("Lint checks: schema validity, 4-section presence, word counts, banned phrases, callout prefixes, body reference words"),
    numberedItem("Content lead reviews and runs: python tools/exercise_approval/exercise_approve.py approve --id <id>"),
    numberedItem("Approved exercise moves to SOURCE_OF_TRUTH/exercises_v4/approved/<persona>/<topic>/"),
    numberedItem("CI gate (check_approved_exercises_status.py) verifies only approved exercises are runtime-visible"),
    spacer(100),

    heading("4.2 K-Tables for All Active Formats", HeadingLevel.HEADING_2),
    para("K-tables define the minimum pool depth (atom count) required per slot type per format. Only F006 currently has a K-table. The assembly compiler needs K-tables to validate it has enough atoms before attempting compilation."),
    spacer(60),

    heading("4.2.1 K-Table Schema", HeadingLevel.HEADING_3),
    ...codeBlock([
      "# config/format_selection/k_tables/F001.yaml",
      "format_id: F001",
      "tier: B",
      "chapter_count: 90",
      "",
      "required_pool_depth:",
      "  HOOK: 15      # unique hooks needed (reuse allowed after 6-chapter gap)",
      "  SCENE: 20     # unique scenes",
      "  STORY: 90     # one per chapter, no reuse",
      "  REFLECTION: 20 # reuse allowed after 10-chapter gap",
      "  EXERCISE: 8    # unique exercises (reuse after 12-chapter gap)",
      "  INTEGRATION: 10",
      "",
      "reuse_rules:",
      "  STORY: never   # absolute no-reuse for stories",
      "  HOOK: {min_gap: 6}",
      "  SCENE: {min_gap: 8}",
      "  REFLECTION: {min_gap: 10}",
      "  EXERCISE: {min_gap: 12}",
      "  INTEGRATION: {min_gap: 6}",
    ]),
    spacer(80),

    heading("4.2.2 K-Tables to Create", HeadingLevel.HEADING_3),
    simpleTable(
      ["Format", "Tier", "Chapters", "STORY Pool Min", "EXERCISE Pool Min"],
      [
        ["F001 (90-Day)", "B", "90", "90", "8"],
        ["F002 (Daily)", "B", "30\u2013365", "30\u2013365", "8"],
        ["F003 (Challenge)", "A", "7\u201321", "7\u201321", "4"],
        ["F004 (Somatic)", "A", "12\u201315", "12\u201315", "6"],
        ["F005 (Rescue Kit)", "C", "10\u201320", "10\u201320", "4"],
        ["F006 (Ladder)", "A", "8\u201312", "8\u201312", "4"],
        ["F007 (Shadow Work)", "A", "8\u201312", "8\u201312", "4"],
        ["F008 (Micro-Habits)", "B", "52", "52", "6"],
        ["F009 (Parts Work)", "A", "10\u201315", "10\u201315", "5"],
        ["F010 (Energy)", "A", "12\u201316", "12\u201316", "6"],
        ["F011 (Relationship)", "A", "8\u201312", "8\u201312", "4"],
        ["F012 (Permission)", "C", "52", "52", "4"],
        ["F013 (Crisis)", "A", "24", "24", "8"],
        ["F014 (Archetype)", "A", "10\u201315", "10\u201315", "5"],
        ["F015 (Sensory)", "C", "5\u20138", "5\u20138", "3"],
      ]
    ),
    spacer(60),

    heading("4.2.3 K-Table Validator", HeadingLevel.HEADING_3),
    boldPara("File: ", "phoenix_v4/qa/validate_k_table.py"),
    para("Before compilation, check that the atom pool for the target persona\u00D7topic meets the K-table minimums for the selected format:"),
    ...codeBlock([
      "def validate_pool_depth(",
      "    format_id: str,",
      "    persona_id: str,",
      "    topic_id: str,",
      "    pool_index: PoolIndex,",
      "    k_tables_dir: Path,",
      ") -> ValidationResult:",
      "    \"\"\"Fail if any slot type pool < K-table minimum.\"\"\"",
    ]),

    new Paragraph({ children: [new PageBreak()] }),
  ];
}

function buildWS4() {
  return [
    heading("5. Workstream 4: Regression Test Suite"),
    para("Current test coverage: 2 files (test_emotional_curve_golden.py, test_format_selector.py). For a system that stakes its identity on determinism, this is insufficient. This workstream adds comprehensive regression tests for the full pipeline."),
    spacer(80),

    heading("5.1 Test Architecture", HeadingLevel.HEADING_2),
    para("All tests use pytest. Test data lives in tests/fixtures/ as YAML and JSON. Golden output files are committed to tests/golden/ for snapshot testing."),
    spacer(60),

    ...codeBlock([
      "tests/",
      "  conftest.py                    # shared fixtures, paths",
      "  fixtures/",
      "    minimal_book_spec.yaml",
      "    minimal_format_plan.yaml",
      "    minimal_arc.yaml",
      "    sample_atoms/               # small canonical atom set for tests",
      "  golden/",
      "    compiled_plan_golden.json    # expected output snapshots",
      "  test_emotional_curve_golden.py # existing",
      "  test_format_selector.py        # existing",
      "  test_assembly_compiler.py      # NEW",
      "  test_slot_resolver.py          # NEW",
      "  test_arc_loader.py             # NEW",
      "  test_wave_orchestrator.py      # NEW",
      "  test_dupe_eval.py              # NEW",
      "  test_narrative_gates.py        # NEW",
      "  test_overlay_substitution.py   # NEW",
      "  test_naming_generator.py       # NEW",
      "  test_pipeline_e2e.py           # NEW",
    ]),
    spacer(100),

    heading("5.2 Test Specifications", HeadingLevel.HEADING_2),
    spacer(40),

    heading("5.2.1 test_assembly_compiler.py", HeadingLevel.HEADING_3),
    simpleTable(
      ["Test Case", "What It Validates"],
      [
        ["test_determinism", "Same (book_spec, format_plan, arc) produces identical plan_hash and atom_ids across 10 runs"],
        ["test_no_atom_reuse", "No atom_id appears twice in a compiled plan"],
        ["test_slot_definitions_respected", "atom_ids length == sum of slot counts; slot types match"],
        ["test_arc_required", "Raises ValueError when arc is None"],
        ["test_band_filtering", "STORY atoms match arc emotional_curve band per chapter"],
        ["test_semantic_family_decay", "No two atoms from same semantic_family in one book"],
        ["test_placeholder_on_pool_exhaustion", "Placeholders inserted when pool too small (require_full_resolution=False)"],
        ["test_require_full_resolution_fails", "Raises when pool insufficient and require_full_resolution=True"],
        ["test_compression_slots", "F006 format correctly fills COMPRESSION slots"],
        ["test_exercise_chapters_computed", "exercise_chapters field matches actual EXERCISE slot positions"],
      ]
    ),
    spacer(80),

    heading("5.2.2 test_slot_resolver.py", HeadingLevel.HEADING_3),
    simpleTable(
      ["Test Case", "What It Validates"],
      [
        ["test_sha256_determinism", "Same selector_key always produces same index"],
        ["test_no_python_hash", "Resolver does NOT use Python\u2019s built-in hash()"],
        ["test_used_ids_excluded", "Previously used atom_ids never selected again"],
        ["test_band_filter_applied", "When required_band_by_chapter set, only matching band atoms selected"],
        ["test_empty_pool_returns_none", "Returns None (not crash) when no atoms available"],
        ["test_lexicographic_sort", "Available atoms sorted by atom_id before selection (reproducibility)"],
      ]
    ),
    spacer(80),

    heading("5.2.3 test_arc_loader.py", HeadingLevel.HEADING_3),
    simpleTable(
      ["Test Case", "What It Validates"],
      [
        ["test_valid_arc_loads", "A well-formed arc YAML loads without errors"],
        ["test_emotional_curve_length", "emotional_curve length must equal chapter_count"],
        ["test_role_plateau_detection", "Flags >2 consecutive identical emotional_role values"],
        ["test_first_chapter_recognition", "First emotional_role must be recognition (or opening_override)"],
        ["test_last_chapter_integration", "Last emotional_role must be integration"],
        ["test_invalid_role_rejected", "Unknown role name raises validation error"],
      ]
    ),
    spacer(80),

    heading("5.2.4 test_wave_orchestrator.py", HeadingLevel.HEADING_3),
    simpleTable(
      ["Test Case", "What It Validates"],
      [
        ["test_wave_diversity", "Selected wave passes wave_ok() constraints (<30% same arc, <40% same band, etc.)"],
        ["test_deterministic_with_seed", "Same seed + same candidates = same wave"],
        ["test_penalty_scoring", "Higher collision = higher penalty"],
        ["test_undersized_pool", "Gracefully returns smaller wave when candidates < wave_size"],
      ]
    ),
    spacer(80),

    heading("5.2.5 test_narrative_gates.py", HeadingLevel.HEADING_3),
    simpleTable(
      ["Test Case", "What It Validates"],
      [
        ["test_mechanism_escalation_pass", "Properly escalating book passes gate"],
        ["test_mechanism_escalation_flat_fail", "Flat-depth book fails with specific error"],
        ["test_cost_gradient_pass", "Escalating cost passes gate"],
        ["test_cost_premature_peak_fail", "Peak cost before midpoint fails"],
        ["test_callback_integrity_pass", "All setups have returns"],
        ["test_callback_orphaned_setup_fail", "Setup without return fails"],
        ["test_identity_monotonic_pass", "Non-decreasing identity stages pass"],
        ["test_identity_regression_fail", "Regression (self_claim then pre_awareness) fails"],
        ["test_macro_cadence_pass", "Varied intensity with regulation passes"],
        ["test_macro_cadence_burnout_fail", "3+ consecutive intensity=5 fails"],
      ]
    ),
    spacer(80),

    heading("5.2.6 test_pipeline_e2e.py", HeadingLevel.HEADING_3),
    para("End-to-end test that runs the full pipeline: CatalogPlanner \u2192 FormatSelector \u2192 ArcLoader \u2192 AssemblyCompiler \u2192 all validators \u2192 DupeEval. Uses a fixture persona\u00D7topic with enough atoms to compile a 12-chapter standard_book."),
    spacer(40),

    simpleTable(
      ["Test Case", "What It Validates"],
      [
        ["test_full_pipeline_succeeds", "Complete pipeline produces a valid CompiledBook"],
        ["test_full_pipeline_deterministic", "Two runs produce identical plan_hash"],
        ["test_validators_all_pass", "validate_compiled_plan + validate_arc_alignment + all narrative gates pass"],
        ["test_dupe_eval_first_book_passes", "First book in empty index always passes"],
      ]
    ),
    spacer(100),

    heading("5.3 Test Fixtures", HeadingLevel.HEADING_2),
    para("Create a minimal but complete test fixture set in tests/fixtures/:"),
    spacer(40),

    bullet("minimal_book_spec.yaml: persona=test_persona, topic=test_topic, teacher_mode=false"),
    bullet("minimal_format_plan.yaml: F006, 8 chapters, slot_definitions with HOOK/SCENE/STORY/REFLECTION/EXERCISE/INTEGRATION"),
    bullet("minimal_arc.yaml: 8-chapter arc with emotional_curve, role_sequence, cost_chapter_index, resolution_type"),
    bullet("sample_atoms/test_persona/test_topic/: 3 engines with 5 atoms each (40 total STORY atoms covering bands 1\u20135, with mechanism_depth, cost_type, cost_intensity, identity_stage, callback_id/phase metadata)"),
    bullet("sample_exercises/: 3 approved exercises covering grounding, regulation, integration cadence roles"),
    spacer(60),

    calloutBox(
      "CI COMMAND",
      "PYTHONPATH=. pytest tests/ -v --tb=short\nThis must pass on every commit. Add to Makefile as: make test",
      COLORS.success_bg, COLORS.success_border
    ),

    new Paragraph({ children: [new PageBreak()] }),
  ];
}

function buildDeliverables() {
  return [
    heading("6. Deliverables Checklist"),
    para("Dev is done when every box is checked. Items are ordered by dependency within each workstream."),
    spacer(80),

    heading("6.1 WS-1: Narrative Gates", HeadingLevel.HEADING_2),
    bullet("CANONICAL.txt parser extended to read MECHANISM_DEPTH, COST_TYPE, COST_INTENSITY, IDENTITY_STAGE, CALLBACK_ID, CALLBACK_PHASE"),
    bullet("atom_metadata_loader.py exposes new fields via PoolIndex"),
    bullet("tag_existing_atoms.py CLI works in interactive and batch mode"),
    bullet("mechanism_escalation_gate.py implemented with warn/fail modes"),
    bullet("cost_gradient_gate.py implemented with warn/fail modes"),
    bullet("callback_integrity_gate.py implemented with warn/fail modes"),
    bullet("identity_shift_gate.py implemented with warn/fail modes"),
    bullet("macro_cadence_gate.py implemented with warn/fail modes"),
    bullet("run_narrative_gates.py unified CI runner works"),
    bullet("All 5 gates pass on a manually-tagged test fixture"),
    spacer(80),

    heading("6.2 WS-2: Arc Blueprint Library", HeadingLevel.HEADING_2),
    bullet("10 arc template YAMLs in config/source_of_truth/master_arcs/templates/"),
    bullet("arc_generator.py produces concrete arcs from templates"),
    bullet("21+ concrete arcs generated for all active persona\u00D7topic combinations"),
    bullet("validate_arc_alignment.py extended to validate template compatibility"),
    bullet("Wave orchestrator tested with 21+ arcs and produces diverse 60-book waves"),
    spacer(80),

    heading("6.3 WS-3: Exercises + K-Tables", HeadingLevel.HEADING_2),
    bullet("26+ approved exercise variants across 11 types in SOURCE_OF_TRUTH/exercises_v4/approved/"),
    bullet("Exercise lint passes on all approved exercises"),
    bullet("K-table YAML files exist for all 15 formats (F001\u2013F015)"),
    bullet("validate_k_table.py checks pool depth before compilation"),
    bullet("Assembly compiler integration-tested with real exercises slotted into plans"),
    spacer(80),

    heading("6.4 WS-4: Test Suite", HeadingLevel.HEADING_2),
    bullet("Test fixtures created (book_spec, format_plan, arc, sample_atoms, sample_exercises)"),
    bullet("test_assembly_compiler.py: 10 test cases, all passing"),
    bullet("test_slot_resolver.py: 6 test cases, all passing"),
    bullet("test_arc_loader.py: 6 test cases, all passing"),
    bullet("test_wave_orchestrator.py: 4 test cases, all passing"),
    bullet("test_narrative_gates.py: 10 test cases, all passing"),
    bullet("test_pipeline_e2e.py: 4 test cases, all passing"),
    bullet("pytest tests/ passes with 0 failures"),
    bullet("make test added to Makefile"),

    new Paragraph({ children: [new PageBreak()] }),
  ];
}

function buildTimeline() {
  return [
    heading("7. Implementation Timeline"),
    spacer(60),

    simpleTable(
      ["Week", "Workstream", "Deliverables"],
      [
        ["1", "WS-4 (Fixtures) + WS-1 (Schema)", "Test fixtures, CANONICAL.txt parser extension, atom_metadata_loader, tag_existing_atoms.py"],
        ["2", "WS-1 (Gates 1\u20133)", "mechanism_escalation_gate, cost_gradient_gate, callback_integrity_gate + unit tests"],
        ["3", "WS-1 (Gates 4\u20135) + WS-2 (Templates)", "identity_shift_gate, macro_cadence_gate, run_narrative_gates.py, 10 arc templates, arc_generator.py"],
        ["4", "WS-2 (Concrete Arcs) + WS-3 (Exercises)", "21+ concrete arcs, exercise authoring + lint + approval, 26+ approved variants"],
        ["5", "WS-3 (K-Tables) + WS-4 (Full Suite)", "15 K-table YAMLs, validate_k_table.py, all test files, e2e pipeline test, CI integration"],
        ["6", "Atom Tagging + Gate Activation", "Content lead tags existing 68 atoms, gates switch from warn to fail mode, full CI green"],
      ]
    ),
    spacer(100),

    calloutBox(
      "DEPENDENCY ORDER",
      "WS-4 fixtures must come first (everything else tests against them). WS-1 schema changes must land before WS-2 arc templates (arcs reference the new metadata fields). WS-3 exercises can proceed in parallel with WS-1/WS-2 since they\u2019re independent content. Atom tagging (Week 6) is a content team task, not dev.",
      COLORS.light_bg, COLORS.muted
    ),
    spacer(100),

    heading("8. Acceptance Criteria"),
    para("The upgrade is complete when:"),
    spacer(40),

    numberedItem("A compiled plan for nyc_executives \u00D7 anxiety \u00D7 F006 passes all 5 narrative gates with zero errors"),
    numberedItem("The wave orchestrator produces a 60-book wave from 21+ arcs with all density constraints met"),
    numberedItem("An exercise is deterministically slotted into every EXERCISE slot using only approved exercises"),
    numberedItem("pytest tests/ exits 0 with \u226540 test cases passing"),
    numberedItem("No runtime code reads from candidate/, _stubs/, or human_seeds/"),
    numberedItem("make test && python -m tools.ci.run_narrative_gates --plan <any_plan> --mode fail exits 0"),
  ];
}

// ─── ASSEMBLE DOCUMENT ──────────────────────────────────────────

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: COLORS.primary },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 }
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: COLORS.primary },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 }
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: COLORS.accent },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 }
      },
    ]
  },
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      },
      {
        reference: "numbers",
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: PAGE_WIDTH, height: 15840 },
        margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          border: { bottom: { style: BorderStyle.SINGLE, size: 1, color: COLORS.border, space: 4 } },
          children: [
            new TextRun({ text: "Phoenix V4 \u2014 Narrative Intelligence Dev Spec", size: 16, font: "Arial", color: COLORS.muted }),
          ]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "Page ", size: 16, font: "Arial", color: COLORS.muted }),
            new TextRun({ children: [PageNumber.CURRENT], size: 16, font: "Arial", color: COLORS.muted }),
          ]
        })]
      })
    },
    children: [
      ...buildTitlePage(),
      ...buildOverview(),
      ...buildWS1(),
      ...buildWS2(),
      ...buildWS3(),
      ...buildWS4(),
      ...buildDeliverables(),
      ...buildTimeline(),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  const outPath = "/sessions/busy-vibrant-maxwell/mnt/phoenix_omega/PHOENIX_V4_NARRATIVE_INTELLIGENCE_DEV_SPEC.docx";
  fs.writeFileSync(outPath, buffer);
  console.log("Wrote:", outPath);
});
