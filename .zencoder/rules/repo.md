---
description: Repository Information Overview
alwaysApply: true
---

# Phoenix Omega / V4 Information

## Summary
**Phoenix Omega** (also referred to as Phoenix V4) is a highly opinionated **content assembly system** designed to scale human-written therapeutic journeys without the use of generative AI for prose. The system decomposes human-authored content into "atoms," "scenes," and "exercises," which are then reassembled at runtime based on specific personas, topics, and narrative rules. The core philosophy is: **Humans create meaning, machines enforce structure, and runtime only assembles.**

## Structure
The repository is currently in a **specification and handoff phase**, containing raw source material, legacy data, and comprehensive architectural specifications.

- **Root Level**: Contains core specifications (`REBUILD_README.txt`, `phoenix_rebuild_spec.txt`), architectural documents (`SCENE_INJECTION_ARCHITECTURE.md`), and raw content data (`unified_personas.txt`, `somatic_exercises.txt`).
- **Archive Files**: Multiple `.zip` files (e.g., `files.zip`) contain developer handoff materials, content team specs, and initial JSON-based asset samples.
- **Workflows**: `.zencoder/workflows` and `.zenflow/workflows` directories for automated task handling.
- **Intended Layout**:
    - `SOURCE_OF_TRUTH/`: Canonical location for `approved/`, `candidate/`, and `packs/` of exercises and atoms.
    - `docs/`: Configuration and policy files (e.g., `EXERCISE_SLOT_POLICY.yaml`).
    - `tools/`: Planned Python-based utilities for linting, importing, and approval.

## Specification & Tools
**Type**: Content Assembly & Specification Repository  
**Version**: Phoenix V4 (Scene Injection 1.0)  
**Required Tools**: 
- **Python 3**: For planned linting and conversion tools (`tools/exercise_lint/`, `tools/exercise_import/`).
- **YAML/JSON**: Core formats for structured content and schemas.
- **Markdown**: For technical specifications and architectural maps.

## Key Resources
**Main Files**:
- [./REBUILD_README.txt](./REBUILD_README.txt): The authoritative system overview and build guide.
- [./phoenix_rebuild_spec.txt](./phoenix_rebuild_spec.txt): Detailed developer specification for the Exercise System.
- [./SCENE_INJECTION_ARCHITECTURE.md](./SCENE_INJECTION_ARCHITECTURE.md): Specification for the Scene Injection system and socket maps.
- [./unified_personas.txt](./unified_personas.txt): Central repository of persona definitions and variables.
- [./persona_topic_variables.schema.yaml](./persona_topic_variables.schema.yaml): YAML schema for validating persona and topic variables.

**Configuration Structure**:
- **Exercise System**: Uses a four-section YAML structure: `intro`, `guided_practice`, `aha_noticing`, and `integration`.
- **Scene Sockets**: Defined locations (`{scene_XX}`) in master text where persona-specific content is injected.
- **Validation Gates**: Hard-coded rules preventing "toxic positivity," "resolution language," or "medical advice."

## Usage & Operations
**Key Commands (Planned/Conceptual)**:
```bash
# Exercise Linting (planned)
PYTHONPATH=. python3 tools/exercise_lint/lint_exercise.py --file path/to/exercise.yaml

# Legacy Import (planned)
PYTHONPATH=. python3 tools/exercise_import/import_legacy_exercises.py --input /path/to/legacy --output SOURCE_OF_TRUTH/exercises_v4/candidate

# Asset Approval (planned)
python3 tools/exercise_approval/exercise_approve.py approve --id ex_id --by "author"
```

**Integration Points**:
- **Runtime Assembler**: The core "Phoenix V4 Assembler" (external or planned) consumes the `approved/` assets.
- **Location Hydrator**: Injects location-specific variables into exercise and scene placeholders.

## Validation
**Quality Checks**:
- **Hard Lint Gates**: Exercises must pass structural and voice checks (2nd person, present tense, no resolution).
- **CI Guards**: Verification that only `approved` status assets are accessible by the runtime assembly engine.
- **Schema Validation**: Ensuring all assets conform to `persona_topic_variables.schema.yaml`.

## Troubleshooting
### Bun Runtime Crash (Illegal Instruction)
If the `zencoder` or `zenflow` tools crash with `panic: Illegal instruction`, it is likely a Bun runtime issue on macOS.
1. **Check Architecture**: Ensure you aren't running an `x64` version of Bun on `arm64` (Apple Silicon).
2. **Upgrade Bun**: Run `bun upgrade` to move past v1.3.7.
3. **Disable AVX**: If on an older Intel Mac, try `BUN_NO_AVX=1` before the command.
4. **Python Core**: Remember that **Phoenix V4** logic is Python-based; Bun crashes do not affect the content assembly logic itself.

**Testing Approach**:
- **Unit Testing**: Planned for the Python-based tools.
- **Validation Gates**: Automated checks for narrative arc completeness, persona violation, and cadence breaks during the assembly process.
