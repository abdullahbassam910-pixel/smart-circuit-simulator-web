
# SMART CIRCUIT SIMULATOR PRO v6.3

SMART CIRCUIT SIMULATOR PRO is a Tkinter-based circuit builder and solver.
Version 6.3 keeps the modular simulation behavior while polishing the workspace
with a more professional UI layer.

## What v6.3 Contains

- Component drawing for resistors, batteries, diodes, capacitors, and ground.
- Wire management with component pin registration and refresh helpers.
- Node management with union-find based connectivity.
- DC and transient simulation through the circuit solver.
- Validation reports, result text output, and lightweight graph rendering.
- A modular UI split across layout, toolbar, events, properties, and canvas code.
- Professional two-level canvas grid with major and minor lines.
- Left component palette, top quick-action toolbar, and theme toggle.
- Dark, light, pro blue, and neon theme modes.
- Improved component hover and selection visuals.
- Step 2 component-system polish with pin markers, smooth drag, snap-on-release, and right-click menus.
- Step 3 Wire System PRO with auto routing, live updates, curved wires, expanded colors, and junction dots.

## Project Layout

- `main.py` starts the application and configures the root window.
- `components/` contains drawable circuit components.
- `core/` contains circuit, wire, node, serialization, and solver logic.
- `simulation/` contains validation and report generation.
- `ui/` contains the Tkinter user interface modules.
- `tests/` contains lightweight regression tests for core behavior.
- `docs/` contains release notes and the roadmap.

## Run

```powershell
python main.py
```

## Run Web Demo

```powershell
streamlit run streamlit_app.py
```

The web demo is intended for online presentation. It reuses the Python solver
engine from `core/` and exposes ready-to-run circuit presets, validation,
simulation results, node voltages, component current, power, and transient
snapshots.

## Deploy Web Demo

1. Push this project to a GitHub repository.
2. Open Streamlit Community Cloud.
3. Create a new app from the repository.
4. Use `streamlit_app.py` as the entrypoint file.
5. Deploy and share the generated `streamlit.app` URL.

## Test

```powershell
python -m unittest discover -s tests
```

## Notes

The UI is intentionally dependency-light. `numpy` is the only runtime dependency
listed in `requirements.txt`.
