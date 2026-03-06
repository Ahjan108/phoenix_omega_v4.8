# Phoenix Control — Native macOS Control Plane

Native Swift/SwiftUI macOS app for the Phoenix Omega repo: multi-tab control plane (Dashboard, Pipeline, Simulation, Tests, Observability, Gates & Release, Pearl News, Teacher, CI/Workflows, Docs & Config).

## Build and run

1. Open **Xcode** (full Xcode required, not only Command Line Tools).
2. Open project: `PhoenixControl.xcodeproj` (from this directory).
3. Select scheme **Phoenix Control**, destination **My Mac**.
4. Build and run: **Product → Run** (or ⌘R).

Minimum: macOS 13.0, Xcode 14+.

## First launch

On first launch the app shows **Open Settings** until a valid **repo path** is set (e.g. the root of the `phoenix_omega` repo). The startup health check requires:

- Repo path set and directory exists
- `scripts/` present
- `artifacts/observability/` present or creatable
- Python 3 on `PATH`

Set the path via the folder button in the toolbar or the initial **Open Settings** button.

## Spec and docs

- Design: see plan **Phoenix Omega — Native macOS Control Plane App** and [docs/DOCS_INDEX.md](../docs/DOCS_INDEX.md) (control plane bundle). For CI/Workflows tab and GitHub (both repos, runner, PR flow): DOCS_INDEX → [GitHub Operations Framework](../docs/DOCS_INDEX.md#github-operations-framework).
- Error state UX: [docs/PHOENIX_OMEGA_ERROR_STATE_UX_SPEC.md](../docs/PHOENIX_OMEGA_ERROR_STATE_UX_SPEC.md).
