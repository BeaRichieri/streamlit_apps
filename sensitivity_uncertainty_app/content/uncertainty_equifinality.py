import json
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
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

ASSESSMENT_FILE = QUESTIONS_DIR / "uncertainty_equifinality_ass.json"

st.session_state.language = LANGUAGE


# -----------------------------------------------------------------------------
# Assessment renderer
# -----------------------------------------------------------------------------
def render_assessment(filename: Path) -> None:
    """Render an assessment in two-column rows."""
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
def render_assessment_fragment() -> None:
    """Keep the self-assessment independent from the interactive plots."""
    render_toggle_container(
        "uncertainty_equifinality_self_assessment",
        "🧠 **Show the equifinality self-assessment**",
        lambda: render_assessment(ASSESSMENT_FILE),
        default_open=False,
    )


# -----------------------------------------------------------------------------
# Synthetic reservoir model
# -----------------------------------------------------------------------------
def simple_reservoir_model(
    precipitation: np.ndarray,
    k: float,
    b: float,
    initial_storage: float = 5.0,
) -> np.ndarray:
    precipitation = np.asarray(precipitation, dtype=float)

    storage = float(initial_storage)
    discharge = np.zeros_like(precipitation, dtype=float)

    for time_index, rainfall in enumerate(precipitation):
        storage += rainfall

        q = k * max(storage, 0.0) ** b
        q = min(q, storage)

        discharge[time_index] = q
        storage = max(0.0, storage - q)

    return discharge


def kge(
    observed: np.ndarray,
    simulated: np.ndarray,
) -> float:
    """Kling-Gupta Efficiency used only as a compact fit measure."""
    observed = np.asarray(observed, dtype=float)
    simulated = np.asarray(simulated, dtype=float)

    obs_std = float(np.std(observed))
    sim_std = float(np.std(simulated))
    obs_mean = float(np.mean(observed))

    if (
        obs_std <= 0.0
        or sim_std <= 0.0
        or np.isclose(obs_mean, 0.0)
    ):
        return -np.inf

    correlation = float(
        np.corrcoef(observed, simulated)[0, 1]
    )
    alpha = sim_std / obs_std
    beta = float(np.mean(simulated)) / obs_mean

    return 1.0 - np.sqrt(
        (correlation - 1.0) ** 2
        + (alpha - 1.0) ** 2
        + (beta - 1.0) ** 2
    )


@st.cache_data
def build_synthetic_observations():
    """Create the same synthetic experiment that is later used for GLUE."""
    n_steps = 80
    precipitation = np.zeros(n_steps, dtype=float)

    event_steps = [
        4, 5, 6,
        17, 18,
        31, 32, 33,
        50, 51,
        64,
    ]
    event_amounts = [
        6, 12, 5,
        8, 14,
        7, 13, 9,
        6, 10,
        8,
    ]

    for index, amount in zip(
        event_steps,
        event_amounts,
    ):
        precipitation[index] = amount

    generating_k = 0.18
    generating_b = 1.15

    reference_discharge = simple_reservoir_model(
        precipitation,
        generating_k,
        generating_b,
    )

    rng = np.random.default_rng(2026)

    observed = np.clip(
        reference_discharge
        + rng.normal(
            0.0,
            0.08,
            size=n_steps,
        ),
        0.0,
        None,
    )

    return (
        precipitation,
        observed,
        generating_k,
        generating_b,
    )


@st.cache_data
def build_performance_surface():
    """Evaluate KGE on a regular k-b grid for the conceptual landscape."""
    precipitation, observed, _, _ = (
        build_synthetic_observations()
    )

    k_values = np.linspace(
        0.05,
        0.40,
        71,
    )
    b_values = np.linspace(
        0.80,
        1.50,
        71,
    )

    scores = np.zeros(
        (
            len(b_values),
            len(k_values),
        ),
        dtype=float,
    )

    for b_index, b_value in enumerate(b_values):
        for k_index, k_value in enumerate(k_values):
            simulated = simple_reservoir_model(
                precipitation,
                float(k_value),
                float(b_value),
            )
            scores[b_index, k_index] = kge(
                observed,
                simulated,
            )

    return k_values, b_values, scores


# -----------------------------------------------------------------------------
# Page title
# -----------------------------------------------------------------------------
st.markdown(
    load_md(
        MD_DIR,
        "md_equifinality_01.md",
        LANGUAGE,
    )
)

st.subheader(
    ":blue[Learning objectives]",
    divider="blue",
)

st.markdown(
    load_md(
        MD_DIR,
        "md_equifinality_learning_objectives.md",
        LANGUAGE,
    )
)


# -----------------------------------------------------------------------------
# Concept
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[What is equifinality?]",
    divider="blue",
)

st.markdown(
    load_md(
        MD_DIR,
        "md_equifinality_02.md",
        LANGUAGE,
    )
)

concept_col1, concept_col2 = st.columns(
    2,
    gap="small",
)

with concept_col1:
    with st.container(
        border=True,
        height=265,
    ):
        st.markdown("### 🎯 One best parameter set")
        st.markdown(
            load_md(
                MD_DIR,
                "md_equifinality_one_best.md",
                LANGUAGE,
            )
        )

with concept_col2:
    with st.container(
        border=True,
        height=265,
    ):
        st.markdown("### 🎲 Several plausible parameter sets")
        st.markdown(
            load_md(
                MD_DIR,
                "md_equifinality_many_sets.md",
                LANGUAGE,
            )
        )

st.warning(
    load_md(
        MD_DIR,
        "md_equifinality_key_message.md",
        LANGUAGE,
    )
)


# -----------------------------------------------------------------------------
# Synthetic experiment
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[Synthetic experiment]",
    divider="blue",
)

st.markdown(
    load_md(
        MD_DIR,
        "md_equifinality_model.md",
        LANGUAGE,
    )
)

equation_col1, equation_col2, equation_col3 = st.columns(
    3,
    gap="small",
)

with equation_col1:
    with st.container(border=True, height=130):
        st.latex(
            r"\widetilde{S}_t=S_{t-1}+P_t"
        )

with equation_col2:
    with st.container(border=True, height=130):
        st.latex(
            r"Q_t=\min\left(k\widetilde{S}_t^{\,b},\widetilde{S}_t\right)"
        )

with equation_col3:
    with st.container(border=True, height=130):
        st.latex(
            r"S_t=\widetilde{S}_t-Q_t"
        )

st.info(
    load_md(
        MD_DIR,
        "md_equifinality_model_note.md",
        LANGUAGE,
    )
)

(
    precipitation,
    observed,
    generating_k,
    generating_b,
) = build_synthetic_observations()

with st.expander(
    "How were the synthetic observations generated?"
):
    st.markdown(
        load_md(
            MD_DIR,
            "md_equifinality_observations.md",
            LANGUAGE,
        )
    )


# -----------------------------------------------------------------------------
# Interactive comparison
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[Can different parameter sets fit similarly well?]",
    divider="blue",
)

st.markdown(
    load_md(
        MD_DIR,
        "md_equifinality_interactive.md",
        LANGUAGE,
    )
)

set_a_col, set_b_col = st.columns(
    2,
    gap="large",
)

with set_a_col:
    with st.container(border=True):
        st.markdown("#### Parameter set A")

        k_a = st.slider(
            "k — set A",
            min_value=0.05,
            max_value=0.40,
            value=0.18,
            step=0.005,
            key="equifinality_k_a",
        )

        b_a = st.slider(
            "b — set A",
            min_value=0.80,
            max_value=1.50,
            value=1.15,
            step=0.01,
            key="equifinality_b_a",
        )

with set_b_col:
    with st.container(border=True):
        st.markdown("#### Parameter set B")

        k_b = st.slider(
            "k — set B",
            min_value=0.05,
            max_value=0.40,
            value=0.315,
            step=0.005,
            key="equifinality_k_b",
        )

        b_b = st.slider(
            "b — set B",
            min_value=0.80,
            max_value=1.50,
            value=0.96,
            step=0.01,
            key="equifinality_b_b",
        )


simulation_a = simple_reservoir_model(
    precipitation,
    k_a,
    b_a,
)

simulation_b = simple_reservoir_model(
    precipitation,
    k_b,
    b_b,
)

kge_a = kge(
    observed,
    simulation_a,
)

kge_b = kge(
    observed,
    simulation_b,
)

metric_col1, metric_col2, metric_col3 = st.columns(
    3
)

metric_col1.metric(
    "KGE — set A",
    f"{kge_a:.3f}",
)

metric_col2.metric(
    "KGE — set B",
    f"{kge_b:.3f}",
)

parameter_distance = np.sqrt(
    (
        (k_a - k_b)
        / (0.40 - 0.05)
    ) ** 2
    + (
        (b_a - b_b)
        / (1.50 - 0.80)
    ) ** 2
)

metric_col3.metric(
    "Normalized parameter distance",
    f"{parameter_distance:.2f}",
    help=(
        "A simple normalized distance between sets A and B in the "
        "two-dimensional parameter space. It is included only to show "
        "that similar model performance can occur for clearly different "
        "parameter combinations."
    ),
)


# Hydrograph
time = np.arange(len(observed))

hydrograph = go.Figure()

hydrograph.add_trace(
    go.Scatter(
        x=time,
        y=observed,
        mode="markers",
        name="Synthetic observations",
        marker=dict(
            size=6,
            color="black",
        ),
    )
)

hydrograph.add_trace(
    go.Scatter(
        x=time,
        y=simulation_a,
        mode="lines",
        name="Set A",
        line=dict(width=2.5),
    )
)

hydrograph.add_trace(
    go.Scatter(
        x=time,
        y=simulation_b,
        mode="lines",
        name="Set B",
        line=dict(
            width=2.5,
            dash="dash",
        ),
    )
)

hydrograph.update_layout(
    height=420,
    margin=dict(
        l=20,
        r=20,
        t=20,
        b=40,
    ),
    xaxis_title="Time step",
    yaxis_title="Discharge",
    legend=dict(
        orientation="h",
        y=1.15,
    ),
)

st.plotly_chart(
    hydrograph,
    use_container_width=True,
    key="equifinality_hydrograph",
    config={
        "displaylogo": False,
    },
)


# -----------------------------------------------------------------------------
# Performance landscape
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[Parameter compensation in the performance landscape]",
    divider="blue",
)

st.markdown(
    load_md(
        MD_DIR,
        "md_equifinality_surface.md",
        LANGUAGE,
    )
)

k_values, b_values, score_surface = (
    build_performance_surface()
)

surface_figure = go.Figure()

surface_figure.add_trace(
    go.Contour(
        x=k_values,
        y=b_values,
        z=score_surface,
        contours=dict(
            coloring="heatmap",
            showlabels=True,
        ),
        colorbar=dict(
            title="KGE",
        ),
        hovertemplate=(
            "k = %{x:.3f}<br>"
            "b = %{y:.3f}<br>"
            "KGE = %{z:.3f}"
            "<extra></extra>"
        ),
        name="KGE surface",
    )
)

surface_figure.add_trace(
    go.Scatter(
        x=[k_a],
        y=[b_a],
        mode="markers+text",
        name="Set A",
        text=["A"],
        textposition="top center",
        marker=dict(
            size=13,
            symbol="circle",
            color="white",
            line=dict(
                color="black",
                width=2,
            ),
        ),
    )
)

surface_figure.add_trace(
    go.Scatter(
        x=[k_b],
        y=[b_b],
        mode="markers+text",
        name="Set B",
        text=["B"],
        textposition="top center",
        marker=dict(
            size=13,
            symbol="diamond",
            color="white",
            line=dict(
                color="black",
                width=2,
            ),
        ),
    )
)

surface_figure.update_layout(
    height=470,
    margin=dict(
        l=20,
        r=20,
        t=20,
        b=45,
    ),
    xaxis_title="Reservoir coefficient k",
    yaxis_title="Nonlinearity exponent b",
    legend=dict(
        orientation="h",
        y=1.12,
    ),
)

surface_figure.update_xaxes(
    range=[0.05, 0.40]
)
surface_figure.update_yaxes(
    range=[0.80, 1.50]
)

st.plotly_chart(
    surface_figure,
    use_container_width=True,
    key="equifinality_surface",
    config={
        "displaylogo": False,
    },
)

st.caption(
    "A narrow peak would indicate a well-constrained optimum. "
    "An elongated region or ridge of similarly high performance shows "
    "that changes in one parameter can be compensated by changes in another."
)


# -----------------------------------------------------------------------------
# Guided tutorial
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[Short tutorial]",
    divider="blue",
)

st.markdown(
    load_md(
        MD_DIR,
        "md_equifinality_tutorial_intro.md",
        LANGUAGE,
    )
)

for exercise_number, title in [
    (1, "Compare two good but different parameter sets"),
    (2, "Follow the high-performance ridge"),
    (3, "Connect equifinality to uncertainty analysis"),
]:
    with st.container(border=True):
        st.markdown(
            f"#### Exercise {exercise_number} — {title}"
        )

        st.markdown(
            load_md(
                MD_DIR,
                f"md_equifinality_tutorial_{exercise_number:02d}.md",
                LANGUAGE,
            )
        )

        with st.expander("💡 Show answer"):
            st.markdown(
                load_md(
                    MD_DIR,
                    f"md_equifinality_tutorial_{exercise_number:02d}_answer.md",
                    LANGUAGE,
                )
            )


# -----------------------------------------------------------------------------
# Check understanding
# -----------------------------------------------------------------------------
st.subheader(
    "❓ :blue[Check your understanding]",
    divider="blue",
)

st.markdown(
    load_md(
        MD_DIR,
        "md_equifinality_check.md",
        LANGUAGE,
    )
)

render_assessment_fragment()


# -----------------------------------------------------------------------------
# Take-home messages
# -----------------------------------------------------------------------------
st.subheader(
    "🎯 :blue[Main take-home messages]",
    divider="blue",
)

st.markdown(
    load_md(
        MD_DIR,
        "md_equifinality_takehome.md",
        LANGUAGE,
    )
)


# -----------------------------------------------------------------------------
# Further learning material
# -----------------------------------------------------------------------------
st.subheader(
    "📖 :blue[Further learning material]",
    divider="blue",
)

st.markdown(
    load_md(
        MD_DIR,
        "md_equifinality_further.md",
        LANGUAGE,
    )
)


# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
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
        str(
            IMAGE_DIR
            / "CC_BY-SA_icon.png"
        )
    )
