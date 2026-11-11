import json
import re

import numpy as np
import plotly.graph_objects as go
from pathlib import Path

import streamlit as st
from streamlit_book import multiple_choice

from app_utils import load_md, render_toggle_container


# Authors, institutions, and year
year = 2026
authors = {
    "Beatrice Richieri": [1],
    "Thomas Reimann": [2],
}
institutions = {
    1: "FAU Erlangen",
    2: "TU Dresden",
}
index_symbols = ["¹", "²", "³", "⁴", "⁵", "⁶", "⁷", "⁸", "⁹"]

author_list = [
    f"{name}{''.join(index_symbols[i - 1] for i in indices)}"
    for name, indices in authors.items()
]
institution_list = [
    f"{index_symbols[i - 1]} {institution}"
    for i, institution in institutions.items()
]
institution_text = " | ".join(institution_list)


# -----------------------------------------------------------------------------
# Fixed language and file locations
# -----------------------------------------------------------------------------
LANGUAGE = "en"

BASE_DIR = st.session_state.BASE_DIR
CONTENT_DIR = st.session_state.CONTENT_DIR
ASSETS_DIR = st.session_state.ASSETS_DIR
IMAGE_DIR = st.session_state.IMAGE_DIR
MD_DIR = st.session_state.MD_DIR
QUESTIONS_DIR = st.session_state.QUESTIONS_DIR

st.session_state.language = LANGUAGE


# -----------------------------------------------------------------------------
# Parameter color coding
# -----------------------------------------------------------------------------
# The colors follow the conceptual LuKARS scheme:
# Qis -> blue, Qhyd -> red, Qsec -> green,
# QMC -> violet, QMS/QCS/Qspring -> orange.
PARAMETER_COLORS = {
    # Slow infiltration
    r"Q_{\mathrm{is}}": "blue",
    r"Q_{\mathrm{is},i}": "blue",
    r"Q_{\mathrm{is},i,t}": "blue",
    r"k_{\mathrm{is}}": "blue",
    r"k_{\mathrm{is},i}": "blue",

    # Fast hydrotope flow
    r"Q_{\mathrm{hyd}}": "red",
    r"Q_{\mathrm{hyd},i}": "red",
    r"Q_{\mathrm{hyd},i,t}": "red",
    r"E_{\min}": "red",
    r"E_{\min,i}": "red",
    r"E_{\max}": "red",
    r"E_{\max,i}": "red",
    r"\alpha": "red",
    r"\alpha_i": "red",
    r"k_{\mathrm{hyd}}": "red",
    r"k_{\mathrm{hyd},i}": "red",
    r"l_{\mathrm{hyd}}": "red",
    r"l_{\mathrm{hyd},i}": "red",

    # Secondary spring discharge
    r"Q_{\mathrm{sec}}": "green",
    r"Q_{\mathrm{sec},i}": "green",
    r"Q_{\mathrm{sec},i,t}": "green",
    r"E_{\mathrm{sec}}": "green",
    r"E_{\mathrm{sec},i}": "green",
    r"k_{\mathrm{sec}}": "green",
    r"k_{\mathrm{sec},i}": "green",

    # Matrix-conduit exchange
    r"Q_{\mathrm{MC}}": "violet",
    r"Q_{\mathrm{MC},t}": "violet",
    r"k_{\mathrm{MC}}": "violet",
    r"a_{\mathrm{MC}}": "violet",

    # Spring discharge components
    r"Q_{\mathrm{MS}}": "orange",
    r"Q_{\mathrm{MS},t}": "orange",
    r"Q_{\mathrm{CS}}": "orange",
    r"Q_{\mathrm{CS},t}": "orange",
    r"Q_{\mathrm{spring}}": "orange",
    r"k_{\mathrm{MS}}": "orange",
    r"a_{\mathrm{MS}}": "orange",
    r"k_{\mathrm{CS}}": "orange",
    r"a_{\mathrm{CS}}": "orange",
}


def color_parameter_markdown(markdown_text: str) -> str:
    """Color LuKARS fluxes/parameters while preserving the surrounding text."""

    # Update the legend text used in the existing Markdown material.
    markdown_text = markdown_text.replace(
        "🔵 **Calibration parameter** — parameters marked with a blue circle "
        "in the tables are parameters whose values are adjusted during model calibration.",
        "★ **Calibration parameter** — parameters marked with a black star "
        "in the tables are parameters whose values are adjusted during model calibration.",
    )

    # Capture the old blue-circle marker when present so it can be removed and
    # replaced consistently by a black star.
    pattern = re.compile(
        r"(?P<calibration>🔵\s*)?"
        r"(?:\$(?P<dollar>[^$]+)\$|\\\((?P<paren>.*?)\\\))"
    )

    def replace_math(match: re.Match) -> str:
        expression = (
            match.group("dollar")
            if match.group("dollar") is not None
            else match.group("paren")
        )

        color = PARAMETER_COLORS.get(expression)
        is_calibration = match.group("calibration") is not None

        if color is not None:
            parameter_text = f":{color}[${expression}$]"
        elif expression == r"C_{\mathrm{loss}}":
            # C_loss remains black: no blue dot and no pathway color.
            parameter_text = f"${expression}$"
        else:
            return match.group(0)

        if is_calibration:
            return f"{parameter_text} ★"

        return parameter_text

    colored_text = pattern.sub(replace_math, markdown_text)

    # l_hyd and C_loss are calibration parameters, but their stars should appear
    # only in Markdown tables, exactly like the other calibration markers.
    table_only_parameters = (
        r":red[$l_{\mathrm{hyd}}$]",
        r":red[$l_{\mathrm{hyd},i}$]",
        r"$C_{\mathrm{loss}}$",
    )

    colored_lines = []

    for line in colored_text.splitlines():
        if line.lstrip().startswith("|"):
            for parameter in table_only_parameters:
                if parameter in line and f"{parameter} ★" not in line:
                    line = line.replace(
                        parameter,
                        f"{parameter} ★",
                        1,
                    )

        colored_lines.append(line)

    return "\n".join(colored_lines)


def load_colored_md(filename: str) -> str:
    """Load one existing Markdown file and apply LuKARS parameter colors."""
    return color_parameter_markdown(
        load_md(
            MD_DIR,
            filename,
            LANGUAGE,
        )
    )

# -----------------------------------------------------------------------------
# Assessment renderer
# -----------------------------------------------------------------------------
def render_assessment(filename: Path) -> None:
    """Render an iNUX JSON assessment in two-column rows."""
    with filename.open("r", encoding="utf-8") as file:
        questions = json.load(file)

    for start_index in range(0, len(questions), 2):
        columns = st.columns(2)

        for column, question_data in zip(
            columns,
            questions[start_index : start_index + 2],
        ):
            with column:
                multiple_choice(
                    question=question_data["question"],
                    options_dict=question_data["options"],
                    success=question_data.get("success", "✅ Correct."),
                    error=question_data.get("error", "❌ Not quite."),
                )

@st.fragment
def render_assessment_fragment(
    filename: Path,
    container_key: str,
    label: str,
    default_open: bool = False,
) -> None:
    """Render an assessment independently from the rest of the page."""
    render_toggle_container(
        container_key,
        label,
        lambda: render_assessment(filename),
        default_open=default_open,
    )
# -----------------------------------------------------------------------------
# Interactive equation explorers
# -----------------------------------------------------------------------------
REFERENCE_AREA_M2 = 1.0e6  # 1 km²


def _response_figure(
    x,
    series,
    x_title: str,
    y_title: str,
    *,
    vertical_lines=None,
    horizontal_zero: bool = False,
    x_range=None,
    y_range=None,
    height: int = 350,
):
    """Create a compact Plotly response-curve figure."""
    figure = go.Figure()

    for label, values, dash in series:
        figure.add_trace(
            go.Scatter(
                x=x,
                y=values,
                mode="lines",
                name=label,
                line={"dash": dash},
            )
        )

    if vertical_lines:
        for value, label in vertical_lines:
            figure.add_vline(
                x=value,
                line_dash="dot",
                annotation_text=label,
                annotation_position="top",
            )

    if horizontal_zero:
        figure.add_hline(y=0.0, line_dash="dot")

    figure.update_layout(
        height=height,
        margin={"l": 20, "r": 20, "t": 25, "b": 20},
        xaxis_title=x_title,
        yaxis_title=y_title,
        hovermode="x unified",
        legend={"orientation": "h", "y": 1.12},
    )

    # Keep axes constant while sliders change so that changes in curve shape
    # and magnitude can be compared visually without Plotly autoscaling.
    figure.update_xaxes(range=x_range, fixedrange=True)
    figure.update_yaxes(range=y_range, fixedrange=True)

    return figure


def _show_response_figure(figure, key: str) -> None:
    st.plotly_chart(
        figure,
        use_container_width=True,
        key=key,
        config={"displaylogo": False, "scrollZoom": False},
    )


@st.fragment
def render_water_balance_explorer() -> None:
    st.markdown("##### Explore one time-step water balance")
    controls, graph = st.columns([1, 2], gap="large")

    with controls:
        current_storage = st.slider(
            "Current storage Eₜ (mm)",
            0.0,
            250.0,
            100.0,
            5.0,
            key="eq_balance_storage",
        )
        source = st.slider(
            "Source term S (mm/Δt)",
            0.0,
            20.0,
            5.0,
            0.5,
            key="eq_balance_source",
        )
        qis = st.slider(
            ":blue[Qis] / A (mm/Δt)",
            0.0,
            15.0,
            1.0,
            0.5,
            key="eq_balance_qis",
        )
        qhyd = st.slider(
            ":red[Qhyd] / A (mm/Δt)",
            0.0,
            15.0,
            2.0,
            0.5,
            key="eq_balance_qhyd",
        )
        qsec = st.slider(
            ":green[Qsec] / A (mm/Δt)",
            0.0,
            15.0,
            0.0,
            0.5,
            key="eq_balance_qsec",
        )

    raw_balance = current_storage + source - qis - qhyd - qsec
    next_storage = max(0.0, raw_balance)

    with graph:
        figure = go.Figure(
            go.Waterfall(
                orientation="v",
                measure=[
                    "absolute",
                    "relative",
                    "relative",
                    "relative",
                    "relative",
                    "total",
                    "absolute",
                ],
                x=[
                    "Eₜ",
                    "+ SΔt",
                    "− Qis/A Δt",
                    "− Qhyd/A Δt",
                    "− Qsec/A Δt",
                    "Raw balance",
                    "Eₜ₊₁",
                ],
                y=[
                    current_storage,
                    source,
                    -qis,
                    -qhyd,
                    -qsec,
                    0.0,
                    next_storage,
                ],
                connector={"line": {"dash": "dot"}},
                textposition="outside",
                text=[
                    f"{current_storage:.1f}",
                    f"+{source:.1f}",
                    f"−{qis:.1f}",
                    f"−{qhyd:.1f}",
                    f"−{qsec:.1f}",
                    f"{raw_balance:.1f}",
                    f"{next_storage:.1f}",
                ],
                hovertemplate="%{x}<br>%{y:.1f} mm<extra></extra>",
            )
        )
        figure.add_hline(y=0.0, line_dash="dot")
        figure.update_layout(
            height=370,
            margin={"l": 20, "r": 20, "t": 25, "b": 20},
            yaxis_title="Hydrotope storage / storage change (mm)",
            showlegend=False,
        )
        figure.update_xaxes(fixedrange=True)
        figure.update_yaxes(range=[-50.0, 280.0], fixedrange=True)
        _show_response_figure(figure, "eq_balance_plot")

    st.caption(
        "The plot follows one simulation time step from left to right: start with "
        "the current hydrotope storage Eₜ, add the net source term SΔt, subtract "
        "slow infiltration, fast flow and secondary discharge, and obtain Eₜ₊₁. "
        "The raw balance is shown before the max(0, ·) constraint; if it is negative, "
        "the final storage is clipped to zero."
    )

@st.fragment
def render_slow_infiltration_explorer() -> None:
    st.markdown("##### Explore parameter effects")
    controls, graph = st.columns([1, 2], gap="large")

    with controls:
        kis = st.slider(
            ":blue[k_is] (1/Δt)",
            0.0,
            0.02,
            0.002,
            0.0001,
            format="%.4f",
            key="eq_kis",
        )

    storage = np.linspace(0.0, 250.0, 251)
    discharge = (
        REFERENCE_AREA_M2 * kis * storage
        / 1000.0
    )

    with graph:
        figure = _response_figure(
            storage,
            [("Qis", discharge, "solid")],
            "Hydrotope storage E (mm)",
            "Qis (m³/Δt)",
            x_range=[0.0, 250.0],
            y_range=[0.0, 2000.0],
        )
        _show_response_figure(figure, "eq_kis_plot")

    st.caption(
        "Illustrative response for a reference hydrotope area of 1 km² and "
        "Δt = 1 time step. Increasing :blue[k_is] steepens the linear "
        "storage–infiltration relationship."
    )


@st.fragment
def render_fast_flow_explorer() -> None:
    st.markdown("##### Explore parameter effects")
    controls, graph = st.columns([1, 2], gap="large")

    with controls:
        thresholds = st.slider(
            ":red[E_min] and :red[E_max] (mm)",
            0.0,
            250.0,
            (20.0, 120.0),
            5.0,
            key="eq_fast_thresholds",
        )
        emin, emax = thresholds
        alpha = st.slider(
            ":red[alpha] (-)",
            0.2,
            6.0,
            2.0,
            0.1,
            key="eq_fast_alpha",
        )
        khyd = st.slider(
            ":red[k_hyd] (m²/Δt)",
            0.0,
            0.01,
            0.0025,
            0.0001,
            format="%.4f",
            key="eq_fast_khyd",
        )

    storage = np.linspace(0.0, 250.0, 501)
    if emax <= emin:
        with graph:
            st.warning("E_max must be larger than E_min.")
        return

    lhyd = 2000.0  # fixed illustrative geometry, m
    active_response = (
        np.maximum(0.0, storage - emin) / (emax - emin)
    ) ** alpha
    active_discharge = (
        active_response * (khyd / lhyd) * REFERENCE_AREA_M2
    )

    # Hysteretic branches following the activation state epsilon:
    # - on the rising limb, fast flow remains inactive until E reaches E_max;
    # - on the falling limb, it remains active until E falls to E_min.
    rising_discharge = np.where(storage >= emax, active_discharge, 0.0)
    falling_discharge = np.where(storage > emin, active_discharge, 0.0)

    with graph:
        figure = go.Figure()

        figure.add_trace(
            go.Scatter(
                x=storage,
                y=rising_discharge,
                mode="lines",
                name="Rising storage",
                line={
                    "color": "#0072B2",
                    "width": 3,
                    "dash": "solid",
                },
            )
        )

        figure.add_trace(
            go.Scatter(
                x=storage,
                y=falling_discharge,
                mode="lines",
                name="Falling storage",
                line={
                    "color": "#E69F00",
                    "width": 3,
                    "dash": "dot",
                },
            )
        )

        figure.add_vline(
            x=emin,
            line_dash="dot",
            annotation_text="Emin",
            annotation_position="top",
        )

        figure.add_vline(
            x=emax,
            line_dash="dot",
            annotation_text="Emax",
            annotation_position="top",
        )

        figure.update_layout(
            height=390,
            margin={"l": 20, "r": 20, "t": 30, "b": 75},
            xaxis_title="Hydrotope storage E (mm)",
            yaxis_title="Qhyd (m³/Δt)",
            hovermode="x unified",
            legend={
                "orientation": "h",
                "x": 0.5,
                "xanchor": "center",
                "y": -0.25,
                "yanchor": "top",
            },
        )

        figure.update_xaxes(
            range=[0.0, 250.0],
            fixedrange=True,
        )

        figure.update_yaxes(
            range=[0.0, 50.0],
            fixedrange=True,
        )

        _show_response_figure(figure, "eq_fast_plot")

    st.caption(
        "Illustrative response for A = 1 km², l_hyd = 2000 m and Δt = 1 time step. "
        "On the rising limb, ε stays 0 until E reaches :red[E_max]. On the falling limb, "
        "ε stays 1 until E falls to :red[E_min]. The separation of the two colored curves "
        "between :red[E_min] and :red[E_max] visualizes the hysteresis."
    )

@st.fragment
def render_secondary_flow_explorer() -> None:
    st.markdown("##### Explore parameter effects")
    controls, graph = st.columns([1, 2], gap="large")

    with controls:
        ksec = st.slider(
            ":green[k_sec] (1/Δt)",
            0.0,
            0.05,
            0.01,
            0.001,
            format="%.3f",
            key="eq_sec_ksec",
        )
        esec = st.slider(
            ":green[E_sec] (mm)",
            0.0,
            250.0,
            150.0,
            5.0,
            key="eq_sec_esec",
        )

    storage = np.linspace(0.0, 300.0, 301)
    discharge = (
        ksec * REFERENCE_AREA_M2 * np.maximum(0.0, storage - esec)
        / 1000.0
    )

    with graph:
        figure = _response_figure(
            storage,
            [("Qsec", discharge, "solid")],
            "Hydrotope storage E (mm)",
            "Qsec (m³/Δt)",
            vertical_lines=[(esec, "Esec")],
            x_range=[0.0, 300.0],
            y_range=[0.0, 5000.0],
        )
        _show_response_figure(figure, "eq_sec_plot")

    st.caption(
        "Illustrative response for a reference hydrotope area of 1 km² and "
        "Δt = 1 time step. :green[E_sec] shifts the activation threshold, while :green[k_sec] controls "
        "the slope above the threshold."
    )


@st.fragment
def render_matrix_conduit_explorer() -> None:
    st.markdown("##### Explore parameter effects")
    controls, graph = st.columns([1, 2], gap="large")

    with controls:
        kmc = st.slider(
            ":violet[k_MC] (mm/Δt)",
            0.0,
            0.2,
            0.02,
            0.001,
            format="%.3f",
            key="eq_mc_kmc",
        )
        amc = st.slider(
            ":violet[a_MC] (-)",
            1.0,
            6.0,
            2.5,
            0.1,
            key="eq_mc_amc",
        )

    difference = np.linspace(-3.0, 3.0, 301)
    discharge = (
        REFERENCE_AREA_M2
        * kmc
        * np.sign(difference)
        * np.abs(difference) ** amc
        / 1000.0
    )

    with graph:
        figure = _response_figure(
            difference,
            [("QMC", discharge, "solid")],
            "Water-level difference M − C (-)",
            "QMC (m³/Δt)",
            horizontal_zero=True,
            x_range=[-3.0, 3.0],
            y_range=[-1000.0, 1000.0],
        )
        _show_response_figure(figure, "eq_mc_plot")

    st.caption(
        "Illustrative response for a recharge area of 1 km² and Δt = 1 time step. "
        ":violet[Q_MC] denotes matrix → conduit exchange when positive; negative values denote "
        "conduit → matrix exchange."
    )


@st.fragment
def render_conduit_loss_explorer() -> None:
    st.markdown("##### Explore parameter effects")
    controls, graph = st.columns([1, 2], gap="large")

    with controls:
        c_loss = st.slider(
            "C_loss",
            0.1,
            5.0,
            2.0,
            0.1,
            key="eq_closs_threshold",
        )

    conduit_storage = np.linspace(0.0, 5.0, 251)
    discharge = (
        np.maximum(0.0, conduit_storage - c_loss)
        * REFERENCE_AREA_M2
        / 1000.0
    )

    with graph:
        figure = _response_figure(
            conduit_storage,
            [("QCloss", discharge, "solid")],
            "Conduit storage level C",
            "QCloss (m³/Δt)",
            vertical_lines=[(c_loss, "C_loss")],
            x_range=[0.0, 5.0],
            y_range=[0.0, 5000.0],
        )
        _show_response_figure(figure, "eq_closs_plot")

    st.caption(
        "Illustrative response for a recharge area of 1 km² and Δt = 1 time step. "
        "The drainage remains zero until C exceeds C_loss, after which excess "
        "conduit storage is removed as bypass flow."
    )


@st.fragment
def render_spring_discharge_explorer() -> None:
    st.markdown("##### Explore parameter effects")
    controls, graph = st.columns([1, 2], gap="large")

    with controls:
        kcs = st.slider(
            ":orange[k_CS] (mm/Δt)",
            0.0,
            0.1,
            0.02,
            0.001,
            format="%.3f",
            key="eq_spring_kcs",
        )
        acs = st.slider(
            ":orange[a_CS] (-)",
            1.0,
            8.0,
            3.0,
            0.1,
            key="eq_spring_acs",
        )
        kms = st.slider(
            ":orange[k_MS] (mm/Δt)",
            0.0,
            0.1,
            0.01,
            0.001,
            format="%.3f",
            key="eq_spring_kms",
        )
        ams = st.slider(
            ":orange[a_MS] (-)",
            1.0,
            8.0,
            1.5,
            0.1,
            key="eq_spring_ams",
        )

    water_level = np.linspace(0.0, 3.0, 301)
    qcs = (
        REFERENCE_AREA_M2 * kcs * water_level ** acs
        / 1000.0
    )
    qms = (
        REFERENCE_AREA_M2 * kms * water_level ** ams
        / 1000.0
    )

    with graph:
        figure = _response_figure(
            water_level,
            [
                ("Conduit → spring (QCS)", qcs, "solid"),
                ("Matrix → spring (QMS)", qms, "dash"),
            ],
            "Compartment water level (-)",
            "Spring-discharge component (m³/Δt)",
            x_range=[0.0, 3.0],
            y_range=[0.0, 1000.0],
        )
        _show_response_figure(figure, "eq_spring_plot")

    st.caption(
        "Illustrative response for a recharge area of 1 km² and Δt = 1 time step. "
        "The :orange[k] parameters scale discharge magnitude, whereas the :orange[a] parameters "
        "control the curvature/nonlinearity of the response."
    )


# -----------------------------------------------------------------------------
# Page title and introduction
# -----------------------------------------------------------------------------
st.markdown(
    load_colored_md("md_lukars_model_01.md")
)


# -----------------------------------------------------------------------------
# Some applications 
# -----------------------------------------------------------------------------
#st.subheader(
 #   ":blue[Applications of LuKARS]",
 #   divider="blue",
#)
#st.markdown(
 #   load_md(
  #      MD_DIR,
   #     "md_lukars_model_01_more.md",
  #      LANGUAGE,
   # )
#)

# -----------------------------------------------------------------------------
# Learning objectives
# -----------------------------------------------------------------------------
st.subheader(
    "🎓 :blue[Learning objectives]",
    divider="blue",
)

st.markdown(
    load_colored_md("md_lukars_model_learning_objectives.md")
)

# -----------------------------------------------------------------------------
# Conceptual structure
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[Conceptual structure of LuKARS]",
    divider="blue",
)

st.markdown(
    load_colored_md("md_lukars_model_02.md")
)

col1, col2, col3 = st.columns([0.4, 4.2, 0.4])
with col2:
    st.image(
        IMAGE_DIR/"lukars_conceptual_model.png",
        caption="Conceptual structure of LuKARS with a user-defined number of hydrotopes and lower matrix and conduit compartments.",
        use_container_width=True,
    )


st.markdown(
    """
**Color coding:** :blue[Qis / slow infiltration] ·
:red[Qhyd / fast hydrotope flow] ·
:green[Qsec / secondary discharge] ·
:violet[QMC / matrix-conduit exchange] ·
:orange[QMS, QCS and spring discharge]
"""
)


# -----------------------------------------------------------------------------
# Main model components
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[Main model components]",
    divider="blue",
)

col1, col2, col3 = st.columns([1, 20, 1])
with col2:
    st.image(
        IMAGE_DIR/"main_LuKARS_component_1.png",
       # caption="Overview of the main conceptual elements of the model",
        use_container_width=True,
    )
    

# -----------------------------------------------------------------------------
# Semi-distributed representation
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[How is spatial variability represented?]",
    divider="blue",
)

st.markdown(
    load_colored_md("md_lukars_model_06.md")
)

with st.expander("Show more about hydrotopes"):
    st.markdown(
        load_colored_md("md_lukars_model_07.md")
    )


# -----------------------------------------------------------------------------
# Flow pathways
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[Flow pathways represented by the model]",
    divider="blue",
)

st.markdown(
    load_colored_md("md_lukars_model_08.md")
)

flow_col1, flow_col2 = st.columns(2, gap="small")

with flow_col1:
    with st.container(border=True):
        st.markdown("##### Slow pathway")
        st.markdown(
            r"""
Water infiltrates from a hydrotope toward the matrix compartment through
the flux :blue[$Q_{\mathrm{is}}$]. This pathway contributes to slower storage and
recession behaviour.
"""
        )

with flow_col2:
    with st.container(border=True):
        st.markdown("##### Fast pathway")
        st.markdown(
            r"""
Once the hydrotope storage exceeds the activation threshold, rapid flow
:red[$Q_{\mathrm{hyd}}$] can transfer water toward the conduit system and produce
a faster spring response.
"""
        )


# -----------------------------------------------------------------------------
# Governing equations
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[Selected governing equations]",
    divider="blue",
)

st.markdown(
    load_colored_md("md_lukars_model_09.md")
)

st.info(
    load_colored_md("md_lukars_model_16.md")
)

with st.expander("Hydrotope water balance", expanded=True):
    st.latex(
        r"E_{i,t+1}="
        r"\max\left["
        r"0,"
        r"E_{i,t}+"
        r"\left("
        r"S_{i,t}-"
        r"\frac{Q_{\mathrm{sec},i,t}+Q_{\mathrm{hyd},i,t}+Q_{\mathrm{is},i,t}}{A_i}"
        r"\right)"
        r"\Delta t"
        r"\right]"
    )

    st.markdown(
        load_colored_md("md_lukars_model_10.md")
    )

    render_water_balance_explorer()

with st.expander("Slow infiltration toward the matrix"):
    st.latex(
        r"Q_{\mathrm{is},i,t}="
        r"k_{\mathrm{is},i}"
        r"E_{i,t}"
        r"A_i"
    )

    st.markdown(
        load_colored_md("md_lukars_model_11.md")
    )

    render_slow_infiltration_explorer()

with st.expander("Fast hydrotope flow"):
    st.latex(
        r"Q_{\mathrm{hyd},i,t}="
        r"\varepsilon_{i,t}"
        r"\left("
        r"\frac{\max(0,E_{i,t}-E_{\min,i})}"
        r"{E_{\max,i}-E_{\min,i}}"
        r"\right)^{\alpha_i}"
        r"\frac{k_{\mathrm{hyd},i}}{l_{\mathrm{hyd},i}}"
        r"A_i"
    )

    st.markdown(
        load_colored_md("md_lukars_model_12.md")
    )

    st.markdown("##### Activation and deactivation")
    st.markdown(
        load_colored_md("md_lukars_model_13.md")
    )

    render_fast_flow_explorer()

with st.expander("Secondary spring discharge"):
    st.latex(
        r"Q_{\mathrm{sec},i,t}="
        r"k_{\mathrm{sec},i}"
        r"\max\left(0,E_{i,t}-E_{\mathrm{sec},i}\right)"
        r"A_i"
    )

    st.markdown(
        load_colored_md("md_lukars_model_13_sec.md")
    )

    render_secondary_flow_explorer()

with st.expander("Matrix-conduit exchange"):
    st.latex(
        r"Q_{\mathrm{MC},t}="
        r"R_a"
        r"k_{\mathrm{MC}}"
        r"\operatorname{sgn}(M_t-C_t)"
        r"|M_t-C_t|^{a_{\mathrm{MC}}}"
    )

    st.markdown(
        load_colored_md("md_lukars_model_14.md")
    )

    render_matrix_conduit_explorer()

with st.expander("Conduit drainage (bypass flow)"):
    st.latex(
        r"Q_{\mathrm{Closs},t}="
        r"\begin{cases}"
        r"\left(C_t-C_{\mathrm{loss}}\right)\dfrac{R_a}{\Delta t},"
        r"& C_t>C_{\mathrm{loss}},\\[4pt]"
        r"0,"
        r"& C_t\leq C_{\mathrm{loss}}."
        r"\end{cases}"
    )

    st.markdown(
        load_colored_md("md_lukars_model_14_closs.md")
    )

    render_conduit_loss_explorer()

with st.expander("Spring discharge components"):
    equation_col1, equation_col2 = st.columns(2, gap="large")

    with equation_col1:
        st.markdown("##### Conduit contribution")
        st.latex(
            r"Q_{\mathrm{CS},t}="
            r"R_a"
            r"k_{\mathrm{CS}}"
            r"C_t^{a_{\mathrm{CS}}}"
        )

    with equation_col2:
        st.markdown("##### Matrix contribution")
        st.latex(
            r"Q_{\mathrm{MS},t}="
            r"R_a"
            r"k_{\mathrm{MS}}"
            r"M_t^{a_{\mathrm{MS}}}"
        )

    st.markdown(
        load_colored_md("md_lukars_model_15.md")
    )

    render_spring_discharge_explorer()


# -----------------------------------------------------------------------------
# Take-home messages
# -----------------------------------------------------------------------------
st.subheader(
    "🎯 :blue[Main take-home messages]",
    divider="blue",
)

st.markdown(
    load_colored_md("md_lukars_model_19.md")
)


# -----------------------------------------------------------------------------
# Assessment
# -----------------------------------------------------------------------------
st.subheader(
    "❓ :blue[Check your understanding]",
    divider="blue",
)

st.markdown(
    load_colored_md("md_lukars_model_20.md")
)

render_assessment_fragment(
    QUESTIONS_DIR/"lukars_model_ass.json",
    "lukars_model_self_assessment",
    "🧠 **Show the self-assessment**",
    default_open=False,
)


# -----------------------------------------------------------------------------
# Further learning
# -----------------------------------------------------------------------------
st.subheader(
    "📖 :blue[Further learning material]",
    divider="blue",
)

st.markdown(
    load_colored_md("md_lukars_model_21.md")
)


# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
columns_lic = st.columns((4, 1))

with columns_lic[0]:
    st.markdown(
        f'Developed by {", ".join(author_list)} ({year}). '
        f"<br> {institution_text}",
        unsafe_allow_html=True,
    )

with columns_lic[1]:
    st.image(IMAGE_DIR/"CC_BY-SA_icon.png")
