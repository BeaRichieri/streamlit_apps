from __future__ import annotations

import importlib.util
import json
import re
import threading
import time
import uuid
from copy import deepcopy
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from streamlit_book import multiple_choice

from app_utils import load_md, render_toggle_container


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
# Same colors as in the LuKARS model-description page.
CLOSS_COLOR = "#4AA3FF"

PARAMETER_COLORS = {
    # Slow infiltration
    r"k_{\mathrm{is}}": "blue",
    r"k_{\mathrm{is},i}": "blue",

    # Fast hydrotope flow
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

    # Matrix-conduit exchange
    r"k_{\mathrm{MC}}": "violet",
    r"a_{\mathrm{MC}}": "violet",

    # Spring discharge components
    r"k_{\mathrm{MS}}": "orange",
    r"a_{\mathrm{MS}}": "orange",
    r"k_{\mathrm{CS}}": "orange",
    r"a_{\mathrm{CS}}": "orange",
}


def color_parameter_markdown(markdown_text: str) -> str:
    """Color LuKARS parameter notation while preserving surrounding text."""

    pattern = re.compile(
        r"(?:\$(?P<dollar>[^$]+)\$|\\\((?P<paren>.*?)\\\))"
    )

    def replace_math(match: re.Match) -> str:
        expression = (
            match.group("dollar")
            if match.group("dollar") is not None
            else match.group("paren")
        )

        if expression in {
            r"C_{\mathrm{loss}}",
            r"C_{\mathrm{loss},t}",
        }:
            return rf"$\color{{{CLOSS_COLOR}}}{{{expression}}}$"

        color = PARAMETER_COLORS.get(expression)

        if color is None:
            return match.group(0)

        return f":{color}[${expression}$]"

    return pattern.sub(replace_math, markdown_text)


def load_colored_md(filename: str) -> str:
    """Load Markdown and apply the LuKARS parameter color convention."""
    return color_parameter_markdown(
        load_md(
            MD_DIR,
            filename,
            LANGUAGE,
        )
    )




# -----------------------------------------------------------------------------
# Tutorial exercise files and standalone exercise view
# -----------------------------------------------------------------------------
TUTORIAL_EXERCISES = {
    "1": {
        "tab": "1 · Slow pathway",
        "file": "md_baget_tutorial_01.md",
    },
    "2": {
        "tab": "2 · Fast pathway",
        "file": "md_baget_tutorial_02.md",
    },
    "3": {
        "tab": "3 · Matrix-conduit",
        "file": "md_baget_tutorial_03.md",
    },
    "4": {
        "tab": "4 · Spring release",
        "file": "md_baget_tutorial_04.md",
    },
    "5": {
        "tab": "5 · Conduit loss",
        "file": "md_baget_tutorial_05.md",
    },
}


def _render_tutorial_markdown(markdown_text: str) -> None:
    """Render tutorial Markdown and $$...$$ display equations."""
    parts = re.split(
        r"(\$\$.*?\$\$)",
        markdown_text,
        flags=re.DOTALL,
    )

    for part in parts:
        if not part or not part.strip():
            continue

        stripped = part.strip()

        if (
            stripped.startswith("$$")
            and stripped.endswith("$$")
        ):
            st.latex(
                stripped[2:-2].strip()
            )
        else:
            st.markdown(
                color_parameter_markdown(part)
            )


def render_tutorial_exercise_file(
    filename: Path,
) -> None:
    """Render one tutorial exercise with collapsed answer expanders.

    Answer blocks in the Markdown files use this syntax:

        :::answer Answer to question 1
        Answer text...
        :::endanswer

    The same renderer is used in the Tutorial tab and in the standalone
    exercise view, so answers remain hidden in both places until opened.
    """
    exercise_text = filename.read_text(
        encoding="utf-8"
    )

    answer_pattern = re.compile(
        r":::answer(?:[ \t]+([^\n]+))?\n(.*?)\n:::endanswer",
        flags=re.DOTALL,
    )

    position = 0

    for match in answer_pattern.finditer(
        exercise_text
    ):
        # Render everything before the answer block normally.
        _render_tutorial_markdown(
            exercise_text[
                position:match.start()
            ]
        )

        title = (
            match.group(1)
            or "Show answer"
        ).strip()

        answer_text = (
            match.group(2)
            or ""
        ).strip()

        # Keep answers closed by default.
        with st.expander(
            f"💡 {title}",
            expanded=False,
        ):
            _render_tutorial_markdown(
                answer_text
            )

        position = match.end()

    # Render the remaining tutorial text after the last answer.
    _render_tutorial_markdown(
        exercise_text[position:]
    )


def tutorial_exercise_url(
    exercise_key: str,
) -> str:
    """Build a URL that opens one tutorial exercise in a new browser tab."""
    return (
        "./?tutorial_exercise="
        f"{exercise_key}"
    )


def render_tutorial_popout_button(
    exercise_key: str,
) -> None:
    """Render the standalone-exercise link at the bottom of an exercise."""
    spacer, button_column = st.columns(
        [4.2, 1.8]
    )

    with button_column:
        st.link_button(
            "↗ Open exercise separately",
            tutorial_exercise_url(
                exercise_key
            ),
            use_container_width=True,
            help=(
                "Open this exercise in a separate browser tab so it can be "
                "placed next to a live graph while you work."
            ),
        )


def render_baget_tutorial_companion() -> bool:
    """Render one tutorial exercise as a lightweight standalone page."""
    if not hasattr(
        st,
        "query_params",
    ):
        return False

    exercise_key = st.query_params.get(
        "tutorial_exercise",
        "",
    )

    if exercise_key not in TUTORIAL_EXERCISES:
        return False

    exercise = TUTORIAL_EXERCISES[
        exercise_key
    ]

    # A compact reading layout works well when the browser window is tiled
    # next to a live Plotly graph.
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 820px !important;
            padding-top: 3.5rem !important;
            padding-left: 1.4rem !important;
            padding-right: 1.4rem !important;
            padding-bottom: 2.0rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "Baget guided parameter investigation · "
        "Standalone exercise view"
    )

    render_tutorial_exercise_file(
        MD_DIR / exercise["file"]
    )

    return True


# If app.py routed this browser tab here as a tutorial exercise, render only
# the exercise and stop before loading the model, data, controls, or plots.
if render_baget_tutorial_companion():
    st.stop()


# -----------------------------------------------------------------------------
# Live companion plots
# -----------------------------------------------------------------------------
LIVE_PLOT_LABELS = {
    "discharge": "Observed and simulated discharge",
    "fluxes": "Internal model fluxes",
    "storages": "Internal model storages",
}


@st.cache_resource
def get_baget_live_plot_store():
    """Return a thread-safe store shared by Streamlit sessions."""
    return {
        "lock": threading.RLock(),
        "plots": {},
    }


def get_baget_live_id() -> str:
    """Return the identifier used by this Baget browser session."""
    if "baget_live_id" not in st.session_state:
        st.session_state.baget_live_id = uuid.uuid4().hex

    return st.session_state.baget_live_id


def publish_live_plot(
    plot_key: str,
    figure: go.Figure,
) -> None:
    """Publish the latest figure for the companion browser tab."""
    if plot_key not in LIVE_PLOT_LABELS:
        return

    live_id = get_baget_live_id()
    store = get_baget_live_plot_store()
    now = time.time()

    with store["lock"]:
        # Remove abandoned live sessions after six hours.
        cutoff = now - 6 * 60 * 60

        stale_keys = [
            key
            for key, snapshot in store["plots"].items()
            if snapshot.get("updated", 0.0) < cutoff
        ]

        for key in stale_keys:
            del store["plots"][key]

        store["plots"][(live_id, plot_key)] = {
            "figure_json": figure.to_json(),
            "updated": now,
        }


def read_live_plot(
    live_id: str,
    plot_key: str,
):
    """Read the most recent published live plot."""
    store = get_baget_live_plot_store()

    with store["lock"]:
        snapshot = store["plots"].get(
            (live_id, plot_key)
        )

        return (
            None
            if snapshot is None
            else dict(snapshot)
        )


def live_plot_url(
    plot_key: str,
) -> str:
    """Build the URL for the live companion tab."""
    live_id = get_baget_live_id()

    return (
        "./?live_plot="
        f"{plot_key}&live_id={live_id}"
    )


def render_live_plot_button(
    plot_key: str,
) -> None:
    """Show the Open live plot button aligned to the right."""
    _, button_column = st.columns(
        [4.0, 1.25]
    )

    with button_column:
        st.link_button(
            "↗ Open live plot",
            live_plot_url(plot_key),
            use_container_width=True,
            help=(
                "Open this graph in a separate browser tab. "
                "Keep the Baget page open and change parameters there; "
                "the companion graph updates automatically."
            ),
        )


def render_baget_live_companion() -> bool:
    """Render only the requested graph in a companion browser tab."""
    if not hasattr(
        st,
        "query_params",
    ):
        return False

    plot_key = st.query_params.get(
        "live_plot",
        "",
    )

    live_id = st.query_params.get(
        "live_id",
        "",
    )

    if (
        plot_key not in LIVE_PLOT_LABELS
        or not live_id
    ):
        return False

    # Use almost the complete browser width in the companion view.
    # The larger top padding prevents Streamlit's top bar from cutting
    # the companion-view heading.
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 100% !important;
            padding-top: 3.5rem !important;
            padding-left: 1.4rem !important;
            padding-right: 1.4rem !important;
            padding-bottom: 1.0rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.subheader(
        f":blue[{LIVE_PLOT_LABELS[plot_key]}]",
        divider="blue",
    )

    st.caption(
        "Live companion view · Keep the original Baget page open. "
        "This graph refreshes automatically when the model parameters change."
    )

    if not hasattr(
        st,
        "fragment",
    ):
        st.error(
            "The live companion view requires a Streamlit version "
            "that supports st.fragment."
        )
        return True

    @st.fragment(
        run_every="1s"
    )
    def live_plot_fragment():
        snapshot = read_live_plot(
            live_id,
            plot_key,
        )

        if snapshot is None:
            st.info(
                "Waiting for the graph from the original Baget page. "
                "Keep that page open and change any parameter once."
            )
            return

        try:
            live_figure = go.Figure(
                json.loads(
                    snapshot["figure_json"]
                )
            )
        except Exception as exc:
            st.error(
                "The companion graph could not be reconstructed."
            )
            st.exception(exc)
            return

        # Preserve zoom, pan and legend selections while results refresh.
        live_figure.update_layout(
            height=700,
            uirevision=(
                f"baget-live-{live_id}-{plot_key}"
            ),
        )

        plot_config = {
            "displaylogo": False,
            "scrollZoom": True,
        }

        if plot_key == "discharge":
            plot_config["modeBarButtonsToAdd"] = [
                "drawline",
                "eraseshape",
            ]

        st.plotly_chart(
            live_figure,
            use_container_width=True,
            key=f"baget_live_chart_{plot_key}",
            config=plot_config,
        )

        st.caption(
            "Automatic refresh: approximately every 1 second."
        )

    live_plot_fragment()
    return True


# If app.py routed this browser tab here as a live companion,
# show only the requested graph and stop the rest of Baget.py.
if render_baget_live_companion():
    st.stop()


# -----------------------------------------------------------------------------
# Manuscript simulation periods
# -----------------------------------------------------------------------------
# The manuscript reports calibration for 01/03/2022-29/03/2022 and
# validation for 30/03/2022-30/04/2022. The model is still run from the
# beginning of the available input series so that all preceding forcing data
# act as warm-up and initialize the internal storages before calibration.
CALIBRATION_START = pd.Timestamp("2022-03-01 00:00")
CALIBRATION_END = pd.Timestamp("2022-03-29 23:00")
VALIDATION_START = pd.Timestamp("2022-03-30 00:00")
VALIDATION_END = pd.Timestamp("2022-04-30 23:00")
DISPLAY_START = CALIBRATION_START
DISPLAY_END = VALIDATION_END


# -----------------------------------------------------------------------------
# Default Baget parameter set
# -----------------------------------------------------------------------------
BAGET_PRESET = {
    "dt": 1.0,
    "TotalArea": 13e6,
    "areas_frac": [0.7, 0.3],
    "kis": [8.11e-5, 0.0],
    "Emin": [10.2, 4.8],
    "Emax": [142.0, 23.5],
    "alpha": [1.98, 1.47],
    "khy": [2730.0, 475.0],
    "lhy": [3170.0, 1580.0],
    "kMC": 2.06e-2,
    "aMC": 2.90,
    "C_loss": 2.0,
    "M_loss": 1e8,
    "kMS": 0.0,
    "aMS": 1.0,
    "kCS": 7.74e-3,
    "aCS": 3.85,
    "E0": 1.0,
    "Qis0": 1.0,
    "Qhy0": 0.0,
    "M0": 1.0,
    "C0": 0.5,
}


# -----------------------------------------------------------------------------
# Load the LuKARS model from assets/lukars_model.py
# -----------------------------------------------------------------------------
@st.cache_resource
def load_lukars_functions(model_path: str):
    """Load run_model and metrics from the LuKARS model file."""
    path = Path(model_path)

    if not path.exists():
        raise FileNotFoundError(
            f"LuKARS model file not found: {path}"
        )

    module_spec = importlib.util.spec_from_file_location(
        "lukars_model_from_assets",
        path,
    )

    if module_spec is None or module_spec.loader is None:
        raise ImportError(
            f"The model module could not be created from: {path}"
        )

    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)

    if not hasattr(module, "run_model"):
        raise AttributeError(
            "The model file does not define a function named 'run_model'."
        )

    if not hasattr(module, "metrics"):
        raise AttributeError(
            "The model file does not define a function named 'metrics'."
        )

    return module.run_model, module.metrics


# -----------------------------------------------------------------------------
# Data utilities
# -----------------------------------------------------------------------------
def _read_table(path: Path) -> pd.DataFrame:
    """Read a tab-, comma-, or semicolon-separated text table."""
    errors = []

    for separator in ("\t", ",", ";"):
        try:
            frame = pd.read_csv(
                path,
                sep=separator,
                encoding="utf-8-sig",
            )

            if len(frame.columns) >= 2:
                return frame
        except Exception as exc:
            errors.append(str(exc))

    raise ValueError(
        "The Baget input file could not be read as a tab-, comma-, or "
        "semicolon-separated table. "
        + (" | ".join(errors[-2:]) if errors else "")
    )


def clean_input_frame(
    frame: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """Validate and standardize a LuKARS input table."""
    frame = frame.copy()
    frame.columns = [
        str(column).strip()
        for column in frame.columns
    ]

    possible_date_names = {
        "date",
        "datetime",
        "time",
        "timestamp",
    }

    date_column = next(
        (
            column
            for column in frame.columns
            if column.lower() in possible_date_names
        ),
        frame.columns[0],
    )

    frame[date_column] = pd.to_datetime(
        frame[date_column],
        dayfirst=True,
        errors="coerce",
        format="mixed",
    )

    invalid_dates = int(
        frame[date_column].isna().sum()
    )

    frame = (
        frame
        .dropna(subset=[date_column])
        .set_index(date_column)
        .sort_index()
    )

    if frame.index.has_duplicates:
        duplicate_count = int(
            frame.index.duplicated().sum()
        )
        raise ValueError(
            f"The input contains {duplicate_count} duplicated timestamp(s)."
        )

    if "P" not in frame.columns:
        raise ValueError(
            "The Baget input file must contain a column named 'P'."
        )

    if "QobsS" not in frame.columns:
        frame["QobsS"] = np.nan

    frame["P"] = pd.to_numeric(
        frame["P"],
        errors="coerce",
    )

    frame["QobsS"] = pd.to_numeric(
        frame["QobsS"],
        errors="coerce",
    )

    missing_precipitation = int(
        frame["P"].isna().sum()
    )
    frame["P"] = frame["P"].fillna(0.0)

    frame = frame[["P", "QobsS"]]

    if len(frame) < 2:
        raise ValueError(
            "At least two valid time steps are required."
        )

    differences = (
        frame.index
        .to_series()
        .diff()
        .dropna()
    )

    median_step = differences.median()
    irregular_steps = int(
        (differences != median_step).sum()
    )

    valid_observations = int(
        frame["QobsS"].notna().sum()
    )
    total_steps = len(frame)

    info = {
        "rows": total_steps,
        "valid_observations": valid_observations,
        "observation_coverage": (
            100.0 * valid_observations / total_steps
            if total_steps
            else 0.0
        ),
        "time_step": str(median_step),
        "irregular_steps": irregular_steps,
        "invalid_dates": invalid_dates,
        "missing_precipitation": missing_precipitation,
    }

    return frame, info


@st.cache_data
def load_baget_data(
    data_path: str,
) -> tuple[pd.DataFrame, dict]:
    """Load and validate assets/input_Baget.txt."""
    path = Path(data_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Baget input file not found: {path}"
        )

    frame = _read_table(path)
    return clean_input_frame(frame)


# -----------------------------------------------------------------------------
# Interface helpers
# -----------------------------------------------------------------------------
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
    """Create a floating-point slider with a clipped default value."""
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
    n_steps: int = 201,
    allow_zero: bool = False,
    help_text: str | None = None,
) -> float:
    """Create a logarithmically spaced slider that displays actual values."""

    if lower <= 0.0:
        raise ValueError(
            "The positive lower bound of a logarithmic slider must be > 0."
        )

    if upper <= lower:
        raise ValueError(
            "The upper bound of a logarithmic slider must exceed the lower bound."
        )

    default_value = float(value)

    # Preserve an existing value when switching from a former linear slider
    # to the logarithmic version during an active Streamlit session.
    current_value = float(
        st.session_state.get(
            key,
            default_value,
        )
    )

    # Zero is kept as a separate physical option for parameters such as kis.
    if allow_zero and np.isclose(current_value, 0.0):
        current_value = 0.0
    else:
        current_value = float(
            np.clip(
                current_value,
                lower,
                upper,
            )
        )

    # Generate evenly spaced positions in log10 space, but use the actual
    # parameter values as the selectable options.
    options = [
        float(item)
        for item in np.geomspace(
            lower,
            upper,
            n_steps,
        )
    ]

    # Include the exact Baget preset and the current session value so that
    # reset and hot-reload keep the precise parameter values.
    if default_value > 0.0:
        options.append(
            float(
                np.clip(
                    default_value,
                    lower,
                    upper,
                )
            )
        )

    if current_value > 0.0:
        options.append(current_value)

    if allow_zero:
        options.append(0.0)

    options = sorted(
        set(options)
    )

    # Set the widget state explicitly. This also makes the reset callback
    # compatible with the logarithmic sliders because the session state stores
    # the real parameter value, not its logarithm.
    st.session_state[key] = current_value

    default_help = (
        "This parameter is varied on a logarithmic scale. "
        "The displayed number is the actual parameter value."
    )

    selected_value = st.select_slider(
        label,
        options=options,
        key=key,
        format_func=lambda x: (
            "0"
            if np.isclose(float(x), 0.0)
            else f"{float(x):.4g}"
        ),
        help=(
            help_text
            if help_text is not None
            else default_help
        ),
    )

    return float(selected_value)


def persistent_series_selector(
    label: str,
    options: list[str],
    default_selected: list[str],
    key: str,
    help_text: str | None = None,
) -> list[str]:
    """Select visible plot series and preserve the choice across reruns."""

    valid_options = list(options)

    if key not in st.session_state:
        st.session_state[key] = [
            item
            for item in default_selected
            if item in valid_options
        ]
    else:
        st.session_state[key] = [
            item
            for item in st.session_state[key]
            if item in valid_options
        ]

    return st.multiselect(
        label,
        options=valid_options,
        key=key,
        help=help_text,
    )


def score_text(
    value: float,
    digits: int = 3,
) -> str:
    """Format a performance metric while handling NaN values."""
    return (
        "not available"
        if not np.isfinite(value)
        else f"{value:.{digits}f}"
    )


def axis_limit_controls(
    key_prefix: str,
    index: pd.DatetimeIndex,
    values: list,
) -> dict:
    """Create optional x- and y-axis controls."""
    with st.expander("Adjust plot limits"):
        x_col1, x_col2 = st.columns(2)

        with x_col1:
            use_x_limits = st.checkbox(
                "Fix x-axis",
                value=False,
                key=f"{key_prefix}_use_x",
            )

            start_date = st.date_input(
                "Start date",
                value=index.min().date(),
                min_value=index.min().date(),
                max_value=index.max().date(),
                key=f"{key_prefix}_x_start",
                disabled=not use_x_limits,
            )

            end_date = st.date_input(
                "End date",
                value=index.max().date(),
                min_value=index.min().date(),
                max_value=index.max().date(),
                key=f"{key_prefix}_x_end",
                disabled=not use_x_limits,
            )

        finite_arrays = []

        for value in values:
            array = np.asarray(
                value,
                dtype=float,
            )
            finite = array[np.isfinite(array)]

            if len(finite):
                finite_arrays.append(finite)

        combined = (
            np.concatenate(finite_arrays)
            if finite_arrays
            else np.array([0.0, 1.0])
        )

        default_y_min = float(
            np.nanmin(combined)
        )
        default_y_max = float(
            np.nanmax(combined)
        )

        if np.isclose(
            default_y_min,
            default_y_max,
        ):
            default_y_max = default_y_min + 1.0

        with x_col2:
            use_y_limits = st.checkbox(
                "Fix y-axis",
                value=False,
                key=f"{key_prefix}_use_y",
            )

            y_min = st.number_input(
                "Y minimum",
                value=default_y_min,
                key=f"{key_prefix}_y_min",
                disabled=not use_y_limits,
            )

            y_max = st.number_input(
                "Y maximum",
                value=default_y_max,
                key=f"{key_prefix}_y_max",
                disabled=not use_y_limits,
            )

    result = {}

    if use_x_limits:
        result["x_range"] = [
            pd.Timestamp(start_date),
            pd.Timestamp(end_date)
            + pd.Timedelta(days=1),
        ]

    if use_y_limits and y_max > y_min:
        result["y_range"] = [
            y_min,
            y_max,
        ]

    return result


def apply_axis_limits(
    figure: go.Figure,
    limits: dict,
) -> None:
    """Apply optional axis limits to a Plotly figure."""
    if "x_range" in limits:
        figure.update_xaxes(
            range=limits["x_range"]
        )

    if "y_range" in limits:
        figure.update_yaxes(
            range=limits["y_range"]
        )


def render_assessment(
    filename: Path,
) -> None:
    """Render the Baget assessment in two-column rows."""
    with filename.open(
        "r",
        encoding="utf-8",
    ) as file:
        questions = json.load(file)

    for start_index in range(
        0,
        len(questions),
        2,
    ):
        columns = st.columns(2)

        for column, question_data in zip(
            columns,
            questions[
                start_index : start_index + 2
            ],
        ):
            with column:
                multiple_choice(
                    question=question_data["question"],
                    options_dict=question_data["options"],
                    success=question_data.get(
                        "success",
                        "Correct.",
                    ),
                    error=question_data.get(
                        "error",
                        "Not quite.",
                    ),
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
    
    
def reset_baget_parameters() -> None:
    """Reset all Baget parameter widgets to the predefined Baget values."""

    # Remove all hydrotope-specific parameter states first. This also clears
    # parameters belonging to hydrotopes 3 and 4 if the user created them.
    for state_key in list(st.session_state):
        if state_key.startswith("baget_par_"):
            del st.session_state[state_key]

    # Restore the top-level controls.
    st.session_state["baget_n_hydrotopes"] = 2
    st.session_state["baget_total_area"] = (
        BAGET_PRESET["TotalArea"] / 1e6
    )

    # Restore the two predefined Baget hydrotopes.
    for index in range(2):
        st.session_state[f"baget_par_frac_{index}"] = (
            BAGET_PRESET["areas_frac"][index]
        )
        st.session_state[f"baget_par_kis_{index}"] = (
            BAGET_PRESET["kis"][index]
        )
        st.session_state[f"baget_par_emin_{index}"] = (
            BAGET_PRESET["Emin"][index]
        )
        st.session_state[f"baget_par_emax_{index}"] = (
            BAGET_PRESET["Emax"][index]
        )
        st.session_state[f"baget_par_alpha_{index}"] = (
            BAGET_PRESET["alpha"][index]
        )
        st.session_state[f"baget_par_khy_{index}"] = (
            BAGET_PRESET["khy"][index]
        )
        st.session_state[f"baget_par_lhy_{index}"] = (
            BAGET_PRESET["lhy"][index]
        )

    # Restore matrix and conduit parameters.
    st.session_state["baget_par_kMC"] = BAGET_PRESET["kMC"]
    st.session_state["baget_par_aMC"] = BAGET_PRESET["aMC"]
    st.session_state["baget_par_kCS"] = BAGET_PRESET["kCS"]
    st.session_state["baget_par_aCS"] = BAGET_PRESET["aCS"]
    st.session_state["baget_par_kMS"] = BAGET_PRESET["kMS"]
    st.session_state["baget_par_C_loss"] = BAGET_PRESET["C_loss"]


# -----------------------------------------------------------------------------
# Load required model and data
# -----------------------------------------------------------------------------
try:
    run_model, metrics = load_lukars_functions(
        str(ASSETS_DIR / "lukars_model.py")
    )
except Exception as exc:
    st.error(
        "The LuKARS model could not be loaded from "
        f"`{ASSETS_DIR / "lukars_model.py"}`."
    )
    st.exception(exc)
    st.stop()

try:
    data, data_info = load_baget_data(
        str(ASSETS_DIR / "input_Baget.txt")
    )
except Exception as exc:
    st.error(
        "The predefined Baget dataset could not be loaded from "
        f"`{ASSETS_DIR / "input_Baget.txt"}`."
    )
    st.exception(exc)
    st.stop()

if data.index.min() > CALIBRATION_START or data.index.max() < VALIDATION_END:
    st.error(
        "The predefined Baget dataset does not fully cover the manuscript "
        "calibration and validation periods."
    )
    st.stop()

# Only data through the end of validation are passed to LuKARS. Data after
# 30/04/2022 are intentionally not part of this teaching experiment.
model_data = data.loc[:VALIDATION_END].copy()

warmup_index = model_data.index[model_data.index < CALIBRATION_START]
if len(warmup_index) == 0:
    st.error(
        "The predefined Baget dataset contains no forcing data before the "
        "calibration period, so a warm-up cannot be performed."
    )
    st.stop()

WARMUP_START = model_data.index.min()
WARMUP_END = warmup_index.max()

display_mask = (
    (model_data.index >= DISPLAY_START)
    & (model_data.index <= DISPLAY_END)
)
calibration_mask = (
    (model_data.index >= CALIBRATION_START)
    & (model_data.index <= CALIBRATION_END)
)
validation_mask = (
    (model_data.index >= VALIDATION_START)
    & (model_data.index <= VALIDATION_END)
)

display_data = model_data.loc[display_mask]


# -----------------------------------------------------------------------------
# Page title
# -----------------------------------------------------------------------------
title_col1, title_col2 = st.columns(
    [0.10, 0.90],
    vertical_alignment="center",
)

with title_col1:
    st.image(str(IMAGE_DIR/"flag_france.png"),
            width=60,
        )


with title_col2:
    st.markdown(
        load_colored_md("md_baget_01.md")
    )


# -----------------------------------------------------------------------------
# Case-study introduction
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[Case-study purpose]",
    divider="blue",
)

st.markdown(
    load_colored_md("md_baget_02.md")
)

# -----------------------------------------------------------------------------
# Data summary
# -----------------------------------------------------------------------------
# with st.expander(
    # "📁 Case-study data",
    # expanded=True,
# ):
    # st.markdown(
        # load_md(
            # MD_DIR,
            # "md_baget_03.md",
            # LANGUAGE,
        # )
    # )

    # data_col1, data_col2, data_col3, data_col4 = st.columns(
        # 4
    # )

    # data_col1.metric(
        # "Source",
        # DATA_FILE.name,
    # )
    # data_col2.metric(
        # "Time steps",
        # f"{data_info['rows']:,}",
    # )
    # data_col3.metric(
        # "Nominal time step",
        # data_info["time_step"],
    # )
    # data_col4.metric(
        # "Observed coverage",
        # f"{data_info['observation_coverage']:.1f}%",
    # )

    # if data_info["invalid_dates"]:
        # st.warning(
            # f"{data_info['invalid_dates']} row(s) with invalid dates "
            # "were removed."
        # )

    # if data_info["missing_precipitation"]:
        # st.warning(
            # f"{data_info['missing_precipitation']} missing precipitation "
            # "value(s) were replaced by zero."
        # )

    # if data_info["irregular_steps"]:
        # st.warning(
            # f"{data_info['irregular_steps']} time interval(s) differ "
            # "from the median time step."
        # )

# -----------------------------------------------------------------------------
# Study area
# -----------------------------------------------------------------------------
st.subheader(
    "🗺️ :blue[Study area]",
    divider="blue",
)

study_col1, study_col2 = st.columns(
    [1.1, 1.4],
    gap="large",
    vertical_alignment="center",
)

with study_col1:
    st.markdown(
        load_colored_md("md_baget_study_area.md")
    )

with study_col2:
    st.image(
        IMAGE_DIR/"baget_study_area.png",
        caption=(
            "Baget catchment, main geological formations, "
            "Las Hountas spring and Lachein stream."
        ),
        use_container_width=True,
    )
    

# -----------------------------------------------------------------------------
# Simulation periods
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[Simulation periods]",
    divider="blue",
)

period_col1, period_col2, period_col3 = st.columns(3)

with period_col1:
    st.markdown(
        f"**Warm-up**  \n"
        f"{WARMUP_START:%d/%m/%Y} - {WARMUP_END:%d/%m/%Y}  \n"
        "All available forcing data before calibration are used to initialize "
        "model states; no performance metrics are computed for this period."
    )

with period_col2:
    st.markdown(
        f"**Calibration**  \n"
        f"{CALIBRATION_START:%d/%m/%Y} - "
        f"{CALIBRATION_END:%d/%m/%Y}  \n"
        "Performance metrics are computed only from observations in this "
        "period."
    )

with period_col3:
    st.markdown(
        f"**Performance test**  \n"
        f"{VALIDATION_START:%d/%m/%Y} - "
        f"{VALIDATION_END:%d/%m/%Y}  \n"
        "Performance metrics are computed independently from the calibration "
        "period."
    )

st.info(
        "**Hourly time discretization**"
    )
    
# -----------------------------------------------------------------------------
# What can be inspected in the app?
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[What can be inspected in the app?]",
    divider="blue",
)

st.markdown(
    load_colored_md("md_lukars_model_18.md")
)


# -----------------------------------------------------------------------------    
@st.fragment
def render_baget_interactive_section() -> None:
    # -----------------------------------------------------------------------------
    # Manual-calibration controls
    # -----------------------------------------------------------------------------
    st.subheader(
        ":blue[Manual-calibration parameters]",
        divider="blue",
    )

    col1, col2, col3 = st.columns([0.4, 4.2, 0.4]) # Model cocncept for Baget
    with col2:
        st.image(
            IMAGE_DIR/"LuKARS_baget.png",
            caption="Conceptual structure of LuKARS for the case study of Baget.",
            use_container_width=True,
        )

    st.markdown(
        """
**Parameter colors:** :blue[kis] ·
:red[Emin, Emax, alpha, khyd, lhyd] ·
:violet[kMC, aMC] ·
:orange[kMS, aMS, kCS, aCS] ·
$\\color{#4AA3FF}{C_{\\mathrm{loss}}}$
"""
    )

    st.markdown(
        load_colored_md("md_baget_04.md")
    )

    with st.expander(
        "Show and modify model parameters",
        expanded=True,
    ):
        top_controls = st.columns(
            [1, 1, 1]
        )

        with top_controls[0]:
            n_hydrotopes = st.number_input(
                "Number of hydrotopes",
                min_value=1,
                max_value=4,
                value=2,
                step=1,
                key="baget_n_hydrotopes",
            )

        with top_controls[1]:
            total_area_km2 = st.number_input(
                "Catchment area (km2)",
                min_value=9.0,
                max_value=15.0,
                value=15.0,
                step=0.5,
                key="baget_total_area",
            )

        with top_controls[2]:
            st.button(
                "Reset Baget parameters",
                use_container_width=True,
                on_click=reset_baget_parameters,
            )

        hydrotope_tabs = st.tabs(
            [
                f"Hydrotope {index + 1}"
                for index in range(n_hydrotopes)
            ]
        )

        fractions = []
        kis = []
        emin = []
        emax = []
        alpha = []
        khy = []
        lhy = []

        default_fractions = (
            BAGET_PRESET["areas_frac"]
            + [1 / n_hydrotopes] * n_hydrotopes
        )[:n_hydrotopes]

        # Common parameter ranges for every hydrotope.
        # They span the full set of values reported for HYD1 and HYD2 in
        # Table 2 of the Baget manuscript. Parameters spanning several orders
        # of magnitude (kis and khyd) are controlled logarithmically below.
        # For kis, zero remains available as a separate physical option so that
        # the Baget HYD2 preset (no matrix infiltration) can still be selected.
        # The area fraction remains an additional app parameter (0-1).
        hydro_ranges = {
            "kis": (0.0, 1e-3, 1e-7),
            "Emin": (1.0, 150.0, 0.5),
            "Emax": (6.0, 200.0, 1.0),
            "alpha": (1.0, 3.0, 0.01),
            "khy": (1.0, 10000.0, 1.0),
            "lhy": (1000.0, 6500.0, 10.0),
        }

        for index, hydrotope_tab in enumerate(
            hydrotope_tabs
        ):

            with hydrotope_tab:
                hydro_col1, hydro_col2 = st.columns(
                    2,
                    gap="large",
                )

                with hydro_col1:
                    fractions.append(
                        float_slider(
                            "Area fraction",
                            default_fractions[index],
                            0.0,
                            1.0,
                            0.01,
                            f"baget_par_frac_{index}",
                        )
                    )

                    kis.append(
                        log_slider(
                            ":blue[kis] (1/h)",
                            (
                                BAGET_PRESET["kis"]
                                + [1e-5] * n_hydrotopes
                            )[index],
                            1e-7,
                            1e-3,
                            f"baget_par_kis_{index}",
                            allow_zero=True,
                        )
                    )

                    emin.append(
                        float_slider(
                            ":red[Emin] (mm)",
                            (
                                BAGET_PRESET["Emin"]
                                + [10.0] * n_hydrotopes
                            )[index],
                            hydro_ranges["Emin"][0],
                            hydro_ranges["Emin"][1],
                            hydro_ranges["Emin"][2],
                            f"baget_par_emin_{index}",
                        )
                    )

                    emax.append(
                        float_slider(
                            ":red[Emax] (mm)",
                            (
                                BAGET_PRESET["Emax"]
                                + [100.0] * n_hydrotopes
                            )[index],
                            hydro_ranges["Emax"][0],
                            hydro_ranges["Emax"][1],
                            hydro_ranges["Emax"][2],
                            f"baget_par_emax_{index}",
                        )
                    )

                with hydro_col2:
                    alpha.append(
                        float_slider(
                            ":red[alpha] (-)",
                            (
                                BAGET_PRESET["alpha"]
                                + [1.5] * n_hydrotopes
                            )[index],
                            hydro_ranges["alpha"][0],
                            hydro_ranges["alpha"][1],
                            hydro_ranges["alpha"][2],
                            f"baget_par_alpha_{index}",
                        )
                    )

                    khy.append(
                        log_slider(
                            ":red[khyd] (m2/h)",
                            (
                                BAGET_PRESET["khy"]
                                + [500.0] * n_hydrotopes
                            )[index],
                            1.0,
                            10000.0,
                            f"baget_par_khy_{index}",
                        )
                    )

                    lhy.append(
                        float_slider(
                            ":red[lhyd] (m)",
                            (
                                BAGET_PRESET["lhy"]
                                + [2000.0] * n_hydrotopes
                            )[index],
                            hydro_ranges["lhy"][0],
                            hydro_ranges["lhy"][1],
                            hydro_ranges["lhy"][2],
                            f"baget_par_lhy_{index}",
                        )
                    )

        st.markdown("#### Matrix and conduit parameters")

        lower_col1, lower_col2, lower_col3 = st.columns(
            3,
            gap="large",
        )

        with lower_col1:
            kmc = log_slider(
                ":violet[kMC]",
                BAGET_PRESET["kMC"],
                1e-5,
                1e-1,
                "baget_par_kMC",
            )

            amc = float_slider(
                ":violet[aMC]",
                BAGET_PRESET["aMC"],
                1.0,
                3.0,
                0.05,
                "baget_par_aMC",
            )

        with lower_col2:
            kcs = log_slider(
                ":orange[kCS]",
                BAGET_PRESET["kCS"],
                1e-3,
                1e1,
                "baget_par_kCS",
            )

            acs = float_slider(
                ":orange[aCS]",
                BAGET_PRESET["aCS"],
                1.0,
                4.0,
                0.05,
                "baget_par_aCS",
            )

        with lower_col3:
            kms = float_slider(
                ":orange[kMS]",
                BAGET_PRESET["kMS"],
                0.0,
                0.1,
                0.0005,
                "baget_par_kMS",
                "%.4f",
            )

            # aMS is fixed to 1.0 for the Baget case study.
            # Streamlit sliders require min_value < max_value, so a fixed
            # parameter should not be represented by a slider.
            ams = float(BAGET_PRESET["aMS"])
            st.caption(f":orange[aMS] = {ams:.1f} (fixed)")

            c_loss = log_slider(
                r"$\color{#4AA3FF}{C_{\mathrm{loss}}}$ — Conduit loss threshold",
                BAGET_PRESET["C_loss"],
                1e-2,
                100.0,
                "baget_par_C_loss",
            )


    # -----------------------------------------------------------------------------
    # Validate parameters and run LuKARS
    # -----------------------------------------------------------------------------
    fractions_array = np.asarray(
        fractions,
        dtype=float,
    )

    if fractions_array.sum() <= 0:
        st.error(
            "At least one hydrotope area fraction must exceed zero."
        )
        st.stop()

    fractions_array = (
        fractions_array
        / fractions_array.sum()
    )

    if np.any(
        np.asarray(emax)
        <= np.asarray(emin)
    ):
        st.error(
            "Emax must be larger than Emin for every hydrotope."
        )
        st.stop()

    params = deepcopy(
        BAGET_PRESET
    )

    params.update(
        {
            "TotalArea": total_area_km2 * 1e6,
            "areas_frac": fractions_array,
            "areas": (
                fractions_array
                * total_area_km2
                * 1e6
            ),
            "kis": np.asarray(kis),
            "Emin": np.asarray(emin),
            "Emax": np.asarray(emax),
            "alpha": np.asarray(alpha),
            "khy": np.asarray(khy),
            "lhy": np.asarray(lhy),
            "kMC": kmc,
            "aMC": amc,
            "kCS": kcs,
            "aCS": acs,
            "kMS": kms,
            "aMS": ams,
            "C_loss": c_loss,
        }
    )

    with st.spinner(
        "Running LuKARS. The first run may take a few seconds."
    ):
        run_up, run_bot = run_model(
            model_data["P"].to_numpy(
                dtype=float
            ),
            params,
        )

    qsim = np.asarray(
        run_bot[7],
        dtype=float,
    )

    observed = model_data["QobsS"].to_numpy(
        dtype=float
    )

    # Performance metrics are computed independently for the manuscript
    # calibration and validation periods. Warm-up observations are never used in
    # the objective metrics.
    score_calibration = metrics(
        observed[calibration_mask],
        qsim[calibration_mask],
    )

    score_validation = metrics(
        observed[validation_mask],
        qsim[validation_mask],
    )

    calibration_valid_mask = (
        calibration_mask
        & np.isfinite(observed)
        & np.isfinite(qsim)
    )
    validation_valid_mask = (
        validation_mask
        & np.isfinite(observed)
        & np.isfinite(qsim)
    )

    n_valid_calibration = int(calibration_valid_mask.sum())
    n_valid_validation = int(validation_valid_mask.sum())

    # Convenience slices used by every plot so that only the calibration and
    # validation window is displayed.
    qsim_display = qsim[display_mask]
    run_bot_display = run_bot[:, display_mask]
    run_up_display = run_up[:, display_mask, :]


    # -----------------------------------------------------------------------------
    # Output tabs
    # -----------------------------------------------------------------------------
    (
        overview_tab,
        calibration_tab,
        flux_tab,
        storage_tab,
        tutorial_tab,
        questions_tab,
        results_tab,
    ) = st.tabs(
        [
            "📍 Overview",
            "🔧 Calibration",
            "🔄 Internal fluxes",
            "💧 Storages",
            "🎓 Tutorial",
            "❓ Questions",
            "📈 Results",
        ]
    )


    # -----------------------------------------------------------------------------
    # Overview tab
    # -----------------------------------------------------------------------------
    with overview_tab:
        st.subheader(
            ":blue[Observed time series]",
            divider="blue",
        )

        st.markdown(
            load_colored_md("md_baget_05.md")
        )

        precipitation_figure = make_subplots(
            specs=[[{"secondary_y": True}]]
        )

        # Observed spring discharge - right y-axis
        precipitation_figure.add_trace(
            go.Scatter(
                x=display_data.index,
                y=display_data["QobsS"],
                name="Observed spring discharge",
                mode="lines",
                #line_dash="dash",
                connectgaps=False,
                line=dict(
                    color="#0068C9",
                    width=2,
                ),
            ),
            secondary_y=True,
        )

        # Net precipitation - left y-axis
        precipitation_figure.add_trace(
            go.Bar(
                x=display_data.index,
                y=display_data["P"],
                name="Net precipitation",
                marker_color="#83C9FF",
            ),
            secondary_y=False,
        )

        # Calibration start
        precipitation_figure.add_vline(
            x=CALIBRATION_START,
            line_dash="dash",
            annotation_text="Calibration starts",
            annotation_position="top",
        )

        # Validation start
        precipitation_figure.add_vline(
            x=VALIDATION_START,
            line_dash="dash",
            annotation_text="Performance test starts",
            annotation_position="top",
        )

        precipitation_figure.update_layout(
            height=420,
            xaxis_title="Time",
            hovermode="x unified",
            margin={
                "l": 20,
                "r": 20,
                "t": 25,
                "b": 80,
            },
            legend={
                "orientation": "h",
                "xanchor": "center",
                "x": 0.5,
                "yanchor": "top",
                "y": -0.3,
            },

        )
    
        # Left y-axis
        precipitation_figure.update_yaxes(
            title_text="Net precipitation (mm)",
            secondary_y=False,
        )

        # Right y-axis
        precipitation_figure.update_yaxes(
            title_text="Observed spring discharge (m3/s)",
            secondary_y=True,
        )

        st.plotly_chart(
            precipitation_figure,
            use_container_width=True,
            config={
                "displaylogo": False,
                "scrollZoom": True,
            },
        )

        st.info(
            "The forcing time series consists of the net precipitation, meaning the precipitation time series already adjusted by including the relevant processes, which are for the Baget catchment evapotranspiration and interception."
        )


    # -----------------------------------------------------------------------------
    # Calibration tab
    # -----------------------------------------------------------------------------
    with calibration_tab:
        st.subheader(
            ":blue[Observed and simulated discharge]",
            divider="blue",
        )

        calibration_figure = go.Figure()

        calibration_figure.add_trace(
            go.Scatter(
                x=display_data.index,
                y=display_data["QobsS"],
                name="Observed",
                mode="lines",
                line=dict(
                    color="#0068C9",
                    width=2,
                ),
                connectgaps=False,
            )
        )

        calibration_figure.add_trace(
            go.Scatter(
                x=display_data.index,
                y=qsim_display,
                name="Simulated",
                mode="lines",
                line_dash="dash",
                line=dict(
                    color="#FF8C00",
                    width=2,
                ),
            )
        )
    
        calibration_figure.add_vline(
            x=CALIBRATION_START,
            line_dash="dash",
            annotation_text="calibration starts",
            annotation_position="top",
        )

        calibration_figure.add_vline(
            x=VALIDATION_START,
            line_dash="dash",
            annotation_text="Performance test starts",
            annotation_position="top",
        )

        calibration_figure.update_layout(
            height=520,
            xaxis_title="Time",
            yaxis_title="Discharge (m3/s)",
            hovermode="x unified",
            margin={
                "l": 20,
                "r": 20,
                "t": 25,
                "b": 80,
            },
                legend={
                "orientation": "h",
                "xanchor": "center",
                "x": 0.5,
                "yanchor": "top",
                "y": -0.18,
            },

        )

        # calibration_limits = axis_limit_controls(
            # "baget_calibration",
            # display_data.index,
            # [
                # display_data["QobsS"],
                # qsim_display,
            # ],
        # )

        # apply_axis_limits(
            # calibration_figure,
            # calibration_limits,
        # )

        publish_live_plot(
            "discharge",
            calibration_figure,
        )

        st.plotly_chart(
            calibration_figure,
            use_container_width=True,
            config={
                "displaylogo": False,
                "scrollZoom": True,
                "modeBarButtonsToAdd": [
                    "drawline",
                    "eraseshape",
                ],
            },
        )

        render_live_plot_button(
            "discharge"
        )

        st.info(
            "Metrics below are computed independently for each period; warm-up data are excluded."
        )

        st.markdown("##### Calibration period")
        calibration_metric_columns = st.columns(5)

        calibration_metric_columns[0].metric(
            "NSE",
            score_text(score_calibration.get("NSE", np.nan)),
        )
        calibration_metric_columns[1].metric(
            "KGE",
            score_text(score_calibration.get("KGE", np.nan)),
        )
        calibration_metric_columns[2].metric(
            "RMSE",
            (
                "not available"
                if not np.isfinite(score_calibration.get("RMSE", np.nan))
                else f"{score_calibration['RMSE']:.4f} m3/s"
            ),
        )
        calibration_metric_columns[3].metric(
            "Bias",
            (
                "not available"
                if not np.isfinite(score_calibration.get("Bias", np.nan))
                else f"{score_calibration['Bias']:.4f} m3/s"
            ),
        )
        calibration_metric_columns[4].metric(
            "Observed points used",
            f"{n_valid_calibration:,}",
        )

        st.markdown("##### Performance test period")
        validation_metric_columns = st.columns(5)

        validation_metric_columns[0].metric(
            "NSE",
            score_text(score_validation.get("NSE", np.nan)),
        )
        validation_metric_columns[1].metric(
            "KGE",
            score_text(score_validation.get("KGE", np.nan)),
        )
        validation_metric_columns[2].metric(
            "RMSE",
            (
                "not available"
                if not np.isfinite(score_validation.get("RMSE", np.nan))
                else f"{score_validation['RMSE']:.4f} m3/s"
            ),
        )
        validation_metric_columns[3].metric(
            "Bias",
            (
                "not available"
                if not np.isfinite(score_validation.get("Bias", np.nan))
                else f"{score_validation['Bias']:.4f} m3/s"
            ),
        )
        validation_metric_columns[4].metric(
            "Observed points used",
            f"{n_valid_validation:,}",
        )

        save_column, history_column = st.columns(
            [1, 2],
            gap="large",
        )

        with save_column:
            calibration_note = st.text_input(
                "Calibration note",
                value="Manual trial",
                key="baget_trial_note",
            )

            if st.button(
                "Save this calibration trial",
                type="primary",
                use_container_width=True,
            ):
                # Store the performance metrics together with all parameter values
                # that define the current manual-calibration trial.
                trial = {
                    "label": calibration_note,
                    "calibration_NSE": score_calibration.get("NSE", np.nan),
                    "calibration_KGE": score_calibration.get("KGE", np.nan),
                    "calibration_RMSE": score_calibration.get("RMSE", np.nan),
                    "calibration_Bias": score_calibration.get("Bias", np.nan),
                    "calibration_valid_observations": n_valid_calibration,
                    "validation_NSE": score_validation.get("NSE", np.nan),
                    "validation_KGE": score_validation.get("KGE", np.nan),
                    "validation_RMSE": score_validation.get("RMSE", np.nan),
                    "validation_Bias": score_validation.get("Bias", np.nan),
                    "validation_valid_observations": n_valid_validation,
                    "n_hydrotopes": int(n_hydrotopes),
                    "TotalArea_km2": float(total_area_km2),
                    "kMC": float(kmc),
                    "aMC": float(amc),
                    "kCS": float(kcs),
                    "aCS": float(acs),
                    "kMS": float(kms),
                    "aMS": float(ams),
                    "C_loss": float(c_loss),
                }

                # Save the hydrotope-specific parameter values actually used by
                # the model. Area fractions are the normalized fractions used in
                # the simulation.
                for index in range(n_hydrotopes):
                    hydrotope_number = index + 1

                    trial[
                        f"H{hydrotope_number}_area_fraction"
                    ] = float(fractions_array[index])

                    trial[
                        f"H{hydrotope_number}_kis"
                    ] = float(kis[index])

                    trial[
                        f"H{hydrotope_number}_Emin"
                    ] = float(emin[index])

                    trial[
                        f"H{hydrotope_number}_Emax"
                    ] = float(emax[index])

                    trial[
                        f"H{hydrotope_number}_alpha"
                    ] = float(alpha[index])

                    trial[
                        f"H{hydrotope_number}_khyd"
                    ] = float(khy[index])

                    trial[
                        f"H{hydrotope_number}_lhyd"
                    ] = float(lhy[index])

                st.session_state.setdefault(
                    "baget_trials",
                    [],
                ).append(trial)

        with history_column:
            trial_frame = pd.DataFrame(
                st.session_state.get(
                    "baget_trials",
                    [],
                )
            )

            if trial_frame.empty:
                st.info(
                    "No calibration trial has been saved yet."
                )
            else:
                metric_columns = [
                    "label",
                    "calibration_NSE",
                    "calibration_KGE",
                    "calibration_RMSE",
                    "calibration_Bias",
                    "calibration_valid_observations",
                    "validation_NSE",
                    "validation_KGE",
                    "validation_RMSE",
                    "validation_Bias",
                    "validation_valid_observations",
                ]

                metric_columns = [
                    column
                    for column in metric_columns
                    if column in trial_frame.columns
                ]

                st.markdown("##### Saved trial performance")

                st.dataframe(
                    trial_frame[metric_columns],
                    use_container_width=True,
                    hide_index=True,
                )

                parameter_columns = [
                    column
                    for column in trial_frame.columns
                    if column not in metric_columns
                ]

                with st.expander(
                    "Show saved parameter values",
                    expanded=False,
                ):
                    st.dataframe(
                        trial_frame[
                            ["label"]
                            + [
                                column
                                for column in parameter_columns
                                if column != "label"
                            ]
                        ],
                        use_container_width=True,
                        hide_index=True,
                    )

                st.download_button(
                    "Download calibration history",
                    trial_frame.to_csv(index=False),
                    "baget_calibration_history.csv",
                    "text/csv",
                )


    # -----------------------------------------------------------------------------
    # Internal-flux tab
    # -----------------------------------------------------------------------------
    with flux_tab:
        st.subheader(
            ":blue",
            divider="blue",
        )

        st.markdown(
            load_colored_md("md_baget_06.md")
        )

        # Option to use the same numerical scale for both y-axes
        same_y_scale = st.toggle(
            "Use the same scale for both y-axes",
            value=False,
            key="baget_flux_same_y_scale",
        )

        flux_series_options = [
            "QMS - Matrix to spring",
            "QCS - Conduit to spring",
            "QCloss - Conduit loss",
            "QMC - Matrix-conduit exchange",
        ]

        for index in range(n_hydrotopes):
            flux_series_options.extend(
                [
                    f"Qis - Hydrotope {index + 1}",
                    f"Qhyd - Hydrotope {index + 1}",
                ]
            )

        flux_series_options.append(
            "Simulated spring discharge"
        )

        visible_flux_series = persistent_series_selector(
            "Displayed fluxes",
            options=flux_series_options,
            default_selected=[
                "QMS - Matrix to spring",
                "QCS - Conduit to spring",
                "QMC - Matrix-conduit exchange",
                "Simulated spring discharge",
            ],
            key="baget_flux_visible_series",
            help_text=(
                "Choose which fluxes are displayed. "
                "This selection is preserved when model parameters or "
                "the common y-axis scale are changed."
            ),
        )

        flux_figure = make_subplots(
            specs=[[{"secondary_y": True}]]
        )

        # Internal fluxes - left y-axis
        flux_figure.add_trace(
            go.Scatter(
                x=display_data.index,
                y=run_bot_display[4],
                name="QMS - Matrix to spring",
                visible=(
                    True
                    if "QMS - Matrix to spring" in visible_flux_series
                    else "legendonly"
                ),
            ),
            secondary_y=False,
        )

        flux_figure.add_trace(
            go.Scatter(
                x=display_data.index,
                y=run_bot_display[5],
                name="QCS - Conduit to spring",
                visible=(
                    True
                    if "QCS - Conduit to spring" in visible_flux_series
                    else "legendonly"
                ),
            ),
            secondary_y=False,
        )

        flux_figure.add_trace(
            go.Scatter(
                x=display_data.index,
                y=run_bot_display[2],
                name="QCloss - Conduit loss",
                visible=(
                    True
                    if "QCloss - Conduit loss" in visible_flux_series
                    else "legendonly"
                ),
            ),
            secondary_y=False,
        )

        flux_figure.add_trace(
            go.Scatter(
                x=display_data.index,
                y=run_bot_display[6],
                name="QMC - Matrix-conduit exchange",
                visible=(
                    True
                    if "QMC - Matrix-conduit exchange" in visible_flux_series
                    else "legendonly"
                ),
            ),
            secondary_y=False,
        )

        for index in range(n_hydrotopes):

            flux_figure.add_trace(
                go.Scatter(
                    x=display_data.index,
                    y=run_up_display[1, :, index],
                    name=(
                        "Qis - Hydrotope "
                        f"{index + 1}"
                    ),
                    visible=(
                        True
                        if f"Qis - Hydrotope {index + 1}" in visible_flux_series
                        else "legendonly"
                    ),
                ),
                secondary_y=False,
            )

            flux_figure.add_trace(
                go.Scatter(
                    x=display_data.index,
                    y=run_up_display[2, :, index],
                    name=(
                        "Qhyd - Hydrotope "
                        f"{index + 1}"
                    ),
                    visible=(
                        True
                        if f"Qhyd - Hydrotope {index + 1}" in visible_flux_series
                        else "legendonly"
                    ),
                ),
                secondary_y=False,
            )

        # Simulated spring discharge - right y-axis
        flux_figure.add_trace(
            go.Scatter(
                x=display_data.index,
                y=qsim_display,
                name="Simulated spring discharge",
                mode="lines",
                visible=(
                    True
                    if "Simulated spring discharge" in visible_flux_series
                    else "legendonly"
                ),
                line=dict(
                    color="#FF8C00",
                    dash="dash",
                    width=2,
                ),
            ),
            secondary_y=True,
        )

        # Calibration / validation markers
        flux_figure.add_vline(
            x=CALIBRATION_START,
            line_dash="dash",
            annotation_text="Calibration starts",
            annotation_position="top",
        )

        flux_figure.add_vline(
            x=VALIDATION_START,
            line_dash="dash",
            annotation_text="Performance test starts",
            annotation_position="top",
        )

        # Figure layout
        flux_figure.update_layout(
            height=560,
            xaxis_title="Time",
            hovermode="x unified",
            margin={
                "l": 20,
                "r": 20,
                "t": 25,
                "b": 80,
            },
                legend={
                "orientation": "h",
                "xanchor": "center",
                "x": 0.5,
                "yanchor": "top",
                "y": -0.18,
                "itemclick": False,
                "itemdoubleclick": False,
            },

        )

        flux_figure.update_yaxes(
            title_text="Internal fluxes (m3/s)",
            secondary_y=False,
            # Force scientific notation in the hover tooltip. Without this,
            # Plotly automatically uses SI prefixes for small values
            # (for example, 20 μ instead of 2.0e-05).
            hoverformat=".3e",
        )

        flux_figure.update_yaxes(
            title_text="Simulated spring discharge (m3/s)",
            secondary_y=True,
            hoverformat=".3e",
        )


        # Optional common y-axis scale
        if same_y_scale:

            flux_values = []

            if "QMS - Matrix to spring" in visible_flux_series:
                flux_values.append(
                    run_bot_display[4]
                )

            if "QCS - Conduit to spring" in visible_flux_series:
                flux_values.append(
                    run_bot_display[5]
                )

            if "QCloss - Conduit loss" in visible_flux_series:
                flux_values.append(
                    run_bot_display[2]
                )

            if "QMC - Matrix-conduit exchange" in visible_flux_series:
                flux_values.append(
                    run_bot_display[6]
                )

            for index in range(n_hydrotopes):
                if (
                    f"Qis - Hydrotope {index + 1}"
                    in visible_flux_series
                ):
                    flux_values.append(
                        run_up_display[1, :, index]
                    )

                if (
                    f"Qhyd - Hydrotope {index + 1}"
                    in visible_flux_series
                ):
                    flux_values.append(
                        run_up_display[2, :, index]
                    )

            if "Simulated spring discharge" in visible_flux_series:
                flux_values.append(
                    qsim_display
                )

            all_values = (
                np.concatenate(
                    [
                        np.asarray(values).ravel()
                        for values in flux_values
                    ]
                )
                if flux_values
                else np.array([])
            )

            # Remove NaN and infinite values
            all_values = all_values[
                np.isfinite(all_values)
            ]

            if len(all_values) > 0:

                data_min = float(
                    np.min(all_values)
                )

                data_max = float(
                    np.max(all_values)
                )

                # Most discharge/flux values are non-negative.
                # In this case, keep zero as the common lower limit.
                if data_min >= 0.0:

                    common_min = 0.0

                    if data_max > 0.0:
                        common_max = (
                            data_max * 1.05
                        )
                    else:
                        common_max = 1.0

                # If a flux contains negative values, retain them
                # and add a small margin on both sides.
                else:

                    data_span = (
                        data_max - data_min
                    )

                    if data_span > 0.0:
                        padding = (
                            0.05 * data_span
                        )
                    else:
                        padding = 0.1

                    common_min = (
                        data_min - padding
                    )

                    common_max = (
                        data_max + padding
                    )

                common_range = [
                    common_min,
                    common_max,
                ]

                flux_figure.update_yaxes(
                    range=common_range,
                    secondary_y=False,
                )

                flux_figure.update_yaxes(
                    range=common_range,
                    secondary_y=True,
                )

        # Publish the fully configured figure to the live companion view.
        publish_live_plot(
            "fluxes",
            flux_figure,
        )

        # Plot
        st.plotly_chart(
            flux_figure,
            use_container_width=True,
            config={
                "displaylogo": False,
                "scrollZoom": True,
            },
        )

        render_live_plot_button(
            "fluxes"
        )

        st.info(
            "Use **Displayed fluxes** above the graph to choose which series are "
            "shown. The selection is preserved when parameters or the common "
            "y-axis scale are changed."
        )
    # -----------------------------------------------------------------------------
    # Storage tab
    # -----------------------------------------------------------------------------
    with storage_tab:
        st.subheader(
            ":blue[Internal model storages]",
            divider="blue",
        )

        st.markdown(
            load_colored_md("md_baget_07.md")
        )

        # ------------------------------------------------------------------
        # Compact teaching demo: fast-flow hysteresis
        # ------------------------------------------------------------------
        with st.expander(
            "💡 How does fast-flow hysteresis work?",
            expanded=True,
        ):
            st.markdown(
                """
Fast flow does **not** depend only on the current epikarst storage $E$.
It also depends on whether the fast pathway was already **ON** or **OFF**.

- If $E \\ge E_{\\max}$ → fast flow switches **ON**.
- If $E \\le E_{\\min}$ → fast flow switches **OFF**.
- If $E_{\\min} < E < E_{\\max}$ → the model **keeps the previous state**.

This is the hysteresis effect.
                """
            )

            demo_col1, demo_col2 = st.columns(
                [1.2, 1.0],
                gap="large",
            )

            with demo_col1:
                demo_emin = 30.0
                demo_emax = 70.0

                demo_e = st.slider(
                    "Example epikarst storage E (mm)",
                    min_value=0.0,
                    max_value=100.0,
                    value=50.0,
                    step=1.0,
                    key="baget_hysteresis_demo_e",
                )

                demo_previous_state = st.radio(
                    "Was the fast pathway previously active?",
                    options=["OFF", "ON"],
                    horizontal=True,
                    key="baget_hysteresis_demo_previous_state",
                )

                if demo_e >= demo_emax:
                    demo_state = "ON"
                    demo_reason = (
                        "E is above Emax, so the fast pathway is activated."
                    )
                elif demo_e <= demo_emin:
                    demo_state = "OFF"
                    demo_reason = (
                        "E is below Emin, so the fast pathway is deactivated."
                    )
                else:
                    demo_state = demo_previous_state
                    demo_reason = (
                        "E lies between Emin and Emax, so the pathway keeps "
                        "its previous state."
                    )

            with demo_col2:
                st.markdown(
                    f"""
**Example thresholds**

$E_{{\\min}} = {demo_emin:.0f}$ mm  
$E_{{\\max}} = {demo_emax:.0f}$ mm

**Current storage**

$E = {demo_e:.0f}$ mm

### Fast pathway: **{demo_state}**

{demo_reason}
                    """
                )

            st.caption(
                "Try setting E between 30 and 70 mm and switch the previous "
                "state between OFF and ON. The same E can then give two "
                "different fast-flow states: this is hysteresis."
            )

        storage_series_options = [
            "Matrix storage M",
            "Conduit storage C",
        ]

        for index in range(n_hydrotopes):
            storage_series_options.append(
                f"Epikarst storage E{index + 1}"
            )

        storage_series_options.append(
            "Simulated spring discharge"
        )

        visible_storage_series = persistent_series_selector(
            "Displayed storages",
            options=storage_series_options,
            default_selected=storage_series_options,
            key="baget_storage_visible_series",
            help_text=(
                "Choose which storage series are displayed. "
                "This selection is preserved when model parameters are changed."
            ),
        )

        storage_figure = make_subplots(
            specs=[[{"secondary_y": True}]]
            )

        storage_figure.add_trace(
            go.Scatter(
                x=display_data.index,
                y=run_bot_display[9],
                name="Matrix storage M",
                visible=(
                    True
                    if "Matrix storage M" in visible_storage_series
                    else "legendonly"
                ),
            ),
            secondary_y=False,
        )

        storage_figure.add_trace(
            go.Scatter(
                x=display_data.index,
                y=run_bot_display[8],
                name="Conduit storage C",
                visible=(
                    True
                    if "Conduit storage C" in visible_storage_series
                    else "legendonly"
                ),
            ),
            secondary_y=False,
        )

        for index in range(
            n_hydrotopes
        ):
            epikarst_visible = (
                True
                if f"Epikarst storage E{index + 1}" in visible_storage_series
                else "legendonly"
            )

            storage_figure.add_trace(
                go.Scatter(
                    x=display_data.index,
                    y=run_up_display[0, :, index],
                    name=(
                        "Epikarst storage E"
                        f"{index + 1}"
                    ),
                    visible=epikarst_visible,
                ),
                secondary_y=False,
            )

            # Hysteresis thresholds for the fast hydrotope pathway.
            # Emax activates Qhyd; Emin deactivates it.
            storage_figure.add_trace(
                go.Scatter(
                    x=[
                        display_data.index.min(),
                        display_data.index.max(),
                    ],
                    y=[
                        emin[index],
                        emin[index],
                    ],
                    name=f"Emin - Hydrotope {index + 1}",
                    mode="lines",
                    line=dict(
                        color="#FF4B4B",
                        dash="dot",
                        width=1.5,
                    ),
                    visible=epikarst_visible,
                    hovertemplate=(
                        f"Emin - Hydrotope {index + 1}: "
                        "%{y:.1f} mm<extra></extra>"
                    ),
                ),
                secondary_y=False,
            )

            storage_figure.add_trace(
                go.Scatter(
                    x=[
                        display_data.index.min(),
                        display_data.index.max(),
                    ],
                    y=[
                        emax[index],
                        emax[index],
                    ],
                    name=f"Emax - Hydrotope {index + 1}",
                    mode="lines",
                    line=dict(
                        color="#FF4B4B",
                        dash="dash",
                        width=1.5,
                    ),
                    visible=epikarst_visible,
                    hovertemplate=(
                        f"Emax - Hydrotope {index + 1}: "
                        "%{y:.1f} mm<extra></extra>"
                    ),
                ),
                secondary_y=False,
            )
        
        # Simulated spring discharge - right y-axis
        storage_figure.add_trace(
            go.Scatter(
                x=display_data.index,
                y=qsim_display,
                name="Simulated spring discharge",
                mode="lines",
                visible=(
                    True
                    if "Simulated spring discharge" in visible_storage_series
                    else "legendonly"
                ),
                line=dict(
                    color="#FF8C00",
                    dash="dash",
                    width=2,
                ),
            ),
            secondary_y=True,
        )


        storage_figure.add_vline(
            x=CALIBRATION_START,
            line_dash="dash",
            annotation_text="calibration starts",
            annotation_position="top",
        )

        storage_figure.add_vline(
            x=VALIDATION_START,
            line_dash="dash",
            annotation_text="Performance test starts",
            annotation_position="top",
        )

        storage_figure.update_layout(
            height=560,
            xaxis_title="Time",
            #yaxis_title="Storage or water level",
            hovermode="x unified",
            margin={
                "l": 20,
                "r": 20,
                "t": 25,
                "b": 80,
            },
                legend={
                "orientation": "h",
                "xanchor": "center",
                "x": 0.5,
                "yanchor": "top",
                "y": -0.18,
                "itemclick": False,
                "itemdoubleclick": False,
            },
        )

        storage_figure.update_yaxes(
            title_text="Storage / equivalent water level (mm)",
            secondary_y=False,
        )

        storage_figure.update_yaxes(
            title_text="Simulated spring discharge (m3/s)",
            secondary_y=True,
        )

        # storage_limits = axis_limit_controls(
            # "baget_storage",
            # display_data.index,
            # [
                # run_bot_display[9],
                # run_bot_display[8],
                # *[
                    # run_up_display[0, :, index]
                    # for index in range(
                        # n_hydrotopes
                    # )
                # ],
            # ],
        # )

        # apply_axis_limits(
            # storage_figure,
            # storage_limits,
        # )

        publish_live_plot(
            "storages",
            storage_figure,
        )

        st.plotly_chart(
            storage_figure,
            use_container_width=True,
            config={
                "displaylogo": False,
                "scrollZoom": True,
            },
        )

        render_live_plot_button(
            "storages"
        )

        st.info(
            "**Reading the Baget simulation:** the dotted lines are "
            "$E_{\\min}$ and the dashed lines are $E_{\\max}$. "
            "If $Q_{\\mathrm{hyd}}$ is already active while $E$ lies between "
            "the two thresholds, this is not an error: the pathway was "
            "activated earlier and remains ON until $E$ falls below "
            "$E_{\\min}$. The displayed period begins after a warm-up, so "
            "that activation may have happened before 1 March."
        )

        st.caption(
            "Use **Displayed storages** to choose which storage series are "
            "shown. The corresponding Emin/Emax lines follow the visibility "
            "of each epikarst storage."
        )
    # -----------------------------------------------------------------------------
    # Tutorial tab
    # -----------------------------------------------------------------------------
    with tutorial_tab:
        st.subheader(
            ":blue[Guided parameter investigation]",
            divider="blue",
        )

        st.markdown(
            load_colored_md("md_baget_08.md")
        )

        st.info(
            "**Tutorial strategy:** follow the water through the model from the "
            "hydrotopes to the spring. For every experiment: predict first, change "
            "one mechanism at a time, inspect the internal fluxes/storages and "
            "the spring hydrograph, and then reset to the Baget reference values."
        )

        st.markdown(
            """
        **Before you start**

        1. Click **Reset Baget parameters** so that everyone starts from the
           same reference simulation.
        2. In the Calibration tab, save this run with the note **Reference**.
        3. Open the **live Internal fluxes**, **live Storages**, and/or
           **live Discharge** plots when useful.
        4. During these exercises, use NSE/KGE only as supporting information.
           The main objective is to understand **why** the model response
           changes.
        """
        )

        exercise_keys = list(
            TUTORIAL_EXERCISES.keys()
        )

        exercise_tabs = st.tabs(
            [
                TUTORIAL_EXERCISES[key]["tab"]
                for key in exercise_keys
            ]
        )

        for exercise_key, exercise_tab in zip(
            exercise_keys,
            exercise_tabs,
        ):
            with exercise_tab:
                exercise = TUTORIAL_EXERCISES[
                    exercise_key
                ]

                render_tutorial_exercise_file(
                    MD_DIR / exercise["file"]
                )

                st.markdown("---")

                render_tutorial_popout_button(
                    exercise_key
                )


    # -----------------------------------------------------------------------------
    # Questions tab
    # -----------------------------------------------------------------------------
    with questions_tab:
        st.subheader(
            ":blue[Check your understanding]",
            divider="blue",
        )

        st.markdown(
            load_colored_md("md_baget_09.md")
        )

        render_assessment_fragment(
            QUESTIONS_DIR/"baget_ass.json",
            "baget_self_assessment",
            "🧠 **Show the Baget self-assessment**",
            default_open=True,
        )

        with st.expander(
            "Discussion question: Can a good hydrograph fit guarantee realistic internal processes?"
        ):
            st.markdown(
                load_colored_md("md_baget_10.md")
            )


    # -----------------------------------------------------------------------------
    # Results tab
    # -----------------------------------------------------------------------------
    with results_tab:
        st.subheader(
            ":blue[Simulation results and export]",
            divider="blue",
        )

        results = display_data.copy()

        results["Qsim"] = qsim_display
        results["QMS"] = run_bot_display[4]
        results["QCS"] = run_bot_display[5]
        results["QCloss"] = run_bot_display[2]
        results["QMC"] = run_bot_display[6]
        results["Matrix_storage"] = run_bot_display[9]
        results["Conduit_storage"] = run_bot_display[8]
        results["QobsS_available"] = (
            results["QobsS"].notna()
        )
        results["Period"] = np.where(
            results.index <= CALIBRATION_END,
            "Calibration",
            "Validation",
        )

        for index in range(
            n_hydrotopes
        ):
            results[
                f"E_H{index + 1}"
            ] = run_up_display[0, :, index]

            results[
                f"Qis_H{index + 1}"
            ] = run_up_display[1, :, index]

            results[
                f"Qhyd_H{index + 1}"
            ] = run_up_display[2, :, index]

        st.dataframe(
            results,
            use_container_width=True,
        )

        st.download_button(
            "Download calibration-validation simulation",
            results.to_csv().encode(
                "utf-8"
            ),
            "baget_lukars_calibration_validation_results.csv",
            "text/csv",
        )




render_baget_interactive_section()

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown("---")

columns_lic = st.columns(
    (4, 1)
)

with columns_lic[0]:
    st.markdown(
        f'Developed by {", ".join(author_list)} ({year}). '
        f"<br> {institution_text}",
        unsafe_allow_html=True,
    )

with columns_lic[1]:
    st.image(
        IMAGE_DIR/"CC_BY-SA_icon.png"
    )
