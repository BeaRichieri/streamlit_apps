import json
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from streamlit_book import multiple_choice

from app_utils import load_md


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
MD_DIR = Path("md")
ASSESSMENT_FILE = Path("questions") / "parameter_uncertainty_ass.json"

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


# -----------------------------------------------------------------------------
# Synthetic GLUE example
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


def kge(observed: np.ndarray, simulated: np.ndarray) -> float:
    observed = np.asarray(observed, dtype=float)
    simulated = np.asarray(simulated, dtype=float)

    obs_std = float(np.std(observed))
    sim_std = float(np.std(simulated))
    obs_mean = float(np.mean(observed))

    if obs_std <= 0.0 or sim_std <= 0.0 or np.isclose(obs_mean, 0.0):
        return -np.inf

    correlation = float(np.corrcoef(observed, simulated)[0, 1])
    alpha = sim_std / obs_std
    beta = float(np.mean(simulated)) / obs_mean

    return 1.0 - np.sqrt(
        (correlation - 1.0) ** 2
        + (alpha - 1.0) ** 2
        + (beta - 1.0) ** 2
    )


def ensemble_quantiles(
    ensemble: np.ndarray,
    quantiles: list[float],
) -> dict[float, np.ndarray]:
    """Calculate ordinary quantiles across the behavioural ensemble."""
    ensemble = np.asarray(ensemble, dtype=float)

    return {
        quantile: np.quantile(
            ensemble,
            quantile,
            axis=0,
        )
        for quantile in quantiles
    }


def build_synthetic_glue_ensemble(num_samples: int = 600):
    n_steps = 80
    precipitation = np.zeros(n_steps, dtype=float)

    event_steps = [4, 5, 6, 17, 18, 31, 32, 33, 50, 51, 64]
    event_amounts = [6, 12, 5, 8, 14, 7, 13, 9, 6, 10, 8]

    for index, amount in zip(event_steps, event_amounts):
        precipitation[index] = amount

    true_k = 0.18
    true_b = 1.15
    true_discharge = simple_reservoir_model(
        precipitation,
        true_k,
        true_b,
    )

    rng = np.random.default_rng(2026)

    observed = np.clip(
        true_discharge + rng.normal(0.0, 0.08, size=n_steps),
        0.0,
        None,
    )

    sampled_k = rng.uniform(0.05, 0.40, size=num_samples)
    sampled_b = rng.uniform(0.80, 1.50, size=num_samples)

    simulations = np.vstack(
        [
            simple_reservoir_model(
                precipitation,
                k_value,
                b_value,
            )
            for k_value, b_value in zip(sampled_k, sampled_b)
        ]
    )

    scores = np.array(
        [
            kge(observed, simulation)
            for simulation in simulations
        ],
        dtype=float,
    )

    return (
        precipitation,
        observed,
        sampled_k,
        sampled_b,
        simulations,
        scores,
    )


def render_glue_playground() -> None:
    st.markdown("##### Explore a synthetic GLUE experiment")
    st.markdown(load_md(MD_DIR, "md_uncertainty_16.md", LANGUAGE))

    st.latex(r"\widetilde{S}_t = S_{t-1} + P_t")
    st.latex(r"Q_t = \min\left(k\,\widetilde{S}_t^{\,b},\;\widetilde{S}_t\right)")
    st.latex(r"S_t = \widetilde{S}_t - Q_t")

    st.caption(
        "The minimum term is a mass-balance safeguard: the reservoir cannot "
        "discharge more water than is currently available in storage."
    )

    st.markdown(load_md(MD_DIR, "md_uncertainty_16_02.md", LANGUAGE))
    st.markdown(load_md(MD_DIR, "md_uncertainty_16_03.md", LANGUAGE))

    parameter_col1, parameter_col2 = st.columns(2, gap="small")
    PARAMETER_RANGE_BOX_HEIGHT = 80

    with parameter_col1:
        with st.container(border=True, height=PARAMETER_RANGE_BOX_HEIGHT):
            st.latex(r"k\sim\mathcal{U}(0.05,\;0.40)")
            

    with parameter_col2:
        with st.container(border=True, height=PARAMETER_RANGE_BOX_HEIGHT):
            st.latex(r"b\sim\mathcal{U}(0.80,\;1.50)")


    st.info(load_md(MD_DIR, "md_uncertainty_16_04.md", LANGUAGE))

    (
        precipitation,
        observed,
        sampled_k,
        sampled_b,
        simulations,
        scores,
    ) = build_synthetic_glue_ensemble()

    st.markdown("##### Model input used in all realizations")

    precipitation_figure = go.Figure()
    precipitation_figure.add_trace(
        go.Bar(
            x=np.arange(len(precipitation)),
            y=precipitation,
            name="Synthetic precipitation",
            hovertemplate=(
                "Time step %{x}<br>"
                "Precipitation = %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )
    precipitation_figure.update_layout(
        height=240,
        margin=dict(l=20, r=20, t=10, b=20),
        xaxis_title="Time step",
        yaxis_title="Precipitation",
        showlegend=False,
    )
    precipitation_figure.update_yaxes(range=[0.0, 16.0])

    st.plotly_chart(
        precipitation_figure,
        use_container_width=True,
        key="uncertainty_glue_precipitation",
        config={"displaylogo": False},
    )

    st.markdown("##### Behavioural and non-behavioural simulations")
    st.markdown(load_md(MD_DIR, "md_uncertainty_16_05.md", LANGUAGE))

    st.latex(
        r"\mathcal{B}"
        r"="
        r"\left\{j:\;\mathrm{KGE}_j\geq \mathrm{KGE}_{\min}\right\}"
    )

    threshold = st.slider(
        "Behavioural threshold for the synthetic KGE score",
        min_value=0.30,
        max_value=0.90,
        value=0.60,
        step=0.05,
        key="uncertainty_glue_threshold",
    )

    behavioural = scores >= threshold
    behavioural_count = int(np.sum(behavioural))

    if behavioural_count == 0:
        st.warning(
            "No sampled parameter set fulfils this threshold. "
            "Lower the threshold to continue the demonstration."
        )
        return

    behavioural_simulations = simulations[behavioural]

    # In this introductory example, all behavioural simulations are treated
    # equally. Quantiles are calculated directly across the retained ensemble.
    quantiles = ensemble_quantiles(
        behavioural_simulations,
        [0.10, 0.25, 0.50, 0.75, 0.90],
    )

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    metric_col1.metric("Sampled sets", len(scores))
    metric_col2.metric("Behavioural sets", behavioural_count)
    metric_col3.metric("Threshold", f"KGE ≥ {threshold:.2f}")
    metric_col4.metric("Best KGE", f"{np.max(scores):.3f}")

    st.info(load_md(MD_DIR, "md_uncertainty_17.md", LANGUAGE))

    parameter_col, hydrograph_col = st.columns(
        [0.9, 1.4],
        gap="small",
    )

    with parameter_col:
        st.markdown("##### Behavioural parameter sets")

        parameter_figure = go.Figure()

        parameter_figure.add_trace(
            go.Scatter(
                x=sampled_k[~behavioural],
                y=sampled_b[~behavioural],
                mode="markers",
                name="Non-behavioural",
                marker=dict(size=6, opacity=0.30),
            )
        )

        parameter_figure.add_trace(
            go.Scatter(
                x=sampled_k[behavioural],
                y=sampled_b[behavioural],
                mode="markers",
                name="Behavioural",
                marker=dict(
                    size=7,
                    opacity=0.80,
                    color="#F28E2B",
                ),
            )
        )

        parameter_figure.update_layout(
            height=430,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="Reservoir coefficient k",
            yaxis_title="Nonlinearity exponent b",
            legend=dict(orientation="h", y=1.15),
        )

        parameter_figure.update_xaxes(range=[0.05, 0.40])
        parameter_figure.update_yaxes(range=[0.80, 1.50])

        st.plotly_chart(
            parameter_figure,
            use_container_width=True,
            key="uncertainty_glue_parameter_space",
            config={"displaylogo": False},
        )

        st.caption(
            "Several different parameter combinations can be behavioural. "
            "This illustrates the idea of equifinality."
        )

    with hydrograph_col:
        st.markdown("##### Predictive uncertainty")

        time = np.arange(len(observed))
        hydrograph_figure = go.Figure()

        hydrograph_figure.add_trace(
            go.Scatter(
                x=time,
                y=quantiles[0.90],
                mode="lines",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip",
            )
        )

        hydrograph_figure.add_trace(
            go.Scatter(
                x=time,
                y=quantiles[0.10],
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                fillcolor="rgba(128,128,128,0.18)",
                name="10–90% range",
                hoverinfo="skip",
            )
        )

        hydrograph_figure.add_trace(
            go.Scatter(
                x=time,
                y=quantiles[0.75],
                mode="lines",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip",
            )
        )

        hydrograph_figure.add_trace(
            go.Scatter(
                x=time,
                y=quantiles[0.25],
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                fillcolor="rgba(128,128,128,0.32)",
                name="25–75% range",
                hoverinfo="skip",
            )
        )

        hydrograph_figure.add_trace(
            go.Scatter(
                x=time,
                y=quantiles[0.50],
                mode="lines",
                name="Median",
                line=dict(width=2.5),
            )
        )

        hydrograph_figure.add_trace(
            go.Scatter(
                x=time,
                y=observed,
                mode="lines",
                name="Synthetic observations",
                line=dict(width=2.5),
            )
        )

        hydrograph_figure.update_layout(
            height=430,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="Time step",
            yaxis_title="Synthetic discharge",
            hovermode="x unified",
            legend=dict(orientation="h", y=1.18),
        )

        hydrograph_figure.update_yaxes(range=[0.0, 8.0])

        st.plotly_chart(
            hydrograph_figure,
            use_container_width=True,
            key="uncertainty_glue_predictive_range",
            config={"displaylogo": False},
        )

        st.caption(
            "The uncertainty bands summarize the predictions generated by the "
            "retained behavioural parameter sets."
        )

    st.caption(
        "In this introductory example, all behavioural simulations are treated "
        "equally and predictive uncertainty is summarized using ordinary ensemble "
        "quantiles. GLUE can also assign likelihood weights to behavioural "
        "simulations, but weighting is a separate modelling choice and is not "
        "considered here."
    )


# -----------------------------------------------------------------------------
# Page title and overview
# -----------------------------------------------------------------------------
st.markdown(load_md(MD_DIR, "md_uncertainty_01.md", LANGUAGE))


# -----------------------------------------------------------------------------
# Learning objectives
# -----------------------------------------------------------------------------
st.subheader(":blue[Learning objectives]", divider="blue")
st.markdown(load_md(MD_DIR, "md_uncertainty_02.md", LANGUAGE))


# -----------------------------------------------------------------------------
# Before we start
# -----------------------------------------------------------------------------
st.subheader("🧭 :blue[Before we start]", divider="blue")
st.markdown(load_md(MD_DIR, "md_uncertainty_03.md", LANGUAGE))

intro_col1, intro_col2 = st.columns(2, gap="small")
INTRO_BOX_HEIGHT = 350

with intro_col1:
    with st.container(border=True, height=INTRO_BOX_HEIGHT):
        st.markdown("### 📊 Sensitivity analysis")
        st.markdown(load_md(MD_DIR, "md_uncertainty_04.md", LANGUAGE))

with intro_col2:
    with st.container(border=True, height=INTRO_BOX_HEIGHT):
        st.markdown("### 🎲 Parameter uncertainty")
        st.markdown(load_md(MD_DIR, "md_uncertainty_05.md", LANGUAGE))


# -----------------------------------------------------------------------------
# Sources of model uncertainty
# -----------------------------------------------------------------------------
st.subheader(":blue[Where does model uncertainty come from?]", divider="blue")
st.markdown(load_md(MD_DIR, "md_uncertainty_06.md", LANGUAGE))

unc_col1, unc_col2, unc_col3, unc_col4 = st.columns(4, gap="small")
UNCERTAINTY_SOURCE_BOX_HEIGHT = 220

for column, title, description in [
    (unc_col1, "🌧️ <br> Input", "uncertainty in forcing data and boundary conditions"),
    (unc_col2, "🎛️ Parameter", "unknown or poorly constrained parameter values"),
    (unc_col3, "🧩 Structure", "simplifications and alternative model concepts"),
    (unc_col4, "📏 Observation", "measurement and observation uncertainty"),
]:
    with column:
        with st.container(
            border=True,
            height=UNCERTAINTY_SOURCE_BOX_HEIGHT,
        ):
            st.markdown(f"#### {title}",
            unsafe_allow_html=True,)
            
            st.markdown(description)

st.info(load_md(MD_DIR, "md_uncertainty_07.md", LANGUAGE))


# -----------------------------------------------------------------------------
# Parameter uncertainty
# -----------------------------------------------------------------------------
st.subheader(":blue[What is parameter uncertainty?]", divider="blue")
col1, col2, col3 = st.columns([1, 20, 1])
with col2:
    st.image(
        "assets/images/ensamble_1.png",
       # caption="General workflow of a conceptual hydrological model",
        use_container_width=True,
    )
    


# -----------------------------------------------------------------------------
# Equifinality
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[Equifinality: more than one plausible parameter set]",
    divider="blue",
)
st.warning(load_md(MD_DIR, "md_uncertainty_12.md", LANGUAGE))

equifinality_col1, equifinality_col2 = st.columns(2, gap="small")
EQUIFINALITY_BOX_HEIGHT = 340

with equifinality_col1:
    with st.container(border=True, height=EQUIFINALITY_BOX_HEIGHT):
        st.markdown("### 🎯 One optimum")
        st.markdown(load_md(MD_DIR, "md_uncertainty_10.md", LANGUAGE))

with equifinality_col2:
    with st.container(border=True, height=EQUIFINALITY_BOX_HEIGHT):
        st.markdown("### 🎲 Ensemble of plausible solutions")
        st.markdown(load_md(MD_DIR, "md_uncertainty_11.md", LANGUAGE))




# -----------------------------------------------------------------------------
# GLUE introduction
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[GLUE: Generalised Likelihood Uncertainty Estimation]",
    divider="blue",
)
st.markdown(load_md(MD_DIR, "md_uncertainty_13.md", LANGUAGE))

col1, col2, col3 = st.columns([1, 20, 1])
with col2:
    st.image(
        "assets/images/GLUE.png",
       # caption="General workflow of a conceptual hydrological model",
        use_container_width=True,
    )

# -----------------------------------------------------------------------------
# Interactive GLUE example
# -----------------------------------------------------------------------------
st.subheader(":blue[Interactive GLUE example]", divider="blue")
render_glue_playground()


# -----------------------------------------------------------------------------
# Predictive uncertainty
# -----------------------------------------------------------------------------
st.subheader(":blue[How do we interpret predictive uncertainty?]", divider="blue")
st.markdown(load_md(MD_DIR, "md_uncertainty_18.md", LANGUAGE))

predict_col1, predict_col2, predict_col3 = st.columns(3, gap="small")
PREDICTIVE_BOX_HEIGHT = 160

for column, title, description in [
    (
        predict_col1,
        "50% median",
        "the median of the behavioural predictions at each time step",
    ),
    (
        predict_col2,
        "25–75% range",
        "the interval containing the central 50% of the behavioural predictions",
    ),
    (
        predict_col3,
        "10–90% range",
        "the interval containing the central 80% of the behavioural predictions",
    ),
]:
    with column:
        with st.container(border=True, height=PREDICTIVE_BOX_HEIGHT):
            st.markdown(f"##### {title}")
            st.markdown(description)

st.info(load_md(MD_DIR, "md_uncertainty_19.md", LANGUAGE))

st.warning(load_md(MD_DIR, "md_uncertainty_19_more.md", LANGUAGE))
# -----------------------------------------------------------------------------
# Self-check
# -----------------------------------------------------------------------------
st.subheader("❓ :blue[Check your understanding]", divider="blue")
st.markdown(load_md(MD_DIR, "md_uncertainty_20.md", LANGUAGE))

with st.expander("🧠 Show the self-assessment"):
    render_assessment(ASSESSMENT_FILE)


# -----------------------------------------------------------------------------
# Take-home messages
# -----------------------------------------------------------------------------
st.subheader("🎯 :blue[Main take-home messages]", divider="blue")
st.markdown(load_md(MD_DIR, "md_uncertainty_21.md", LANGUAGE))


# -----------------------------------------------------------------------------
# Further learning material
# -----------------------------------------------------------------------------
st.subheader("📖 :blue[Further learning material]", divider="blue")
st.markdown(load_md(MD_DIR, "md_uncertainty_22.md", LANGUAGE))


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
    st.image("assets/images/CC_BY-SA_icon.png")
