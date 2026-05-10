import streamlit as st

st.set_page_config(
    page_title="Smart Circuit Simulator Pro",
    layout="wide"
)

st.title("⚡ Smart Circuit Simulator Pro v6.3")

st.subheader("Online Demo Version")

st.write("""
This is the online version of my Smart Circuit Simulator Pro project.
The desktop version contains:
- Circuit Drawing
- Wire System
- Node Detection
- Matrix Solver
- Simulation Engine
""")

st.divider()

st.header("Circuit Solver Demo")

voltage = st.number_input("Voltage (V)", value=12.0)
resistance = st.number_input("Resistance (Ω)", value=1000.0)

if st.button("Solve Circuit"):
    if resistance == 0:
        st.error("Resistance cannot be zero")
    else:
        current = voltage / resistance
        power = voltage * current

        st.success("Simulation Completed")

        col1, col2, col3 = st.columns(3)

        col1.metric("Voltage", f"{voltage} V")
        col2.metric("Current", f"{current:.5f} A")
        col3.metric("Power", f"{power:.5f} W")

st.divider()

st.header("Future Roadmap")

st.markdown("""
- v7 → Better UI
- v8 → Advanced Components
- v10 → Cloud Save
- v12 → AI Circuit Analysis
- v14 → Professional Simulation Platform
""")
