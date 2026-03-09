const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        AlignmentType, LevelFormat, BorderStyle, WidthType, ShadingType,
        HeadingLevel, PageBreak } = require("docx");

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

function cell(text, opts = {}) {
  const width = opts.width || 4680;
  const bold = opts.bold || false;
  const shading = opts.shading ? { fill: opts.shading, type: ShadingType.CLEAR } : undefined;
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA }, margins: cellMargins, shading,
    children: [new Paragraph({ children: [new TextRun({ text, bold, font: "Arial", size: 22 })] })]
  });
}

function heading(text) {
  return new Paragraph({
    spacing: { before: 300, after: 120 },
    children: [new TextRun({ text, bold: true, font: "Arial", size: 28, color: "1A1A2E" })]
  });
}

function para(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 120 },
    children: [new TextRun({ text, font: "Arial", size: 22, bold: opts.bold || false, color: opts.color || "333333" })]
  });
}

function bulletItem(text, ref) {
  return new Paragraph({
    numbering: { reference: ref, level: 0 },
    spacing: { after: 80 },
    children: [new TextRun({ text, font: "Arial", size: 22 })]
  });
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers2", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers3", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers4", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers5", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "bullets2", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [
      // Header
      new Paragraph({
        spacing: { after: 60 },
        children: [new TextRun({ text: "GHL Onboarding: FreeMe Funnel System", bold: true, font: "Arial", size: 36, color: "1A1A2E" })]
      }),
      new Paragraph({
        spacing: { after: 300 },
        children: [new TextRun({ text: "Setup instructions for GoHighLevel admin", font: "Arial", size: 24, color: "666666", italics: true })]
      }),

      // Greeting
      para("Hi Ma\u2019at,"),
      new Paragraph({ spacing: { after: 120 }, children: [] }),
      para("We\u2019re launching the FreeMe freebie funnel system. It captures leads through breathing exercise landing pages, pushes them into GHL as contacts, and runs a 4-email Proof Loop sequence that nurtures them toward a book purchase."),
      para("Below is everything you need to set up on the GHL side. The app handles form capture, lead storage, and (depending on email mode) email sending. Your job is to make sure GHL is ready to receive contacts and, if we go with GHL-managed emails, build the automation sequence."),
      new Paragraph({ spacing: { after: 60 }, children: [] }),

      // ============ STEP 1 ============
      heading("Step 1: API Key and Location ID (required)"),
      para("We need these two credentials so the app can push contacts into GHL."),
      new Paragraph({
        numbering: { reference: "numbers", level: 0 }, spacing: { after: 80 },
        children: [new TextRun({ text: "Go to Settings \u2192 Business Profile \u2192 copy the ", font: "Arial", size: 22 }), new TextRun({ text: "Location ID", bold: true, font: "Arial", size: 22 }), new TextRun({ text: " (the sub-account ID, not the agency ID).", font: "Arial", size: 22 })]
      }),
      new Paragraph({
        numbering: { reference: "numbers", level: 0 }, spacing: { after: 80 },
        children: [new TextRun({ text: "Go to Settings \u2192 API \u2192 create an ", font: "Arial", size: 22 }), new TextRun({ text: "API Key 2.0", bold: true, font: "Arial", size: 22 }), new TextRun({ text: ". Name it something like \u201CFreeMe Funnel\u201D.", font: "Arial", size: 22 })]
      }),
      new Paragraph({
        numbering: { reference: "numbers", level: 0 }, spacing: { after: 80 },
        children: [new TextRun({ text: "Send both values to me securely (not in plain email \u2014 use a password manager share or encrypted note).", font: "Arial", size: 22 })]
      }),
      new Paragraph({ spacing: { after: 60 }, children: [] }),

      // ============ STEP 2 ============
      heading("Step 2: Create Custom Fields (required)"),
      para("The app sends structured data with each contact. GHL needs matching custom fields to receive it."),
      para("This is the most common failure point: GHL custom fields use UUIDs internally, not human-readable names. If the field IDs are wrong, data silently drops.", { bold: true }),
      new Paragraph({ spacing: { after: 80 }, children: [] }),
      para("Go to Settings \u2192 Custom Fields and create these three fields:"),
      new Paragraph({ spacing: { after: 60 }, children: [] }),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2200, 2200, 4960],
        rows: [
          new TableRow({ children: [
            cell("Field Name", { width: 2200, bold: true, shading: "1A1A2E" }),
            cell("Field Type", { width: 2200, bold: true, shading: "1A1A2E" }),
            cell("Purpose", { width: 4960, bold: true, shading: "1A1A2E" }),
          ].map((c, i) => {
            // Override text color to white for header
            return new TableCell({
              borders, width: { size: [2200,2200,4960][i], type: WidthType.DXA }, margins: cellMargins,
              shading: { fill: "1A1A2E", type: ShadingType.CLEAR },
              children: [new Paragraph({ children: [new TextRun({ text: ["Field Name","Field Type","Purpose"][i], bold: true, font: "Arial", size: 22, color: "FFFFFF" })] })]
            });
          }) }),
          new TableRow({ children: [cell("topic", { width: 2200 }), cell("Single-line text", { width: 2200 }), cell("Which funnel hub (e.g. burnout, anxiety, sleep)", { width: 4960 })] }),
          new TableRow({ children: [cell("exercise", { width: 2200 }), cell("Single-line text", { width: 2200 }), cell("Which exercise the lead chose (e.g. cyclic_sighing)", { width: 4960 })] }),
          new TableRow({ children: [cell("persona", { width: 2200 }), cell("Single-line text", { width: 2200 }), cell("Optional \u2014 if we add a \u201CI work as\u2026\u201D dropdown later", { width: 4960 })] }),
        ]
      }),
      new Paragraph({ spacing: { after: 120 }, children: [] }),

      para("After creating each field, click into it and copy the UUID from the URL or field details. Send me all three UUIDs. Example format:"),
      para("topic: aB1cD2eF3gH4iJ5kL6mN", { bold: true }),
      para("exercise: xY7zA8bC9dE0fG1hI2jK", { bold: true }),
      para("persona: mN3oP4qR5sT6uV7wX8yZ", { bold: true }),
      new Paragraph({ spacing: { after: 60 }, children: [] }),

      // ============ STEP 3 ============
      heading("Step 3: Create Tags (recommended)"),
      para("Tags let us segment contacts and trigger automations. Create these tags in GHL:"),
      new Paragraph({ spacing: { after: 60 }, children: [] }),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [3500, 5860],
        rows: [
          new TableRow({ children: [
            new TableCell({ borders, width: { size: 3500, type: WidthType.DXA }, margins: cellMargins, shading: { fill: "1A1A2E", type: ShadingType.CLEAR },
              children: [new Paragraph({ children: [new TextRun({ text: "Tag", bold: true, font: "Arial", size: 22, color: "FFFFFF" })] })] }),
            new TableCell({ borders, width: { size: 5860, type: WidthType.DXA }, margins: cellMargins, shading: { fill: "1A1A2E", type: ShadingType.CLEAR },
              children: [new Paragraph({ children: [new TextRun({ text: "When applied", bold: true, font: "Arial", size: 22, color: "FFFFFF" })] })] }),
          ] }),
          new TableRow({ children: [cell("funnel_burnout_reset", { width: 3500 }), cell("Every lead from the burnout funnel", { width: 5860 })] }),
          new TableRow({ children: [cell("topic_burnout", { width: 3500 }), cell("Burnout hub leads (we\u2019ll add topic_anxiety etc. later)", { width: 5860 })] }),
          new TableRow({ children: [cell("exercise_cyclic_sighing", { width: 3500 }), cell("Lead chose cyclic sighing as their exercise", { width: 5860 })] }),
        ]
      }),
      new Paragraph({ spacing: { after: 120 }, children: [] }),
      para("As we add more topic hubs (anxiety, sleep, etc.), we\u2019ll add matching tags following the same pattern."),
      new Paragraph({ spacing: { after: 60 }, children: [] }),

      // ============ STEP 4 ============
      heading("Step 4: Email Automation (if GHL sends emails)"),
      para("There are two modes. I\u2019ll confirm which we\u2019re using, but here\u2019s what each means for you:"),
      new Paragraph({ spacing: { after: 80 }, children: [] }),

      para("Mode A: App sends emails (Brevo SMTP)", { bold: true }),
      bulletItem("You don\u2019t need to build any email automation in GHL.", "bullets"),
      bulletItem("The app handles the full 4-email sequence with scheduling.", "bullets"),
      bulletItem("GHL is just the CRM / contact store. You can still build workflows triggered by tags if you want.", "bullets"),
      new Paragraph({ spacing: { after: 120 }, children: [] }),

      para("Mode B: GHL sends emails", { bold: true }),
      bulletItem("Build a GHL automation workflow triggered by: Contact Created + has tag funnel_burnout_reset.", "bullets2"),
      bulletItem("The automation sends 4 emails in sequence (the Proof Loop). I\u2019ll provide the exact copy.", "bullets2"),
      new Paragraph({ spacing: { after: 80 }, children: [] }),

      para("Proof Loop email sequence (timing is critical):"),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [1200, 1800, 6360],
        rows: [
          new TableRow({ children: [
            new TableCell({ borders, width: { size: 1200, type: WidthType.DXA }, margins: cellMargins, shading: { fill: "1A1A2E", type: ShadingType.CLEAR },
              children: [new Paragraph({ children: [new TextRun({ text: "Email", bold: true, font: "Arial", size: 22, color: "FFFFFF" })] })] }),
            new TableCell({ borders, width: { size: 1800, type: WidthType.DXA }, margins: cellMargins, shading: { fill: "1A1A2E", type: ShadingType.CLEAR },
              children: [new Paragraph({ children: [new TextRun({ text: "Timing", bold: true, font: "Arial", size: 22, color: "FFFFFF" })] })] }),
            new TableCell({ borders, width: { size: 6360, type: WidthType.DXA }, margins: cellMargins, shading: { fill: "1A1A2E", type: ShadingType.CLEAR },
              children: [new Paragraph({ children: [new TextRun({ text: "Content", bold: true, font: "Arial", size: 22, color: "FFFFFF" })] })] }),
          ] }),
          new TableRow({ children: [cell("E1", { width: 1200 }), cell("Immediate", { width: 1800 }), cell("First breathing exercise (the one they chose on the form)", { width: 6360 })] }),
          new TableRow({ children: [cell("E2", { width: 1200 }), cell("+24 hours", { width: 1800 }), cell("Second exercise (complementary technique \u2014 I\u2019ll specify which)", { width: 6360 })] }),
          new TableRow({ children: [cell("E3", { width: 1200 }), cell("+72 hours", { width: 1800 }), cell("Transformation story (real person, anonymized)", { width: 6360 })] }),
          new TableRow({ children: [cell("E4", { width: 1200 }), cell("+48h after E3", { width: 1800 }), cell("Book recommendation \u2014 minimum 48-hour gap from story email", { width: 6360 })] }),
        ]
      }),
      new Paragraph({ spacing: { after: 120 }, children: [] }),
      para("Important: The 48-hour minimum gap between E3 (story) and E4 (book offer) is non-negotiable. The Proof Loop psychology requires two micro-relief experiences before the offer.", { bold: true }),
      para("Every email must include an unsubscribe link and CAN-SPAM compliant footer with physical mailing address."),
      new Paragraph({ spacing: { after: 60 }, children: [] }),

      // ============ STEP 5 ============
      heading("Step 5: CAN-SPAM Compliance"),
      para("Every email (whether sent by the app or GHL) needs a physical mailing address in the footer. Please confirm which address we\u2019re using so I can add it to the email templates and you can set it in GHL."),
      new Paragraph({ spacing: { after: 60 }, children: [] }),

      // ============ STEP 6 ============
      heading("Step 6: End-to-End Test (required before go-live)"),
      para("Before we go live, we need to run through this checklist together:"),
      new Paragraph({ spacing: { after: 60 }, children: [] }),

      new Paragraph({ numbering: { reference: "numbers2", level: 0 }, spacing: { after: 80 },
        children: [new TextRun({ text: "Submit the form with a real email address.", font: "Arial", size: 22 })] }),
      new Paragraph({ numbering: { reference: "numbers2", level: 0 }, spacing: { after: 80 },
        children: [new TextRun({ text: "Confirm the contact appears in GHL with correct custom field values (topic, exercise) and tags.", font: "Arial", size: 22 })] }),
      new Paragraph({ numbering: { reference: "numbers2", level: 0 }, spacing: { after: 80 },
        children: [new TextRun({ text: "If SMTP mode: confirm Email 1 arrives immediately, and Emails 2\u20135 are scheduled.", font: "Arial", size: 22 })] }),
      new Paragraph({ numbering: { reference: "numbers2", level: 0 }, spacing: { after: 80 },
        children: [new TextRun({ text: "If GHL mode: confirm the automation triggers and emails send on schedule.", font: "Arial", size: 22 })] }),
      new Paragraph({ numbering: { reference: "numbers2", level: 0 }, spacing: { after: 80 },
        children: [new TextRun({ text: "Click the unsubscribe link and confirm it works (contact is suppressed, no more emails).", font: "Arial", size: 22 })] }),
      new Paragraph({ numbering: { reference: "numbers2", level: 0 }, spacing: { after: 80 },
        children: [new TextRun({ text: "Check that custom field UUIDs are mapping correctly (this is the #1 failure point).", font: "Arial", size: 22 })] }),
      new Paragraph({ spacing: { after: 60 }, children: [] }),

      // ============ WHAT I NEED FROM YOU ============
      heading("What I Need From You"),
      para("To summarize, here\u2019s the deliverables list:"),
      new Paragraph({ spacing: { after: 60 }, children: [] }),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [800, 5060, 1800, 1700],
        rows: [
          new TableRow({ children: [
            new TableCell({ borders, width: { size: 800, type: WidthType.DXA }, margins: cellMargins, shading: { fill: "1A1A2E", type: ShadingType.CLEAR },
              children: [new Paragraph({ children: [new TextRun({ text: "#", bold: true, font: "Arial", size: 22, color: "FFFFFF" })] })] }),
            new TableCell({ borders, width: { size: 5060, type: WidthType.DXA }, margins: cellMargins, shading: { fill: "1A1A2E", type: ShadingType.CLEAR },
              children: [new Paragraph({ children: [new TextRun({ text: "Item", bold: true, font: "Arial", size: 22, color: "FFFFFF" })] })] }),
            new TableCell({ borders, width: { size: 1800, type: WidthType.DXA }, margins: cellMargins, shading: { fill: "1A1A2E", type: ShadingType.CLEAR },
              children: [new Paragraph({ children: [new TextRun({ text: "Priority", bold: true, font: "Arial", size: 22, color: "FFFFFF" })] })] }),
            new TableCell({ borders, width: { size: 1700, type: WidthType.DXA }, margins: cellMargins, shading: { fill: "1A1A2E", type: ShadingType.CLEAR },
              children: [new Paragraph({ children: [new TextRun({ text: "Blocks", bold: true, font: "Arial", size: 22, color: "FFFFFF" })] })] }),
          ] }),
          new TableRow({ children: [cell("1", { width: 800 }), cell("API Key 2.0 + Location ID", { width: 5060 }), cell("Required", { width: 1800 }), cell("Everything", { width: 1700 })] }),
          new TableRow({ children: [cell("2", { width: 800 }), cell("Custom field UUIDs (topic, exercise, persona)", { width: 5060 }), cell("Required", { width: 1800 }), cell("Contact data", { width: 1700 })] }),
          new TableRow({ children: [cell("3", { width: 800 }), cell("Tags created (funnel_burnout_reset, topic_burnout, exercise_cyclic_sighing)", { width: 5060 }), cell("Recommended", { width: 1800 }), cell("Segmentation", { width: 1700 })] }),
          new TableRow({ children: [cell("4", { width: 800 }), cell("CAN-SPAM physical address", { width: 5060 }), cell("Required", { width: 1800 }), cell("Go-live", { width: 1700 })] }),
          new TableRow({ children: [cell("5", { width: 800 }), cell("Email automation (if GHL mode)", { width: 5060 }), cell("If applicable", { width: 1800 }), cell("Email delivery", { width: 1700 })] }),
          new TableRow({ children: [cell("6", { width: 800 }), cell("End-to-end test with me", { width: 5060 }), cell("Required", { width: 1800 }), cell("Go-live", { width: 1700 })] }),
        ]
      }),
      new Paragraph({ spacing: { after: 200 }, children: [] }),

      // ============ FUTURE HUBS ============
      heading("Looking Ahead"),
      para("This exact same setup scales to future topic hubs (anxiety, sleep, etc.). Each new hub reuses the same GHL structure \u2014 we just add new tags (topic_anxiety, exercise_box_breathing, etc.) and a new automation workflow if you\u2019re running GHL emails. The custom fields and API setup are one-time."),
      new Paragraph({ spacing: { after: 120 }, children: [] }),

      para("Let me know once you have the API key, Location ID, and custom field UUIDs and we\u2019ll schedule the test run."),
      new Paragraph({ spacing: { after: 200 }, children: [] }),
      para("Nihala"),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/sessions/eager-trusting-brahmagupta/mnt/phoenix_omega/GHL_Admin_Onboarding_Email.docx", buffer);
  console.log("Done");
});
