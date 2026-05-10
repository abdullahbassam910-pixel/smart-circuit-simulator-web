from types import SimpleNamespace

import streamlit as st

from core.node_manager import NodeManager
from core.solver import CircuitSolver
from simulation.analyzer import SimulationAnalyzer
from simulation.validator import CircuitValidator


APP_NAME = "SMART CIRCUIT SIMULATOR PRO"
APP_VERSION = "6.3 Web Demo"


COMPONENT_STYLES = {
    "Ground": {"color": "#8aa0b8", "icon": "GND"},
    "Battery": {"color": "#2dd4bf", "icon": "DC"},
    "ACSource": {"color": "#38bdf8", "icon": "AC"},
    "CurrentSource": {"color": "#a78bfa", "icon": "I"},
    "Resistor": {"color": "#f59e0b", "icon": "R"},
    "LED": {"color": "#fb7185", "icon": "LED"},
    "Switch": {"color": "#f97316", "icon": "SW"},
    "Transistor": {"color": "#e879f9", "icon": "Q"},
}


PRESETS = {
    "Basic DC resistor circuit": {
        "description": "Battery, resistor, and ground loop for Ohm's law simulation.",
        "analysis": "dc",
        "components": [
            ("g1", "Ground", 0.0, {}),
            ("b1", "Battery", 10.0, {}),
            ("r1", "Resistor", 1000.0, {}),
        ],
        "wires": [("g1", 1, "b1", 1), ("b1", 2, "r1", 1), ("r1", 2, "g1", 2)],
    },
    "LED indicator circuit": {
        "description": "Battery, current-limiting resistor, LED, and ground.",
        "analysis": "dc",
        "components": [
            ("g1", "Ground", 0.0, {}),
            ("b1", "Battery", 5.0, {}),
            ("r1", "Resistor", 1000.0, {}),
            ("l1", "LED", 2.0, {}),
        ],
        "wires": [("g1", 1, "b1", 1), ("b1", 2, "r1", 1), ("r1", 2, "l1", 1), ("l1", 2, "g1", 2)],
    },
    "Switch-controlled load": {
        "description": "Closed or open switch controlling a resistor load.",
        "analysis": "dc",
        "components": [
            ("g1", "Ground", 0.0, {}),
            ("b1", "Battery", 5.0, {}),
            ("s1", "Switch", 1.0, {}),
            ("r1", "Resistor", 1000.0, {}),
        ],
        "wires": [("g1", 1, "b1", 1), ("b1", 2, "s1", 1), ("s1", 2, "r1", 1), ("r1", 2, "g1", 2)],
    },
    "AC transient resistor": {
        "description": "AC source with transient stepping into a resistor load.",
        "analysis": "transient",
        "components": [
            ("g1", "Ground", 0.0, {}),
            ("ac1", "ACSource", 10.0, {"frequency": 50.0, "phase": 0.0}),
            ("r1", "Resistor", 1000.0, {}),
        ],
        "wires": [("g1", 1, "ac1", 1), ("ac1", 2, "r1", 1), ("r1", 2, "g1", 2)],
    },
    "Current source load": {
        "description": "Independent current source driving a resistor.",
        "analysis": "dc",
        "components": [
            ("g1", "Ground", 0.0, {}),
            ("i1", "CurrentSource", -0.01, {}),
            ("r1", "Resistor", 1000.0, {}),
        ],
        "wires": [("i1", 1, "r1", 1), ("r1", 2, "g1", 1), ("i1", 2, "g1", 2)],
    },
    "NPN transistor switch": {
        "description": "Simplified NPN switch model with a base-drive source.",
        "analysis": "dc",
        "components": [
            ("g1", "Ground", 0.0, {}),
            ("b1", "Battery", 5.0, {}),
            ("b2", "Battery", 1.0, {}),
            ("r1", "Resistor", 1000.0, {}),
            ("q1", "Transistor", 100.0, {"PIN_COUNT": 3}),
        ],
        "wires": [
            ("g1", 1, "b1", 1),
            ("b1", 2, "r1", 1),
            ("r1", 2, "q1", 1),
            ("q1", 3, "g1", 2),
            ("g1", 1, "b2", 1),
            ("b2", 2, "q1", 2),
        ],
    },
}


def apply_page_style():
    st.set_page_config(page_title=APP_NAME, page_icon="assets/icons/resistor.png", layout="wide")
    st.markdown(
        """
        <style>
        .stApp { background: linear-gradient(180deg, #111827 0%, #0f172a 48%, #101820 100%); }
        .block-container { padding-top: 1.2rem; max-width: 1380px; }
        h1, h2, h3 { letter-spacing: 0; }
        [data-testid="stMetric"] {
            background: rgba(23, 29, 41, .82);
            border: 1px solid rgba(148, 163, 184, .18);
            border-radius: 8px;
            padding: 14px 16px;
        }
        [data-testid="stSidebar"] {
            background: #0f172a;
            border-right: 1px solid rgba(148, 163, 184, .14);
        }
        .hero {
            border-bottom: 1px solid rgba(148, 163, 184, .18);
            padding: 4px 0 16px 0;
            margin-bottom: 14px;
        }
        .kicker { color: #2dd4bf; font-size: .86rem; font-weight: 700; text-transform: uppercase; }
        .subtitle { color: #98a6ba; margin-top: -8px; max-width: 860px; }
        .circuit-board {
            background:
                linear-gradient(rgba(148, 163, 184, .07) 1px, transparent 1px),
                linear-gradient(90deg, rgba(148, 163, 184, .07) 1px, transparent 1px),
                #121923;
            background-size: 28px 28px;
            border: 1px solid rgba(148, 163, 184, .18);
            border-radius: 8px;
            min-height: 366px;
            padding: 22px;
            overflow: hidden;
        }
        .row { display: flex; align-items: center; gap: 0; margin-bottom: 24px; }
        .wire {
            height: 3px;
            background: #67e8f9;
            box-shadow: 0 0 12px rgba(103, 232, 249, .42);
            flex: 1 1 44px;
            min-width: 38px;
        }
        .part {
            width: 94px;
            min-height: 82px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, .16);
            background: #172033;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-shadow: inset 0 0 0 1px rgba(255, 255, 255, .03);
        }
        .part strong { display: block; color: #f8fafc; font-size: .9rem; line-height: 1.2; }
        .part span { color: #a7b5c8; font-size: .75rem; margin-top: 4px; }
        .chip {
            width: 36px;
            height: 28px;
            border-radius: 6px;
            display: grid;
            place-items: center;
            font-size: .7rem;
            font-weight: 800;
            color: #071018;
            margin-bottom: 8px;
        }
        .note { color: #a7b5c8; font-size: .9rem; }
        .status-ok {
            border-left: 4px solid #22c55e;
            padding: 10px 12px;
            background: rgba(34, 197, 94, .10);
            border-radius: 7px;
        }
        .status-bad {
            border-left: 4px solid #ef4444;
            padding: 10px 12px;
            background: rgba(239, 68, 68, .10);
            border-radius: 7px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def create_component(comp_id, comp_type, value, extras=None):
    extras = dict(extras or {})
    pin_count = int(extras.pop("PIN_COUNT", 2))
    data = {"id": comp_id, "comp_type": comp_type, "value": float(value), "deleted": False, "PIN_COUNT": pin_count}
    data.update(extras)
    return SimpleNamespace(**data)


def build_circuit(preset, overrides):
    components = []
    by_id = {}
    for comp_id, comp_type, default_value, extras in preset["components"]:
        comp = create_component(comp_id, comp_type, overrides.get(comp_id, default_value), extras)
        components.append(comp)
        by_id[comp_id] = comp

    wires = []
    for index, (start_id, start_pin, end_id, end_pin) in enumerate(preset["wires"], start=1):
        wires.append(
            SimpleNamespace(
                id=f"w{index}",
                start_comp=by_id[start_id],
                start_pin=start_pin,
                end_comp=by_id[end_id],
                end_pin=end_pin,
                deleted=False,
            )
        )
    return components, wires


def run_solver(components, wires, analysis_mode, time_step, transient_steps):
    validation = CircuitValidator().validate(components, wires)
    solver = CircuitSolver()
    solver.set_node_manager(NodeManager())
    analyzer = SimulationAnalyzer(solver)
    result = analyzer.run_analysis(
        components,
        wires,
        analysis_mode=analysis_mode,
        time_step=time_step,
        transient_steps=transient_steps,
    )
    return validation, result, analyzer


def component_value_label(comp):
    value = f"{comp.value:g}"
    if comp.comp_type == "Resistor":
        return f"{value} ohm"
    if comp.comp_type in ("Battery", "LED", "ACSource"):
        return f"{value} V"
    if comp.comp_type == "CurrentSource":
        return f"{value} A"
    if comp.comp_type == "Switch":
        return "Closed" if comp.value >= 0.5 else "Open"
    if comp.comp_type == "Ground":
        return "0 V"
    return value


def render_circuit_board(components, wires):
    html_rows = []
    for chunk_start in range(0, len(components), 4):
        chunk = components[chunk_start : chunk_start + 4]
        cells = []
        for idx, comp in enumerate(chunk):
            style = COMPONENT_STYLES.get(comp.comp_type, {"color": "#cbd5e1", "icon": "?"})
            cells.append(
                f"""
                <div class="part">
                    <div class="chip" style="background:{style['color']}">{style['icon']}</div>
                    <strong>{comp.comp_type}</strong>
                    <span>{comp.id} | {component_value_label(comp)}</span>
                </div>
                """
            )
            if idx < len(chunk) - 1:
                cells.append('<div class="wire"></div>')
        html_rows.append(f"<div class='row'>{''.join(cells)}</div>")

    wire_list = "".join(
        f"<span class='note'>{wire.start_comp.id}:pin{wire.start_pin} -> {wire.end_comp.id}:pin{wire.end_pin}</span><br>"
        for wire in wires
    )
    st.markdown(
        f"""
        <div class="circuit-board">
            {''.join(html_rows)}
            <div style="margin-top: 8px; border-top: 1px solid rgba(148, 163, 184, .18); padding-top: 14px;">
                <strong style="color:#e5edf8;">Connections</strong><br>
                {wire_list}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(preset):
    st.sidebar.header("Circuit setup")
    st.sidebar.caption("Change component values and run the web simulation.")
    overrides = {}
    for comp_id, comp_type, default_value, _extras in preset["components"]:
        if comp_type == "Ground":
            continue
        label = f"{comp_type} ({comp_id})"
        if comp_type == "Switch":
            overrides[comp_id] = 1.0 if st.sidebar.toggle(label, value=default_value >= 0.5) else 0.0
        else:
            step = 0.001 if comp_type == "CurrentSource" else 0.1
            overrides[comp_id] = st.sidebar.number_input(label, value=float(default_value), step=step, format="%.6f")

    st.sidebar.divider()
    analysis_mode = st.sidebar.selectbox(
        "Analysis mode",
        ["dc", "transient"],
        index=1 if preset["analysis"] == "transient" else 0,
    )
    time_step = st.sidebar.number_input("Time step (s)", min_value=0.000001, value=0.005, step=0.001, format="%.6f")
    transient_steps = st.sidebar.number_input("Transient steps", min_value=1, max_value=200, value=8, step=1)
    st.sidebar.divider()
    st.sidebar.markdown("**Online deployment**")
    st.sidebar.caption("Push this repository to GitHub, then deploy `streamlit_app.py` on Streamlit Community Cloud.")
    return overrides, analysis_mode, time_step, int(transient_steps)


def render_validation(validation):
    status_class = "status-ok" if validation.get("success") else "status-bad"
    status_text = "PASS" if validation.get("success") else "NEEDS FIX"
    st.markdown(
        f"<div class='{status_class}'><strong>Validation: {status_text}</strong><br>{validation.get('message')}</div>",
        unsafe_allow_html=True,
    )
    if validation.get("errors"):
        st.error("\n".join(f"- {item}" for item in validation["errors"]))
    if validation.get("warnings"):
        st.warning("\n".join(f"- {item}" for item in validation["warnings"]))
    if validation.get("info"):
        with st.expander("Validation details"):
            st.write("\n".join(f"- {item}" for item in validation["info"]))


def render_results(result, analyzer):
    if not result.get("success"):
        st.error(result.get("message", "Simulation failed."))
        return

    power = result.get("power_balance", {})
    solver_info = result.get("solver_info", {})
    node_voltages = result.get("node_voltages", [])
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Mode", result.get("analysis_mode", "dc").upper())
    col2.metric("Nodes", len(node_voltages))
    col3.metric("Power used", f"{float(power.get('consumed', 0.0)):.6f} W")
    col4.metric("Matrix", f"{solver_info.get('matrix_size', 0)} x {solver_info.get('matrix_size', 0)}")

    rows = []
    for item in result.get("component_results", []):
        rows.append(
            {
                "ID": item.get("id"),
                "Type": item.get("type"),
                "V drop": item.get("v_drop"),
                "Current": item.get("current"),
                "Power": item.get("power"),
                "Mode": item.get("mode", ""),
                "Model": item.get("model", ""),
            }
        )

    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("Component results")
        st.dataframe(rows, use_container_width=True, hide_index=True)
    with right:
        st.subheader("Node voltages")
        st.dataframe(
            [{"Node": index, "Voltage": voltage} for index, voltage in enumerate(node_voltages)],
            use_container_width=True,
            hide_index=True,
        )

    with st.expander("Engineering report"):
        st.code(analyzer.get_result_formatting(), language="text")
    if result.get("transient_snapshots"):
        with st.expander("Transient snapshots"):
            st.dataframe(result["transient_snapshots"], use_container_width=True)


def main():
    apply_page_style()
    st.markdown(
        f"""
        <div class="hero">
            <div class="kicker">{APP_VERSION}</div>
            <h1>{APP_NAME}</h1>
            <p class="subtitle">
                Online presentation version for circuit validation, MNA/KCL solving,
                component results, node voltages, power balance, and transient snapshots.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    preset_name = st.selectbox("Circuit preset", list(PRESETS.keys()))
    preset = PRESETS[preset_name]
    overrides, analysis_mode, time_step, transient_steps = render_sidebar(preset)
    components, wires = build_circuit(preset, overrides)

    top_left, top_right = st.columns([1.25, 0.75])
    with top_left:
        st.subheader(preset_name)
        st.caption(preset["description"])
        render_circuit_board(components, wires)
    with top_right:
        st.subheader("Project status")
        st.write(
            "This web version reuses the Python simulation engine from the desktop app "
            "and gives a shareable online demo for the mini project."
        )
        st.info("Desktop UI: Tkinter\n\nWeb demo: Streamlit\n\nCore engine: NodeManager + CircuitSolver")
        st.write("Run the simulation from the button below.")

    run_clicked = st.button("Run validation and simulation", type="primary", use_container_width=True)
    if run_clicked or "last_result" not in st.session_state:
        validation, result, analyzer = run_solver(components, wires, analysis_mode, time_step, transient_steps)
        st.session_state["last_validation"] = validation
        st.session_state["last_result"] = result
    else:
        validation = st.session_state["last_validation"]
        result = st.session_state["last_result"]
        analyzer = SimulationAnalyzer()
        analyzer.last_results = result

    st.divider()
    validation_col, result_col = st.columns([0.8, 1.2])
    with validation_col:
        st.subheader("Validation")
        render_validation(validation)
    with result_col:
        st.subheader("Simulation")
        render_results(result, analyzer)

    st.divider()
    st.subheader("Presentation note")
    st.write(
        "This is the online demo branch of SMART CIRCUIT SIMULATOR PRO v6.3. "
        "The full desktop builder remains available in `main.py`, while this web interface "
        "shows the solver and project idea online for university review."
    )


if __name__ == "__main__":
    main()
