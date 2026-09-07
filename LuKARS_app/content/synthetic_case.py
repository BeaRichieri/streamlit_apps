from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from app_utils import load_md


# -----------------------------------------------------------------------------
# Fixed page settings and project paths
# -----------------------------------------------------------------------------
LANGUAGE = "en"

BASE_DIR = Path(st.session_state.get("BASE_DIR", Path(".")))
CONTENT_DIR = Path(st.session_state.get("CONTENT_DIR", BASE_DIR / "content"))
ASSETS_DIR = Path(st.session_state.get("ASSETS_DIR", BASE_DIR / "assets"))
IMAGE_DIR = Path(st.session_state.get("IMAGE_DIR", ASSETS_DIR / "images"))
MD_DIR = Path(st.session_state.get("MD_DIR", BASE_DIR / "md"))
QUESTIONS_DIR = Path(st.session_state.get("QUESTIONS_DIR", BASE_DIR / "questions"))

st.session_state.language = LANGUAGE


# -----------------------------------------------------------------------------
# Authors, institutions, and year
# -----------------------------------------------------------------------------
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
# Colors: same convention used elsewhere in the LuKARS app
# -----------------------------------------------------------------------------
PRECIP_COLOR = "#A6CEE3"
QIS_COLOR = "#1F77B4"
QHYD_COLOR = "#D62728"
QMC_COLOR = "#9467BD"
QMS_COLOR = "#F5A623"
QCS_COLOR = "#E67E22"
QSPRING_COLOR = "#FF7F0E"
QLOSS_COLOR = "#4AA3FF"
SIMPLE_RESERVOIR_COLOR = "#6B6B6B"

E_COLOR = "#D62728"
M_COLOR = "#6F6F6F"
C_COLOR = "#111111"


# -----------------------------------------------------------------------------
# Synthetic experiment defaults
# -----------------------------------------------------------------------------
SYNTHETIC_PRESET = {
    # One synthetic hydrotope, fixed at 1 km2.
    "dt": 1.0,                    # h
    "TotalArea": 1.0e6,           # m2
    "areas_frac": np.array([1.0]),
    "areas": np.array([1.0e6]),

    # Hydrotope parameters.
    "kis": np.array([8.0e-5]),     # 1/h
    "Emin": np.array([10.0]),      # mm
    "Emax": np.array([25.0]),      # mm
    "alpha": np.array([1.5]),      # -
    "khy": np.array([500.0]),      # m2/h
    "lhy": np.array([1600.0]),     # m

    # Matrix-conduit parameters.
    "kMC": 1.0e-2,
    "aMC": 1.5,
    "C_loss": 20.0,
    "M_loss": 1.0e8,

    # Spring-release parameters.
    "kMS": 5.0e-3,
    "aMS": 1.0,
    "kCS": 1.0e-2,
    "aCS": 1.8,

    # Initial states.
    "E0": 1.0,
    "Qis0": 0.0,   # recomputed from E0 and kis below
    "Qhy0": 0.0,
    "M0": 1.0,
    "C0": 0.5,
}

EVENT_DEFAULTS = {
    "shape": "Rectangular",
    "total_mm": 60.0,
    "duration_hours": 24.0,
}

SIMPLE_RESERVOIR_DEFAULTS = {
    # Same formulation as the lumped-reservoir page:
    # dS/dt = P - ET - Q ; Q = a S^b
    # Time unit on this page is hour.
    "a": 0.010 / 24.0,
    "b": 1.3,
    "S0": 5.0,
}


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
@st.cache_resource
def load_lukars_model(model_path: str):
    """Load the same LuKARS run_model function used by the case-study pages."""
    path = Path(model_path)

    if not path.exists():
        raise FileNotFoundError(f"LuKARS model file not found: {path}")

    module_spec = importlib.util.spec_from_file_location(
        "lukars_model_for_synthetic_page",
        path,
    )

    if module_spec is None or module_spec.loader is None:
        raise ImportError(f"Could not load LuKARS model module from: {path}")

    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)

    if not hasattr(module, "run_model"):
        raise AttributeError("The model module does not define 'run_model'.")

    return module.run_model


def float_slider(
    label: str,
    value: float,
    lower: float,
    upper: float,
    step: float,
    key: str,
    number_format: str | None = None,
    help_text: str | None = None,
) -> float:
    """Create a float slider while keeping defaults inside the allowed range."""
    return st.slider(
        label,
        min_value=float(lower),
        max_value=float(upper),
        value=float(np.clip(value, lower, upper)),
        step=float(step),
        key=key,
        format=number_format,
        help=help_text,
    )


def log_slider(
    label: str,
    value: float,
    lower: float,
    upper: float,
    key: str,
    *,
    n_steps: int = 161,
    allow_zero: bool = False,
    help_text: str | None = None,
) -> float:
    """Logarithmic select-slider with the actual parameter values displayed."""
    if lower <= 0.0 or upper <= lower:
        raise ValueError("Invalid bounds for logarithmic slider.")

    default = float(value)
    current = float(st.session_state.get(key, default))

    if allow_zero and np.isclose(current, 0.0):
        current = 0.0
    else:
        current = float(np.clip(current, lower, upper))

    options = [float(v) for v in np.geomspace(lower, upper, n_steps)]
    options.append(float(np.clip(default, lower, upper)))

    if current > 0.0:
        options.append(current)

    if allow_zero:
        options.append(0.0)

    options = sorted(set(options))

    def formatter(v: float) -> str:
        if np.isclose(v, 0.0):
            return "0"
        return f"{v:.2e}"

    return float(
        st.select_slider(
            label,
            options=options,
            value=current,
            key=key,
            format_func=formatter,
            help=help_text,
        )
    )


def clear_synthetic_state() -> None:
    """Restore the complete synthetic experiment to its defaults."""
    for state_key in list(st.session_state):
        if state_key.startswith("synthetic_"):
            del st.session_state[state_key]


def build_precipitation(
    shape: str,
    total_mm: float,
    duration_hours: float,
    *,
    simulation_hours: float = 20.0 * 24.0,
    event_start_hour: float = 48.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Create an hourly rectangular or triangular event with exact total depth."""
    dt_hours = 1.0
    n_steps = int(round(simulation_hours / dt_hours)) + 1
    time_hours = np.arange(n_steps, dtype=float) * dt_hours
    precipitation = np.zeros(n_steps, dtype=float)

    duration_steps = max(int(round(duration_hours / dt_hours)), 1)
    start_index = int(round(event_start_hour / dt_hours))
    end_index = min(start_index + duration_steps, n_steps)

    event_length = max(end_index - start_index, 1)

    if shape == "Rectangular":
        event_weights = np.ones(event_length, dtype=float)
    else:
        # Symmetric triangle sampled at hourly time-step centres.
        centres = (np.arange(event_length, dtype=float) + 0.5) / event_length
        event_weights = 1.0 - np.abs(2.0 * centres - 1.0)
        event_weights = np.maximum(event_weights, 1e-12)

    # Normalization guarantees that rectangular and triangular events contain
    # exactly the same total precipitation selected by the user.
    event_depths = total_mm * event_weights / np.sum(event_weights)
    precipitation[start_index:end_index] = event_depths

    return time_hours, precipitation


def simulate_simple_reservoir(
    precipitation_mm_h: np.ndarray,
    *,
    area_m2: float,
    a: float,
    b: float,
    initial_storage_mm: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Simulate dS/dt=P-Q, Q=a*S^b with an hourly time step."""
    n = len(precipitation_mm_h)
    storage = np.zeros(n, dtype=float)
    discharge_mm_h = np.zeros(n, dtype=float)

    storage[0] = max(float(initial_storage_mm), 0.0)
    dt_hours = 1.0

    for i in range(n - 1):
        discharge_mm_h[i] = max(a * storage[i] ** b, 0.0)

        storage_change = (
            precipitation_mm_h[i]
            - discharge_mm_h[i]
        )

        storage[i + 1] = max(
            0.0,
            storage[i] + storage_change * dt_hours,
        )

    discharge_mm_h[-1] = max(a * storage[-1] ** b, 0.0)

    discharge_m3_s = (
        discharge_mm_h * area_m2 / 1000.0 / 3600.0
    )

    return storage, discharge_m3_s


def event_preview_figure(
    time_hours: np.ndarray,
    precipitation: np.ndarray,
) -> go.Figure:
    figure = go.Figure()

    figure.add_trace(
        go.Bar(
            x=time_hours,
            y=precipitation,
            name="Precipitation",
            marker_color=PRECIP_COLOR,
            hovertemplate=(
                "Time: %{x:.0f} h<br>"
                "Precipitation: %{y:.2f} mm h⁻¹<extra></extra>"
            ),
        )
    )

    figure.update_layout(
        height=285,
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
        xaxis_title="Time [hours]",
        yaxis_title="Precipitation [mm h⁻¹]",
        showlegend=False,
        bargap=0.02,
        uirevision="synthetic-event-preview",
    )

    figure.update_xaxes(range=[0.0, 8.0 * 24.0], fixedrange=False)
    figure.update_yaxes(rangemode="tozero", fixedrange=False)

    return figure


def spring_response_figure(
    time_hours: np.ndarray,
    precipitation: np.ndarray,
    q_lukars: np.ndarray,
    q_simple: np.ndarray,
) -> go.Figure:
    figure = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.27, 0.73],
        vertical_spacing=0.07,
    )

    figure.add_trace(
        go.Bar(
            x=time_hours,
            y=precipitation,
            name="Precipitation",
            marker_color=PRECIP_COLOR,
            hovertemplate=(
                "Time: %{x:.0f} h<br>"
                "P: %{y:.2f} mm h⁻¹<extra></extra>"
            ),
        ),
        row=1,
        col=1,
    )

    figure.add_trace(
        go.Scatter(
            x=time_hours,
            y=q_lukars,
            mode="lines",
            name="LuKARS spring discharge",
            line={"color": QSPRING_COLOR, "width": 3},
            hovertemplate=(
                "Time: %{x:.0f} h<br>"
                "Qspring: %{y:.4f} m³ s⁻¹<extra></extra>"
            ),
        ),
        row=2,
        col=1,
    )

    figure.add_trace(
        go.Scatter(
            x=time_hours,
            y=q_simple,
            mode="lines",
            name="Simple reservoir",
            line={
                "color": SIMPLE_RESERVOIR_COLOR,
                "width": 2.5,
                "dash": "dash",
            },
            hovertemplate=(
                "Time: %{x:.0f} h<br>"
                "Qsimple: %{y:.4f} m³ s⁻¹<extra></extra>"
            ),
        ),
        row=2,
        col=1,
    )

    figure.update_yaxes(
        title_text="P [mm h⁻¹]",
        rangemode="tozero",
        row=1,
        col=1,
    )
    figure.update_yaxes(
        title_text="Discharge [m³ s⁻¹]",
        rangemode="tozero",
        row=2,
        col=1,
    )
    figure.update_xaxes(
        title_text="Time [hours]",
        row=2,
        col=1,
    )

    figure.update_layout(
        height=600,
        margin={"l": 20, "r": 20, "t": 25, "b": 25},
        hovermode="x unified",
        legend={
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": -0.12,
            "yanchor": "top",
        },
        bargap=0.02,
        uirevision="synthetic-spring-response",
    )

    return figure


def internal_flux_figure(
    time_hours: np.ndarray,
    run_up: np.ndarray,
    run_bot: np.ndarray,
) -> go.Figure:
    figure = go.Figure()

    series = [
        (
            "Qis - Slow infiltration",
            np.asarray(run_up[1, :, 0], dtype=float),
            QIS_COLOR,
            "solid",
            True,
        ),
        (
            "Qhyd - Fast hydrotope flow",
            np.asarray(run_up[2, :, 0], dtype=float),
            QHYD_COLOR,
            "solid",
            True,
        ),
        (
            "QMC - Matrix-conduit exchange",
            np.asarray(run_bot[6], dtype=float),
            QMC_COLOR,
            "solid",
            True,
        ),
        (
            "QMS - Matrix to spring",
            np.asarray(run_bot[4], dtype=float),
            QMS_COLOR,
            "solid",
            True,
        ),
        (
            "QCS - Conduit to spring",
            np.asarray(run_bot[5], dtype=float),
            QCS_COLOR,
            "solid",
            True,
        ),
        (
            "QCloss - Conduit loss",
            np.asarray(run_bot[2], dtype=float),
            QLOSS_COLOR,
            "dot",
            "legendonly",
        ),
        (
            "Qspring - Total spring discharge",
            np.asarray(run_bot[7], dtype=float),
            QSPRING_COLOR,
            "dash",
            "legendonly",
        ),
    ]

    for name, values, color, dash, visible in series:
        figure.add_trace(
            go.Scatter(
                x=time_hours,
                y=values,
                mode="lines",
                name=name,
                visible=visible,
                line={
                    "color": color,
                    "width": 2.3,
                    "dash": dash,
                },
            )
        )

    figure.add_hline(
        y=0.0,
        line_dash="dot",
        line_width=1,
    )

    figure.update_layout(
        height=500,
        margin={"l": 20, "r": 20, "t": 25, "b": 25},
        xaxis_title="Time [hours]",
        yaxis_title="Flux [m³ s⁻¹]",
        hovermode="x unified",
        legend={
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": -0.18,
            "yanchor": "top",
        },
        # Keep legend visibility, zoom and pan when parameter values change.
        uirevision="synthetic-internal-fluxes",
    )

    return figure


def storage_figure(
    time_hours: np.ndarray,
    run_up: np.ndarray,
    run_bot: np.ndarray,
) -> go.Figure:
    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=time_hours,
            y=np.asarray(run_up[0, :, 0], dtype=float),
            mode="lines",
            name="E - Hydrotope storage",
            line={"color": E_COLOR, "width": 2.5},
        )
    )

    figure.add_trace(
        go.Scatter(
            x=time_hours,
            y=np.asarray(run_bot[9], dtype=float),
            mode="lines",
            name="M - Matrix storage",
            line={"color": M_COLOR, "width": 2.5},
        )
    )

    figure.add_trace(
        go.Scatter(
            x=time_hours,
            y=np.asarray(run_bot[8], dtype=float),
            mode="lines",
            name="C - Conduit storage",
            line={"color": C_COLOR, "width": 2.5},
        )
    )

    figure.update_layout(
        height=430,
        margin={"l": 20, "r": 20, "t": 25, "b": 25},
        xaxis_title="Time [hours]",
        yaxis_title="Storage / water level [mm]",
        hovermode="x unified",
        legend={
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": -0.16,
            "yanchor": "top",
        },
        uirevision="synthetic-storages",
    )

    figure.update_yaxes(rangemode="tozero")

    return figure


# -----------------------------------------------------------------------------
# Load the common LuKARS model engine
# -----------------------------------------------------------------------------
try:
    run_model = load_lukars_model(
        str(ASSETS_DIR / "lukars_model.py")
    )
except Exception as exc:
    st.error(
        "The synthetic page uses the same model engine as the other LuKARS "
        f"pages, but `{ASSETS_DIR / 'lukars_model.py'}` could not be loaded."
    )
    st.exception(exc)
    st.stop()


# -----------------------------------------------------------------------------
# Page title and purpose
# -----------------------------------------------------------------------------
st.title("🧪 Synthetic experiment")

st.markdown(load_md(MD_DIR, "md_synthetic_01.md", LANGUAGE))

st.info(load_md(MD_DIR, "md_synthetic_02.md", LANGUAGE))


# -----------------------------------------------------------------------------
# 1. Define precipitation event
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[1. Define a precipitation event]",
    divider="blue",
)

control_col, preview_col = st.columns(
    [0.85, 1.65],
    gap="large",
)

with control_col:
    event_shape = st.radio(
        "Event shape",
        ["Rectangular", "Triangular"],
        index=0,
        horizontal=True,
        key="synthetic_event_shape",
    )

    total_precipitation = st.slider(
        "Total precipitation [mm]",
        min_value=10.0,
        max_value=150.0,
        value=EVENT_DEFAULTS["total_mm"],
        step=5.0,
        key="synthetic_event_total",
        help=(
            "The total precipitation is kept identical when switching "
            "between rectangular and triangular events."
        ),
    )

    event_duration_hours = st.slider(
        "Event duration [hours]",
        min_value=6.0,
        max_value=72.0,
        value=EVENT_DEFAULTS["duration_hours"],
        step=6.0,
        key="synthetic_event_duration",
    )

time_hours, precipitation = build_precipitation(
    event_shape,
    total_precipitation,
    event_duration_hours,
)

with preview_col:
    st.plotly_chart(
        event_preview_figure(
            time_hours,
            precipitation,
        ),
        use_container_width=True,
        key="synthetic_event_plot",
        config={
            "displaylogo": False,
            "scrollZoom": False,
        },
    )

max_intensity_hour = float(np.max(precipitation))


st.markdown(
    """
    <style>
    div[data-testid="stMetricLabel"] p {
        font-size: 14px;
    }

    div[data-testid="stMetricValue"] {
        font-size: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

metric_col1, metric_col2, metric_col3 = st.columns(3)
metric_col1.metric(
    "Event type",
    event_shape,
)
metric_col2.metric(
    "Total precipitation",
    f"{np.sum(precipitation):.1f} mm",
)
metric_col3.metric(
    "Maximum precipitation intensity",
    f"{max_intensity_hour:.2f} mm h⁻¹",
)


# -----------------------------------------------------------------------------
# 2. Conceptual comparison
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[2. From precipitation to spring discharge]",
    divider="blue",
)

st.markdown(load_md(MD_DIR, "md_synthetic_03.md", LANGUAGE))

with st.container(border=True):
    simple_col, lukars_col = st.columns(
        2,
        gap="medium",
    )

    with simple_col:
        st.markdown("#### Simple reservoir")

        st.markdown(
            load_md(
                MD_DIR,
                "md_synthetic_04_simple_reservoir.md",
                LANGUAGE,
            )
        )

    with lukars_col:
        st.markdown("#### LuKARS")

        st.markdown(
            load_md(
                MD_DIR,
                "md_synthetic_05_lukars.md",
                LANGUAGE,
            )
        )


# -----------------------------------------------------------------------------
# 3. Parameters
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[3. Explore the model parameters]",
    divider="blue",
)

st.markdown(load_md(MD_DIR, "md_synthetic_06.md", LANGUAGE))

# -----------------------------------------------------------------------------
# Three LuKARS parameter groups
# -----------------------------------------------------------------------------
hydro_col, mc_col, spring_col = st.columns(
    3,
    gap="small",
)


# -----------------------------------------------------------------------------
# Hydrotope parameters
# -----------------------------------------------------------------------------
with hydro_col:

    with st.expander(
        "Hydrotope parameters",
        expanded=False,
    ):

        kis = log_slider(
            ":blue[kis] [1/h]",
            float(SYNTHETIC_PRESET["kis"][0]),
            1e-7,
            1e-3,
            "synthetic_kis",
            allow_zero=True,
        )

        emin = float_slider(
            ":red[Emin] [mm]",
            float(SYNTHETIC_PRESET["Emin"][0]),
            1.0,
            50.0,
            0.5,
            "synthetic_emin",
        )

        emax = float_slider(
            ":red[Emax] [mm]",
            float(SYNTHETIC_PRESET["Emax"][0]),
            5.0,
            120.0,
            1.0,
            "synthetic_emax",
        )

        alpha = float_slider(
            ":red[alpha] [-]",
            float(SYNTHETIC_PRESET["alpha"][0]),
            1.0,
            3.0,
            0.05,
            "synthetic_alpha",
        )

        khy = log_slider(
            ":red[khyd] [m²/h]",
            float(SYNTHETIC_PRESET["khy"][0]),
            1.0,
            10000.0,
            "synthetic_khyd",
        )

        lhy = float_slider(
            ":red[lhyd] [m]",
            float(SYNTHETIC_PRESET["lhy"][0]),
            500.0,
            6500.0,
            50.0,
            "synthetic_lhyd",
        )


# -----------------------------------------------------------------------------
# Matrix-conduit parameters
# -----------------------------------------------------------------------------
with mc_col:

    with st.expander(
        "Matrix–conduit parameters",
        expanded=False,
    ):

        kmc = log_slider(
            ":violet[kMC]",
            SYNTHETIC_PRESET["kMC"],
            1e-5,
            1e-1,
            "synthetic_kmc",
        )

        amc = float_slider(
            ":violet[aMC]",
            SYNTHETIC_PRESET["aMC"],
            1.0,
            3.0,
            0.05,
            "synthetic_amc",
        )

        c_loss = log_slider(
            r"$\color{#4AA3FF}{C_{\mathrm{loss}}}$ [mm]",
            SYNTHETIC_PRESET["C_loss"],
            1.0,
            100.0,
            "synthetic_c_loss",
        )

        st.caption(
            "Matrix-loss threshold is kept effectively inactive "
            "(M_loss = 10⁸ mm)."
        )


# -----------------------------------------------------------------------------
# Transfers to spring
# -----------------------------------------------------------------------------
with spring_col:

    with st.expander(
        "Transfers to spring",
        expanded=False,
    ):

        kms = log_slider(
            ":orange[kMS]",
            SYNTHETIC_PRESET["kMS"],
            1e-5,
            1e-1,
            "synthetic_kms",
            allow_zero=True,
        )

        ams = float_slider(
            ":orange[aMS]",
            SYNTHETIC_PRESET["aMS"],
            1.0,
            3.0,
            0.05,
            "synthetic_ams",
        )

        kcs = log_slider(
            ":orange[kCS]",
            SYNTHETIC_PRESET["kCS"],
            1e-4,
            1e0,
            "synthetic_kcs",
        )

        acs = float_slider(
            ":orange[aCS]",
            SYNTHETIC_PRESET["aCS"],
            1.0,
            4.0,
            0.05,
            "synthetic_acs",
        )


# -----------------------------------------------------------------------------
# Simple reservoir
# -----------------------------------------------------------------------------
with st.expander(
    "Simple reservoir parameters",
    expanded=False,
):

    reservoir_col1, reservoir_col2, reservoir_col3 = st.columns(
        3,
        gap="large",
    )

    with reservoir_col1:
        reservoir_a = st.slider(
            "Discharge parameter a",
            min_value=0.001 / 24.0,
            max_value=0.050 / 24.0,
            value=SIMPLE_RESERVOIR_DEFAULTS["a"],
            step=0.001 / 24.0,
            format="%.5f",
            key="synthetic_reservoir_a",
            help=(
                "Same reservoir formulation used on the lumped-reservoir page, "
                "expressed here with an hourly time unit."
            ),
        )

    with reservoir_col2:
        reservoir_b = st.slider(
            "Nonlinearity parameter b [-]",
            min_value=1.0,
            max_value=3.0,
            value=SIMPLE_RESERVOIR_DEFAULTS["b"],
            step=0.1,
            key="synthetic_reservoir_b",
        )

    with reservoir_col3:
        reservoir_s0 = st.slider(
            "Initial storage S₀ [mm]",
            min_value=0.0,
            max_value=20.0,
            value=SIMPLE_RESERVOIR_DEFAULTS["S0"],
            step=0.5,
            key="synthetic_reservoir_s0",
        )

# Reset button
reset_col1, reset_col2 = st.columns([5, 1])

with reset_col2:
    st.button(
        "Reset experiment",
        use_container_width=True,
        on_click=clear_synthetic_state,
        key="synthetic_reset_button",
    )


# -----------------------------------------------------------------------------
# Validate and run
# -----------------------------------------------------------------------------
if emax <= emin:
    st.error("Emax must be larger than Emin.")
    st.stop()

params = {
    "dt": 1.0,
    "TotalArea": float(SYNTHETIC_PRESET["TotalArea"]),
    "areas_frac": np.array([1.0], dtype=float),
    "areas": np.array([SYNTHETIC_PRESET["TotalArea"]], dtype=float),
    "kis": np.array([kis], dtype=float),
    "Emin": np.array([emin], dtype=float),
    "Emax": np.array([emax], dtype=float),
    "alpha": np.array([alpha], dtype=float),
    "khy": np.array([khy], dtype=float),
    "lhy": np.array([lhy], dtype=float),
    "kMC": float(kmc),
    "aMC": float(amc),
    "C_loss": float(c_loss),
    "M_loss": float(SYNTHETIC_PRESET["M_loss"]),
    "kMS": float(kms),
    "aMS": float(ams),
    "kCS": float(kcs),
    "aCS": float(acs),
    "E0": float(SYNTHETIC_PRESET["E0"]),
    "Qhy0": 0.0,
    "M0": float(SYNTHETIC_PRESET["M0"]),
    "C0": float(SYNTHETIC_PRESET["C0"]),
}

# Physically consistent slow-infiltration flux at the initial hydrotope state.
params["Qis0"] = (
    params["areas"][0]
    * params["kis"][0]
    * params["E0"]
)

try:
    run_up, run_bot = run_model(
        precipitation.astype(float),
        params,
    )

    run_up = np.asarray(run_up, dtype=float)
    run_bot = np.asarray(run_bot, dtype=float)

except Exception as exc:
    st.error("LuKARS could not complete the synthetic simulation.")
    st.exception(exc)
    st.stop()

if (
    run_up.shape[1] != len(time_hours)
    or run_bot.shape[1] != len(time_hours)
    or not np.all(np.isfinite(run_up))
    or not np.all(np.isfinite(run_bot))
):
    st.error(
        "The selected parameter combination produced invalid model results. "
        "Reset the experiment or choose less extreme parameter values."
    )
    st.stop()

simple_storage, simple_discharge = simulate_simple_reservoir(
    precipitation,
    area_m2=float(params["TotalArea"]),
    a=float(reservoir_a),
    b=float(reservoir_b),
    initial_storage_mm=float(reservoir_s0),
)

q_lukars = np.asarray(run_bot[7], dtype=float)


# -----------------------------------------------------------------------------
# 4. Spring response
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[4. Spring response]",
    divider="blue",
)

st.markdown(load_md(MD_DIR, "md_synthetic_07.md", LANGUAGE))

st.plotly_chart(
    spring_response_figure(
        time_hours,
        precipitation,
        q_lukars,
        simple_discharge,
    ),
    use_container_width=True,
    key="synthetic_spring_response_plot",
    config={
        "displaylogo": False,
        "scrollZoom": True,
    },
)


# -----------------------------------------------------------------------------
# 5. Internal fluxes
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[5. What happens inside LuKARS?]",
    divider="blue",
)

st.markdown(load_md(MD_DIR, "md_synthetic_08.md", LANGUAGE))

st.plotly_chart(
    internal_flux_figure(
        time_hours,
        run_up,
        run_bot,
    ),
    use_container_width=True,
    key="synthetic_internal_flux_plot",
    config={
        "displaylogo": False,
        "scrollZoom": True,
    },
)


# -----------------------------------------------------------------------------
# 6. Internal storages
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[6. Internal storages]",
    divider="blue",
)

st.markdown(load_md(MD_DIR, "md_synthetic_09.md", LANGUAGE))

st.plotly_chart(
    storage_figure(
        time_hours,
        run_up,
        run_bot,
    ),
    use_container_width=True,
    key="synthetic_storage_plot",
    config={
        "displaylogo": False,
        "scrollZoom": True,
    },
)


# -----------------------------------------------------------------------------
# Main take-home message
# -----------------------------------------------------------------------------
st.subheader(
    "🎯 :blue[Main take-home message]",
    divider="blue",
)

st.success(load_md(MD_DIR, "md_synthetic_10.md", LANGUAGE))


# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown("---")

footer_col1, footer_col2 = st.columns((4, 1))

with footer_col1:
    st.markdown(
        f'Developed by {", ".join(author_list)} ({year}). '
        f"<br>{institution_text}",
        unsafe_allow_html=True,
    )

with footer_col2:
    license_icon = IMAGE_DIR / "CC_BY-SA_icon.png"
    if license_icon.exists():
        st.image(str(license_icon))
