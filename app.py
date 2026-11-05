import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="Three Phase Dashboard",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Three-Phase Interactive Dashboard")
st.write("Interactive analysis of Balanced Star and Delta Connected Loads")

# ---------------------------------
# SIDEBAR INPUTS
# ---------------------------------

st.sidebar.header("⚙️ System Parameters")

VL = st.sidebar.number_input(
    "Line Voltage VL (V)",
    min_value=1.0,
    value=415.0,
    step=5.0
)

frequency = st.sidebar.number_input(
    "Frequency (Hz)",
    min_value=1.0,
    value=50.0,
    step=1.0
)

connection = st.sidebar.radio(
    "Connection Type",
    ["Star", "Delta"]
)

load_condition = st.sidebar.radio(
    "Load Condition",
    ["Balanced", "Unbalanced"]
)

st.sidebar.header("🔧 Load Parameters")

if load_condition == "Balanced":

    R = st.sidebar.slider(
        "Resistance R (Ω)",
        1.0, 100.0, 20.0
    )

    L = st.sidebar.slider(
        "Inductance L (H)",
        0.0, 1.0, 0.1
    )

    RR = R
    RY = R
    RB = R

    LR = L
    LY = L
    LB = L

else:

    st.sidebar.subheader("R Phase")
    RR = st.sidebar.slider(
        "R Phase Resistance (Ω)",
        1.0, 100.0, 20.0
    )

    LR = st.sidebar.slider(
        "R Phase Inductance (H)",
        0.0, 1.0, 0.10
    )

    st.sidebar.subheader("Y Phase")
    RY = st.sidebar.slider(
        "Y Phase Resistance (Ω)",
        1.0, 100.0, 30.0
    )

    LY = st.sidebar.slider(
        "Y Phase Inductance (H)",
        0.0, 1.0, 0.15
    )

    st.sidebar.subheader("B Phase")
    RB = st.sidebar.slider(
        "B Phase Resistance (Ω)",
        1.0, 100.0, 40.0
    )

    LB = st.sidebar.slider(
        "B Phase Inductance (H)",
        0.0, 1.0, 0.20
    )


# ---------------------------------
# CALCULATIONS
# ---------------------------------

omega = 2 * np.pi * frequency

if load_condition == "Balanced":

    # Balanced load
    XL = omega * L
    Z = complex(R, XL)

    Z_mag = abs(Z)
    phi = np.angle(Z)

    if connection == "Star":
      Vph = VL / np.sqrt(3)

      V_R = Vph * np.exp(1j * np.deg2rad(0))
      V_Y = Vph * np.exp(1j * np.deg2rad(-120))
      V_B = Vph * np.exp(1j * np.deg2rad(120))

      I_R = V_R / Z
      I_Y = V_Y / Z
      I_B = V_B / Z

      Iph = abs(I_R)
      IL = Iph


    else:  # Delta

      Vph = VL

     # Delta branch voltages
      V_RY = VL * np.exp(1j * np.deg2rad(30))
      V_YB = VL * np.exp(1j * np.deg2rad(-90))
      V_BR = VL * np.exp(1j * np.deg2rad(150))

     # Delta branch currents
      I_RY = V_RY / Z
      I_YB = V_YB / Z
      I_BR = V_BR / Z

     # Delta line currents
      I_R = I_RY - I_BR
      I_Y = I_YB - I_RY
      I_B = I_BR - I_YB

     # Current magnitudes
      Iph = abs(I_RY)
      IL = abs(I_R)

    power_factor = np.cos(phi)
    P = np.sqrt(3) * VL * IL * power_factor
    Q = np.sqrt(3) * VL * IL * np.sin(phi)
    S = np.sqrt(3) * VL * IL


else:   # Unbalanced load
    # Individual phase impedances
    ZR = complex(RR, omega * LR)
    ZY = complex(RY, omega * LY)
    ZB = complex(RB, omega * LB)

    if connection == "Star":

        Vph = VL / np.sqrt(3)

        # Three-phase supply voltages
        VR = Vph * np.exp(1j * np.deg2rad(0))
        VY = Vph * np.exp(1j * np.deg2rad(-120))
        VB = Vph * np.exp(1j * np.deg2rad(120))

        # Phase currents
        IR = VR / ZR
        IY = VY / ZY
        IB = VB / ZB

        # Neutral current for 4-wire Star
        IN = -(IR + IY + IB)

# ==========================================
# UNBALANCED STAR POWER CALCULATIONS
# ==========================================

        SR = VR * np.conj(IR)
        SY = VY * np.conj(IY)
        SB = VB * np.conj(IB)

# Individual phase powers
        PR = SR.real
        PY = SY.real
        PB = SB.real

        QR = SR.imag
        QY = SY.imag
        QB = SB.imag

# Total complex power
        S_total_unbal = SR + SY + SB

        P_total_unbal = S_total_unbal.real
        Q_total_unbal = S_total_unbal.imag
        S_mag_unbal = abs(S_total_unbal)

# Overall power factor
        if S_mag_unbal > 1e-12:
           PF_unbal = abs(P_total_unbal) / S_mag_unbal
        else:
           PF_unbal = 0.0

    else:  # Unbalanced Delta

        # Line-line voltages
        VRY = VL * np.exp(1j * np.deg2rad(0))
        VYB = VL * np.exp(1j * np.deg2rad(-120))
        VBR = VL * np.exp(1j * np.deg2rad(120))

        # Delta branch currents
        IRY = VRY / ZR
        IYB = VYB / ZY
        IBR = VBR / ZB

        # Line currents
        IR = IRY - IBR
        IY = IYB - IRY
        IB = IBR - IYB

        # ==========================================
        # UNBALANCED DELTA POWER CALCULATION
        # ==========================================

        S_RY = VRY * np.conj(IRY)
        S_YB = VYB * np.conj(IYB)
        S_BR = VBR * np.conj(IBR)

        # Total complex three-phase power
        S_total_unbal_delta = S_RY + S_YB + S_BR

        # Active and reactive power
        P_total_unbal_delta = S_total_unbal_delta.real
        Q_total_unbal_delta = S_total_unbal_delta.imag

        # Apparent power
        S_mag_unbal_delta = abs(S_total_unbal_delta)

        # Overall power factor
        if S_mag_unbal_delta > 1e-12:
            PF_total_unbal_delta = abs(P_total_unbal_delta) / S_mag_unbal_delta
        else:
            PF_total_unbal_delta = 0.0


# -----------------------------------
# DISPLAY RESULTS
# -----------------------------------

st.subheader(f"📊 {load_condition} {connection} Connection")


# ===== BALANCED LOAD =====

if load_condition == "Balanced":

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Phase Voltage",
        f"{Vph:.2f} V"
    )

    col2.metric(
        "Phase Current",
        f"{Iph:.2f} A"
    )

    col3.metric(
        "Line Current",
        f"{IL:.2f} A"
    )

    col4.metric(
        "Power Factor",
        f"{power_factor:.3f}"
    )

    st.divider()

    col5, col6, col7 = st.columns(3)

    col5.metric(
        "Active Power",
        f"{P:.2f} W"
    )

    col6.metric(
        "Reactive Power",
        f"{Q:.2f} VAR"
    )

    col7.metric(
        "Apparent Power",
        f"{S:.2f} VA"
    )


# ===== UNBALANCED LOAD =====

else:

    st.write("### Phase / Line Current Results")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "R Phase Current",
        f"{abs(IR):.2f} A"
    )

    col2.metric(
        "Y Phase Current",
        f"{abs(IY):.2f} A"
    )

    col3.metric(
        "B Phase Current",
        f"{abs(IB):.2f} A"
    )

    st.divider()

    st.write("### Load Impedances")

    col4, col5, col6 = st.columns(3)

    col4.metric(
        "|ZR|",
        f"{abs(ZR):.2f} Ω"
    )

    col5.metric(
        "|ZY|",
        f"{abs(ZY):.2f} Ω"
    )

    col6.metric(
        "|ZB|",
        f"{abs(ZB):.2f} Ω"
    )
  # -----------------------------
# NEUTRAL CURRENT DISPLAY
# -----------------------------

if connection == "Star":

    st.subheader("Neutral Current")

    if load_condition == "Balanced":
        st.metric("Neutral Current IN", "0.00 A")
        st.success("✅ Balanced Star load: Neutral current is approximately zero.")

    else:
        st.metric(
            "Neutral Current IN",
            f"{abs(IN):.2f} A"
        )

        st.write(
            f"Neutral Current Angle = "
            f"{np.degrees(np.angle(IN)):.2f}°"
        )

        if abs(IN) < 0.01:
            st.success(
                "✅ The load is approximately balanced. Neutral current ≈ 0 A."
            )
        else:
            st.warning(
                f"⚠️ Unbalanced Star load: Neutral current = "
                f"{abs(IN):.2f} A"
            )

elif connection == "Delta":

    st.info(
        "ℹ️ Delta connection has no neutral conductor, "
        "so neutral current is not applicable."
    )

# ==========================================
# UNBALANCED THREE-PHASE POWER DISPLAY
# ==========================================

if load_condition == "Unbalanced":

    st.divider()
    st.subheader("⚡ Three-Phase Power Analysis")

    if connection == "Star":

        P_display = P_total_unbal
        Q_display = Q_total_unbal
        S_display = abs(S_total_unbal)

        if S_display > 1e-12:
            PF_display = abs(P_display) / S_display
        else:
            PF_display = 0.0

    elif connection == "Delta":

        P_display = P_total_unbal_delta
        Q_display = Q_total_unbal_delta
        S_display = S_mag_unbal_delta
        PF_display = PF_total_unbal_delta

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Active Power",
        f"{P_display:.2f} W"
    )

    col2.metric(
        "Reactive Power",
        f"{Q_display:.2f} VAR"
    )

    col3.metric(
        "Apparent Power",
        f"{S_display:.2f} VA"
    )

    col4.metric(
        "Power Factor",
        f"{PF_display:.3f}"
    )

# ==========================================================
# LINE AND PHASE QUANTITIES
# ==========================================================

st.divider()
st.subheader("⚡ Line and Phase Quantities")

# ----------------------------------------------------------
# BALANCED STAR
# ----------------------------------------------------------

if connection == "Star" and load_condition == "Balanced":

    st.write("### Balanced Star")

    v1, v2 = st.columns(2)

    v1.metric(
        "Line Voltage VL",
        f"{VL:.2f} V"
    )

    v2.metric(
        "Phase Voltage Vph",
        f"{Vph:.2f} V"
    )

    i1, i2 = st.columns(2)

    i1.metric(
        "Line Current IL",
        f"{IL:.2f} A"
    )

    i2.metric(
        "Phase Current Iph",
        f"{Iph:.2f} A"
    )


# ----------------------------------------------------------
# UNBALANCED STAR
# ----------------------------------------------------------

elif connection == "Star" and load_condition == "Unbalanced":

    st.write("### Unbalanced Star")

    # Line voltage
    st.metric(
        "Line Voltage VL",
        f"{VL:.2f} V"
    )

    # Phase voltages
    st.write("#### Phase Voltages")

    v1, v2, v3 = st.columns(3)

    v1.metric(
        "VR",
        f"{abs(VR):.2f} V"
    )

    v2.metric(
        "VY",
        f"{abs(VY):.2f} V"
    )

    v3.metric(
        "VB",
        f"{abs(VB):.2f} V"
    )

    # Star: line current = phase current
    st.write("#### Line / Phase Currents")

    i1, i2, i3 = st.columns(3)

    i1.metric(
        "IR",
        f"{abs(IR):.2f} A"
    )

    i2.metric(
        "IY",
        f"{abs(IY):.2f} A"
    )

    i3.metric(
        "IB",
        f"{abs(IB):.2f} A"
    )

    st.caption(
        "For a Star connection, line current equals phase current."
    )


# ----------------------------------------------------------
# BALANCED DELTA
# ----------------------------------------------------------

elif connection == "Delta" and load_condition == "Balanced":

    st.write("### Balanced Delta")

    v1, v2 = st.columns(2)

    v1.metric(
        "Line Voltage VL",
        f"{VL:.2f} V"
    )

    v2.metric(
        "Phase / Branch Voltage Vph",
        f"{Vph:.2f} V"
    )

    i1, i2 = st.columns(2)

    i1.metric(
        "Line Current IL",
        f"{IL:.2f} A"
    )

    i2.metric(
        "Phase / Branch Current Iph",
        f"{Iph:.2f} A"
    )

    st.caption(
        "For balanced Delta: Vph = VL and IL = √3 × Iph."
    )


# ----------------------------------------------------------
# UNBALANCED DELTA
# ----------------------------------------------------------

elif connection == "Delta" and load_condition == "Unbalanced":

    st.write("### Unbalanced Delta")

    # Delta branch voltages
    st.write("#### Line / Branch Voltages")

    v1, v2, v3 = st.columns(3)

    v1.metric(
        "VRY",
        f"{abs(VRY):.2f} V"
    )

    v2.metric(
        "VYB",
        f"{abs(VYB):.2f} V"
    )

    v3.metric(
        "VBR",
        f"{abs(VBR):.2f} V"
    )

    # Delta branch currents
    st.write("#### Phase / Branch Currents")

    b1, b2, b3 = st.columns(3)

    b1.metric(
        "IRY",
        f"{abs(IRY):.2f} A"
    )

    b2.metric(
        "IYB",
        f"{abs(IYB):.2f} A"
    )

    b3.metric(
        "IBR",
        f"{abs(IBR):.2f} A"
    )

    # Delta line currents
    st.write("#### Line Currents")

    i1, i2, i3 = st.columns(3)

    i1.metric(
        "IR",
        f"{abs(IR):.2f} A"
    )

    i2.metric(
        "IY",
        f"{abs(IY):.2f} A"
    )

    i3.metric(
        "IB",
        f"{abs(IB):.2f} A"
    )

    st.caption(
        "For an unbalanced Delta load, line currents are obtained "
        "from phasor differences of the branch currents."
    )
# -----------------------------------
# INTERACTIVE VOLTAGE AND CURRENT PHASOR DIAGRAM
# -----------------------------------

st.divider()

st.subheader("🔄 Interactive voltage and Current Phasor Diagram")

st.caption(
    "Dashed vectors = phase voltages; dotted vectors = line voltages; "
    "thick solid vectors = line currents; thin solid vectors = "
    "phase/branch currents. Voltage vectors are scaled for visual "
    "comparison only. Labels show actual magnitudes and angles."
)


# ==========================================
# 1. SELECT CURRENT PHASORS
# ==========================================

if load_condition == "Balanced":
    plot_IR = I_R
    plot_IY = I_Y
    plot_IB = I_B
else:
    plot_IR = IR
    plot_IY = IY
    plot_IB = IB

# ==========================================
# VOLTAGE PHASORS
# ==========================================

# Source phase-to-neutral voltages
V_phase_mag = VL / np.sqrt(3)

VRN_plot = V_phase_mag * np.exp(
    1j * np.deg2rad(0)
)

VYN_plot = V_phase_mag * np.exp(
    1j * np.deg2rad(-120)
)

VBN_plot = V_phase_mag * np.exp(
    1j * np.deg2rad(120)
)

# Line-to-line voltages
VRY_plot = VRN_plot - VYN_plot
VYB_plot = VYN_plot - VBN_plot
VBR_plot = VBN_plot - VRN_plot


if connection == "Star":

    # Star phase voltages
    phase_voltage_phasors = {
        "VRN": VRN_plot,
        "VYN": VYN_plot,
        "VBN": VBN_plot
    }

    # Star line voltages
    line_voltage_phasors = {
        "VRY": VRY_plot,
        "VYB": VYB_plot,
        "VBR": VBR_plot
    }


else:  # Delta

    # In Delta:
    # Phase voltage = line voltage
    # Therefore don't plot the same voltage twice

    phase_voltage_phasors = {}

    line_voltage_phasors = {
        "VRY": VRY_plot,
        "VYB": VYB_plot,
        "VBR": VBR_plot
    }

fig = go.Figure()
# ==========================================
# SCALE VOLTAGE PHASORS FOR DISPLAY
# ==========================================

max_current = max(
    abs(plot_IR),
    abs(plot_IY),
    abs(plot_IB)
)

all_voltage_values = (
    list(phase_voltage_phasors.values())
    +
    list(line_voltage_phasors.values())
)

max_voltage = max(
    abs(v) for v in all_voltage_values
)

if max_voltage > 0:
    voltage_scale = max_current / max_voltage
else:
    voltage_scale = 1.0

# ==========================================
# CURRENT PHASORS
# ==========================================

if connection == "Star":

    # Star: line current = phase current
    current_phasors = {
        "IR = IphR": plot_IR,
        "IY = IphY": plot_IY,
        "IB = IphB": plot_IB
    }

else:

    # Delta line currents
    current_phasors = {
        "IR line": plot_IR,
        "IY line": plot_IY,
        "IB line": plot_IB
    }

current_colors = {
    "IR = IphR": "red",
    "IY = IphY": "gold",
    "IB = IphB": "blue",

    "IR line": "red",
    "IY line": "gold",
    "IB line": "blue"
}


# ==========================================
# DRAW VOLTAGE PHASORS
# ==========================================

voltage_colors = {
    "VR": "red",
    "VY": "gold",
    "VB": "blue",
    "VRY": "red",
    "VYB": "gold",
    "VBR": "blue"
}

# ==========================================
# DRAW PHASE VOLTAGES
# ==========================================

phase_voltage_colors = {
    "VRN": "red",
    "VYN": "gold",
    "VBN": "blue"
}

for name, voltage in phase_voltage_phasors.items():

    magnitude = abs(voltage)
    angle = np.degrees(np.angle(voltage))

    voltage_display = voltage * voltage_scale

    fig.add_trace(
        go.Scatter(
            x=[0, voltage_display.real],
            y=[0, voltage_display.imag],
            mode="lines+text",
            name=name,

            line=dict(
                color=phase_voltage_colors[name],
                width=3,
                dash="dash"
            ),

            text=[
                "",
                f"{name} = {magnitude:.1f} V ∠ {angle:.1f}°"
            ],

            textposition="bottom center"
        )
    )

    fig.add_annotation(
        x=voltage_display.real,
        y=voltage_display.imag,

        ax=voltage_display.real * 0.88,
        ay=voltage_display.imag * 0.88,

        xref="x",
        yref="y",
        axref="x",
        ayref="y",

        showarrow=True,
        arrowhead=3,
        arrowsize=1.2,
        arrowwidth=2,

        arrowcolor=phase_voltage_colors[name],

        text=""
    )
    # ==========================================
# DRAW LINE VOLTAGES
# ==========================================

line_voltage_colors = {
    "VRY": "crimson",
    "VYB": "orange",
    "VBR": "royalblue"
}

for name, voltage in line_voltage_phasors.items():

    magnitude = abs(voltage)
    angle = np.degrees(np.angle(voltage))

    voltage_display = voltage * voltage_scale

    fig.add_trace(
        go.Scatter(
            x=[0, voltage_display.real],
            y=[0, voltage_display.imag],
            mode="lines+text",
            name=name,

            line=dict(
                color=line_voltage_colors[name],
                width=3,
                dash="dot"
            ),

            text=[
                "",
                f"{name} = {magnitude:.1f} V ∠ {angle:.1f}°"
            ],

            textposition="top center"
        )
    )

    fig.add_annotation(
        x=voltage_display.real,
        y=voltage_display.imag,

        ax=voltage_display.real * 0.88,
        ay=voltage_display.imag * 0.88,

        xref="x",
        yref="y",
        axref="x",
        ayref="y",

        showarrow=True,
        arrowhead=3,
        arrowsize=1.2,
        arrowwidth=2,

        arrowcolor=line_voltage_colors[name],

        text=""
    )

for name, current in current_phasors.items():

    # Calculate magnitude and phase angle
    magnitude = abs(current)
    angle = np.degrees(np.angle(current))

    # End point of phasor
    x = current.real
    y = current.imag

    # Create label
    label = f"{name} = {magnitude:.2f} A ∠ {angle:.1f}°"

    # Draw phasor
    fig.add_trace(
        go.Scatter(
            x=[0, x],
            y=[0, y],
            mode="lines+text",
            name=name,
            line=dict(
                color=current_colors[name],
                width=4
            )
        )
    )
     # Arrowhead
    fig.add_annotation(
        x=current.real,
        y=current.imag,
        ax=0,
        ay=0,
        xref="x",
        yref="y",
        axref="x",
        ayref="y",
        showarrow=True,
        arrowhead=3,
        arrowsize=1.5,
        arrowwidth=3,
        arrowcolor=current_colors[name],
        text=""
    )

    # Magnitude and angle label
    fig.add_annotation(
        x=current.real,
        y=current.imag,
        text=f"{name} = {magnitude:.2f} A ∠ {angle:.1f}°",
        showarrow=False,
        yshift=15
    )
    marker=dict(
    size=[6, 10],
    color=current_colors[name]
            ),
    text=["", label],
    textposition="top center",
    hovertemplate=(
    f"<b>{name}</b><br>"
    f"Magnitude: {magnitude:.2f} A<br>"
    f"Angle: {angle:.1f}°"
     "<extra></extra>"
            )

 # ==========================================
# DELTA PHASE / BRANCH CURRENT PHASORS
# ==========================================

if connection == "Delta":

    # Balanced Delta
    if load_condition == "Balanced":

        delta_branch_currents = {
            "IRY branch": I_RY,
            "IYB branch": I_YB,
            "IBR branch": I_BR
        }

    # Unbalanced Delta
    else:

        delta_branch_currents = {
            "IRY branch": IRY,
            "IYB branch": IYB,
            "IBR branch": IBR
        }

    branch_colors = {
        "IRY branch": "lightcoral",
        "IYB branch": "khaki",
        "IBR branch": "cornflowerblue"
    }

    for name, current in delta_branch_currents.items():

        magnitude = abs(current)
        angle = np.degrees(np.angle(current))

        fig.add_trace(
            go.Scatter(
                x=[0, current.real],
                y=[0, current.imag],

                mode="lines+text",

                name=name,

                line=dict(
                    color=branch_colors[name],
                    width=2
                ),

                text=[
                    "",
                    f"{name} = {magnitude:.2f} A ∠ {angle:.1f}°"
                ],

                textposition="bottom center",

                hovertemplate=(
                    f"<b>{name}</b><br>"
                    f"Magnitude: {magnitude:.2f} A<br>"
                    f"Angle: {angle:.1f}°"
                    "<extra></extra>"
                )
            )
        )

        # Arrowhead
        fig.add_annotation(
            x=current.real,
            y=current.imag,

            ax=current.real * 0.88,
            ay=current.imag * 0.88,

            xref="x",
            yref="y",
            axref="x",
            ayref="y",

            showarrow=True,
            arrowhead=3,
            arrowsize=1.1,
            arrowwidth=2,

            arrowcolor=branch_colors[name],

            text=""
        )

fig.update_layout(

    title=dict(
        text="Three-Phase Line and Phase Voltage / Current Phasors",
        x=0.5,
        xanchor="center"
    ),

    xaxis_title="Real Axis (Scaled)",
    yaxis_title="Imaginary Axis (Scaled)",

    height=750,

    showlegend=True,

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ),

    margin=dict(
        l=50,
        r=50,
        t=110,
        b=50
    )
)
fig.update_xaxes(
    zeroline=True,
    zerolinewidth=2,
    zerolinecolor="gray"
)

fig.update_yaxes(
    zeroline=True,
    zerolinewidth=2,
    zerolinecolor="gray",
    scaleanchor="x",
    scaleratio=1
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key=f"current_phasor_{connection}_{load_condition}"
)
# ==========================================
# TWO-WATTMETER METHOD
# ==========================================

st.divider()
st.subheader("⚡ Two-Wattmeter Method")
if load_condition == "Balanced":
       # Load angle
    phi_w = np.arctan2(XL, R)

    # Power factor
    PF_w = abs(np.cos(phi_w))
    # Wattmeter readings
    W1 = VL * IL * np.cos(np.deg2rad(30) - phi_w)

    W2 = VL * IL * np.cos(np.deg2rad(30) + phi_w)
        # Total active power
    P_2W = W1 + W2

    # Reactive power for balanced load
    Q_2W = np.sqrt(3) * (W1 - W2)

    # Load angle in degrees
    phi_deg_w = np.degrees(phi_w)
    st.write("### Wattmeter Readings")

    wcol1, wcol2 = st.columns(2)

    wcol1.metric(
        "Wattmeter W1",
        f"{W1:.2f} W"
    )

    wcol2.metric(
        "Wattmeter W2",
        f"{W2:.2f} W"
    )
    st.write("### Power from Two Wattmeters")

    pcol1, pcol2, pcol3 = st.columns(3)

    pcol1.metric(
        "Total Active Power",
        f"{P_2W:.2f} W"
    )

    pcol2.metric(
        "Reactive Power",
        f"{Q_2W:.2f} VAR"
    )

    pcol3.metric(
        "Power Factor",
        f"{PF_w:.3f}"
    )
    st.write(
    f"**Load Angle φ = {phi_deg_w:.2f}°**"
    )
    # Teaching interpretation

    if PF_w >= 0.999:

        st.success(
            "✅ Unity Power Factor: W1 = W2. "
            "Each wattmeter reads half of the total active power."
        )

    elif abs(PF_w - 0.5) < 0.01:

        st.warning(
            "⚠️ Power Factor ≈ 0.5: "
            "One wattmeter reading approaches zero."
        )

    elif PF_w < 0.5:

        st.error(
            "🔴 Power Factor < 0.5: "
            "One wattmeter reading becomes negative."
        )

    else:

        st.info(
            "Both wattmeters have positive but unequal readings."
        )
else:

    # ==========================================
    # UNBALANCED DELTA TWO-WATTMETER METHOD
    # ==========================================

    if connection == "Delta":

        st.write("### Unbalanced Delta Measurements")
        # Line-to-neutral source voltage phasors
        Vph_source = VL / np.sqrt(3)

        V_R = Vph_source * np.exp(1j * np.deg2rad(0))
        V_Y = Vph_source * np.exp(1j * np.deg2rad(-120))
        V_B = Vph_source * np.exp(1j * np.deg2rad(120))

        # Line-to-line voltage phasors
        V_RY = V_R - V_Y
        V_YB = V_Y - V_B
        V_BR = V_B - V_R

        # Delta branch currents
        IRY = V_RY / ZR
        IYB = V_YB / ZY
        IBR = V_BR / ZB

        # ==========================================
        # DELTA LINE CURRENTS
        # ==========================================

        IR = IRY - IBR
        IY = IYB - IRY
        IB = IBR - IYB

        # Wattmeter 1:
        # Current coil in R line
        # Voltage coil connected between R and Y
        W1_unbal = np.real(V_RY * np.conj(IR))

        # Wattmeter 2:
        # Current coil in B line
        # Voltage coil connected between B and Y
        V_BY = -V_YB

        W2_unbal = np.real(V_BY * np.conj(IB))

        # Total active power measured by two wattmeters
        P_2W_unbal = W1_unbal + W2_unbal

        # Display wattmeter readings
        w1_col, w2_col, total_col = st.columns(3)

        w1_col.metric(
            "Wattmeter W1",
            f"{W1_unbal:.2f} W"
        )

        w2_col.metric(
            "Wattmeter W2",
            f"{W2_unbal:.2f} W"
        )

        total_col.metric(
            "W1 + W2",
            f"{P_2W_unbal:.2f} W"
        )

        # Compare with independently calculated active power
        power_error = abs(
            P_2W_unbal - P_total_unbal_delta
        )

        if power_error < 0.1:

            st.success(
                "✅ Two-wattmeter verification successful: "
                "W1 + W2 equals the total three-phase active power."
            )

        else:

            st.warning(
                f"⚠️ Difference between W1 + W2 and calculated "
                f"active power: {power_error:.2f} W"
            )

        # Negative wattmeter indication
        if W1_unbal < 0 or W2_unbal < 0:

            st.warning(
                "⚠️ One wattmeter has a negative reading. "
                "In practice, the pressure-coil or current-coil "
                "terminals would be reversed to obtain an upscale "
                "reading, and the reading would be treated as negative."
            )

    # ==========================================
    # UNBALANCED STAR WITH NEUTRAL
    # ==========================================

    else:

        st.info(
            "ℹ️ The present Unbalanced Star model includes a neutral "
            "conductor and a non-zero neutral current. The standard "
            "two-wattmeter method applies to three-wire systems, so it "
            "is not displayed for this four-wire Star configuration."
        )

    