# Phoenix Control — Native macOS Control Plane

Native Swift/SwiftUI macOS app for the Phoenix Omega repo: multi-tab control plane (Dashboard, Pipeline, Simulation, Tests, Observability, Gates & Release, Pearl News, Teacher, CI/Workflows, Docs & Config).

## Build and run

1. Open **Xcode** (full Xcode required, not only Command Line Tools).
2. Open project: `PhoenixControl.xcodeproj` (from this directory).
3. Select scheme **Phoenix Control**, destination **My Mac**.
4. **Product → Clean Build Folder** (⇧⌘K), then **Product → Build** (⌘B). (Clean ensures the real app executable is built, not only preview artifacts.)
5. Run from Xcode: **Product → Run** (⌘R).

Minimum: macOS 13.0, Xcode 14+.

**If the app says "executable is missing" or "damaged":** The bundle had only preview artifacts. In Xcode do **Product → Clean Build Folder** (⇧⌘K), then **Product → Build** (⌘B), then run `./PhoenixControl/install-to-applications.sh` again.

## Launch from Finder and keep in Dock

- **Build a copy you can open from Finder:** In Xcode, **Product → Build** (⌘B). The app is created at:
  - **Debug:** `~/Library/Developer/Xcode/DerivedData/PhoenixControl-*/Build/Products/Debug/Phoenix Control.app`
  - To run from Finder, drag **Phoenix Control.app** to **Applications** (or any folder), then double‑click it. The app will appear in the Dock while it’s running.
- **Keep in Dock:** After launching, right‑click the app’s icon in the Dock → **Options → Keep in Dock**. The icon stays in the Dock so you can launch it with one click.
- **Optional — install to Applications:** After building in Xcode, from the repo root run:
  - `./PhoenixControl/install-to-applications.sh` — copies the built app to `/Applications/` so you can open **Phoenix Control** from Finder and add it to the Dock.
  - Or use **Product → Archive** in Xcode, then **Distribute App → Copy App** to get a standalone `.app` to drag to Applications.

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
