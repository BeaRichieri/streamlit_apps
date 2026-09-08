import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import qmc
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


PARAMETER_NAMES = ["x1", "x2", "x3"]
SAMPLE_OPTIONS = [32, 64, 128, 256, 512, 1024, 2048, 4096]
SOBOL_ASSESSMENT_FILE = QUESTIONS_DIR / "sensitivity_sobol_ass.json"


# -----------------------------------------------------------------------------
# Assessment renderer: same style used in the other sensitivity pages
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


def load_dynamic_md(filename: str, replacements: dict[str, str]) -> str:
    """Load Markdown and replace simple placeholders with current values."""
    markdown_text = load_md(
        MD_DIR,
        filename,
        LANGUAGE,
    )

    for placeholder, value in replacements.items():
        markdown_text = markdown_text.replace(
            placeholder,
            str(value),
        )

    return markdown_text


# -----------------------------------------------------------------------------
# Synthetic model
# -----------------------------------------------------------------------------
def synthetic_model_matrix(x, interaction_strength):
    x = np.asarray(x, dtype=float)

    x1 = x[:, 0]
    x2 = x[:, 1]
    x3 = x[:, 2]

    return (
        2.0 * x1
        + 1.50 * x1**2
        + 0.20 * x2
        + 2.0 * np.sin(np.pi * x3)
        + interaction_strength * (x1 - 0.5) * (x3 - 0.5)
    )


def exact_sobol_indices(interaction_strength):
    """Analytical Sobol' indices for the synthetic model used on this page.

    Because x1, x2 and x3 are independent U(0,1) variables and the interaction
    term is centered, the variance decomposition is available analytically.
    These exact values are used only as reference lines in the convergence plot.
    """
    variance_x1 = 31.0 / 30.0
    variance_x2 = 1.0 / 300.0
    variance_x3 = 2.0 - 16.0 / np.pi**2

    # Var[(x1 - 0.5)(x3 - 0.5)] = (1/12)*(1/12) = 1/144
    variance_x1_x3 = interaction_strength**2 / 144.0

    total_variance = (
        variance_x1
        + variance_x2
        + variance_x3
        + variance_x1_x3
    )

    first_order = np.array(
        [
            variance_x1 / total_variance,
            variance_x2 / total_variance,
            variance_x3 / total_variance,
        ],
        dtype=float,
    )

    total_order = np.array(
        [
            (variance_x1 + variance_x1_x3) / total_variance,
            variance_x2 / total_variance,
            (variance_x3 + variance_x1_x3) / total_variance,
        ],
        dtype=float,
    )

    return first_order, total_order


# -----------------------------------------------------------------------------
# Sobol' sampling and estimators
# -----------------------------------------------------------------------------
def generate_sobol_base_samples(
    base_sample_size: int,
    seed: int = 2026,
):
    """Generate the two base matrices A and B with low-discrepancy sampling.

    A scrambled Sobol sequence is generated in 2k dimensions and split into
    two k-dimensional matrices. N must be a power of two. The first rows are
    nested when N is increased, which makes the convergence illustration easy
    to interpret and produces much more stable estimates for this teaching
    example than ordinary pseudo-random sampling.
    """
    number_parameters = len(PARAMETER_NAMES)

    if (
        base_sample_size < 1
        or base_sample_size & (base_sample_size - 1)
    ):
        raise ValueError(
            "The base sample size N must be a power of two."
        )

    exponent = int(np.log2(base_sample_size))

    sampler = qmc.Sobol(
        d=2 * number_parameters,
        scramble=True,
        seed=seed,
    )

    base_sample = sampler.random_base2(
        m=exponent,
    )

    A = base_sample[:, :number_parameters]
    B = base_sample[:, number_parameters:]

    return A, B


def estimate_sobol_from_samples(
    A: np.ndarray,
    B: np.ndarray,
    interaction_strength: float,
):
    """Estimate first- and total-order Sobol' indices from A and B.

    For each parameter i, C_i is obtained by copying A and replacing only
    column i with column i from B.

    First order:
        Saltelli-type estimator.

    Total order:
        Jansen estimator.
    """
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)

    number_parameters = A.shape[1]

    fA = synthetic_model_matrix(A, interaction_strength)
    fB = synthetic_model_matrix(B, interaction_strength)

    output_variance = float(
        np.var(
            np.concatenate([fA, fB]),
            ddof=1,
        )
    )

    if output_variance <= 0.0:
        raise ValueError("Model-output variance is zero.")

    first_order = np.zeros(number_parameters, dtype=float)
    total_order = np.zeros(number_parameters, dtype=float)

    for parameter_index in range(number_parameters):
        C_i = A.copy()
        C_i[:, parameter_index] = B[:, parameter_index]

        fC = synthetic_model_matrix(
            C_i,
            interaction_strength,
        )

        # Saltelli-type first-order estimator:
        # contribution of parameter i acting alone.
        first_order[parameter_index] = (
            np.mean(
                fB * (fC - fA)
            )
            / output_variance
        )

        # Jansen total-order estimator:
        # contribution of parameter i including all interactions.
        total_order[parameter_index] = (
            np.mean(
                (fA - fC) ** 2
            )
            / (2.0 * output_variance)
        )

    return first_order, total_order, output_variance


def estimate_sobol_indices(
    base_sample_size: int,
    interaction_strength: float,
    seed: int = 2026,
):
    A, B = generate_sobol_base_samples(
        base_sample_size,
        seed=seed,
    )

    first_order, total_order, output_variance = (
        estimate_sobol_from_samples(
            A,
            B,
            interaction_strength,
        )
    )

    return A, B, first_order, total_order, output_variance


# -----------------------------------------------------------------------------
# Sampling-scheme visualization
# -----------------------------------------------------------------------------
def sampling_scheme_figure(parameter_index: int) -> go.Figure:
    """Show conceptually how A, B and hybrid C_i are constructed."""
    figure = go.Figure()

    selected_number = parameter_index + 1

    rows = [
        ("A", 2.5),
        ("B", 1.5),
        (f"C{selected_number}", 0.5),
    ]

    box_width = 0.70
    box_height = 0.55

    for row_name, y in rows:
        figure.add_annotation(
            x=-0.25,
            y=y,
            text=f"<b>{row_name}</b>",
            showarrow=False,
            font=dict(size=13),
        )

    for column_index, parameter_name in enumerate(PARAMETER_NAMES):
        figure.add_annotation(
            x=column_index + box_width / 2,
            y=2.92,
            text=f"<b>{parameter_name}</b>",
            showarrow=False,
            font=dict(size=12),
        )

    for column_index in range(3):
        # A row
        figure.add_shape(
            type="rect",
            x0=column_index,
            x1=column_index + box_width,
            y0=2.5 - box_height / 2,
            y1=2.5 + box_height / 2,
            line=dict(color="gray", width=1.2),
            fillcolor="rgba(220,220,220,0.30)",
        )
        figure.add_annotation(
            x=column_index + box_width / 2,
            y=2.5,
            text=f"a{column_index + 1}",
            showarrow=False,
        )

        # B row
        figure.add_shape(
            type="rect",
            x0=column_index,
            x1=column_index + box_width,
            y0=1.5 - box_height / 2,
            y1=1.5 + box_height / 2,
            line=dict(color="gray", width=1.2),
            fillcolor="rgba(220,220,220,0.30)",
        )
        figure.add_annotation(
            x=column_index + box_width / 2,
            y=1.5,
            text=f"b{column_index + 1}",
            showarrow=False,
        )

        # Hybrid C_i row
        comes_from_b = column_index == parameter_index
        cell_text = (
            f"b{column_index + 1}"
            if comes_from_b
            else f"a{column_index + 1}"
        )
        fill = (
            "rgba(242,142,43,0.30)"
            if comes_from_b
            else "rgba(220,220,220,0.30)"
        )

        figure.add_shape(
            type="rect",
            x0=column_index,
            x1=column_index + box_width,
            y0=0.5 - box_height / 2,
            y1=0.5 + box_height / 2,
            line=dict(
                color="#F28E2B" if comes_from_b else "gray",
                width=1.8 if comes_from_b else 1.2,
            ),
            fillcolor=fill,
        )
        figure.add_annotation(
            x=column_index + box_width / 2,
            y=0.5,
            text=cell_text,
            showarrow=False,
        )

    figure.add_annotation(
        x=parameter_index + box_width / 2,
        y=0.92,
        ax=parameter_index + box_width / 2,
        ay=1.15,
        text="replace this column",
        showarrow=True,
        arrowhead=2,
        font=dict(size=11),
    )

    figure.update_layout(
        height=270,
        margin=dict(l=30, r=20, t=20, b=10),
        xaxis=dict(
            range=[-0.45, 3.0],
            visible=False,
            fixedrange=True,
        ),
        yaxis=dict(
            range=[0.0, 3.0],
            visible=False,
            fixedrange=True,
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
    )

    return figure


# -----------------------------------------------------------------------------
# Page title and learning objectives
# -----------------------------------------------------------------------------
st.markdown(
    load_md(
        MD_DIR,
        "md_sobol_01.md",
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
        "md_sobol_learning_objectives.md",
        LANGUAGE,
    )
)

st.info(
    load_md(
        MD_DIR,
        "md_sobol_learning_purpose.md",
        LANGUAGE,
    )
)
# -----------------------------------------------------------------------------
# 1. Meaning of the indices
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[What do Sobol' indices represent?]",
    divider="blue",
)

st.markdown(
    load_md(
        MD_DIR,
        "md_sobol_02.md",
        LANGUAGE,
    )
)

st.info(
    load_md(
        MD_DIR,
        "md_sobol_variance_decomposition.md",
        LANGUAGE,
    )
)

definition_col1, definition_col2 = st.columns(
    2,
    gap="small",
)

with definition_col1:
    with st.container(
        border=True,
        height=330,
    ):
        st.markdown("#### First-order index $S_i$")
        st.markdown(
            load_md(
                MD_DIR,
                "md_sobol_first_order.md",
                LANGUAGE,
            )
        )

with definition_col2:
    with st.container(
        border=True,
        height=330,
    ):
        st.markdown("#### Total-order index $S_{T_i}$")
        st.markdown(
            load_md(
                MD_DIR,
                "md_sobol_total_order.md",
                LANGUAGE,
            )
        )

with st.expander(
    "Show the formal definitions and notation"
):
    st.markdown(
        load_md(
            MD_DIR,
            "md_sobol_notation.md",
            LANGUAGE,
        )
    )


# -----------------------------------------------------------------------------
# 2. How the Sobol' indices are estimated
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[How are Sobol' indices estimated?]",
    divider="blue",
)

st.markdown(
    load_md(
        MD_DIR,
        "md_sobol_estimation_simple.md",
        LANGUAGE,
    )
)

st.info(
    load_md(
        MD_DIR,
        "md_sobol_estimation_simple_info.md",
        LANGUAGE,
    )
)

# Simple visual workflow
col1, col2, col3 = st.columns([1, 20, 1])
with col2:
    st.image(
        str(IMAGE_DIR / "sobol.png"),
        use_container_width=True,
    )


with st.expander(
    "How is this implemented computationally?"
):
    st.markdown(
        load_md(
            MD_DIR,
            "md_sobol_sampling_intro.md",
            LANGUAGE,
        )
    )

    sampling_parameter = st.radio(
        "Parameter used in the sampling example",
        PARAMETER_NAMES,
        horizontal=True,
        key="sobol_sampling_parameter",
    )

    sampling_parameter_index = PARAMETER_NAMES.index(
        sampling_parameter
    )

    st.plotly_chart(
        sampling_scheme_figure(
            sampling_parameter_index,
        ),
        use_container_width=True,
        key="sobol_sampling_scheme",
        config={
            "displaylogo": False,
            "staticPlot": True,
        },
    )
    
    st.markdown(
        load_dynamic_md(
            "md_sobol_sampling_dynamic.md",
            {
                "[[PARAMETER]]": sampling_parameter,
                "[[INDEX]]": str(
                    sampling_parameter_index + 1
                ),
            },
        )
    )
        
    # scheme_col, scheme_text_col = st.columns(
        # [1.25, 1.0],
        # gap="small",
    # )

    # with scheme_col:
        # st.plotly_chart(
            # sampling_scheme_figure(
                # sampling_parameter_index,
            # ),
            # use_container_width=True,
            # key="sobol_sampling_scheme",
            # config={
                # "displaylogo": False,
                # "staticPlot": True,
            # },
        # )

    # with scheme_text_col:
        # st.markdown(
            # load_dynamic_md(
                # "md_sobol_sampling_dynamic.md",
                # {
                    # "[[PARAMETER]]": sampling_parameter,
                    # "[[INDEX]]": str(
                        # sampling_parameter_index + 1
                    # ),
                # },
            # )
        # )

    st.markdown(
        load_md(
            MD_DIR,
            "md_sobol_estimators.md",
            LANGUAGE,
        )
    )

    st.info(
        load_md(
            MD_DIR,
            "md_sobol_estimators_plain.md",
            LANGUAGE,
        )
    )


# -----------------------------------------------------------------------------
# 3. Synthetic experiment
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[Synthetic experiment]",
    divider="blue",
)

st.markdown(
    load_md(
        MD_DIR,
        "md_sobol_03.md",
        LANGUAGE,
    )
)

control_col, result_col = st.columns(
    [0.75, 1.45],
    gap="large",
)

with control_col:
    base_sample_size = st.select_slider(
        "Number of samples N",
        options=SAMPLE_OPTIONS,
        value=1024,
        key="sobol_N",
        help=(
            "N controls the base sampling effort. The app uses a low-discrepancy "
            "Sobol sequence. With k parameters, N samples require N(k+2) actual "
            "model evaluations."
        ),
    )

    interaction_strength = st.slider(
        "Interaction strength γ",
        min_value=0.0,
        max_value=4.0,
        value=2.0,
        step=0.25,
        key="sobol_gamma",
        help=(
            "γ controls the explicit x1–x3 interaction term "
            "γ(x1−0.5)(x3−0.5). Set γ = 0 to remove this interaction."
        ),
    )

(
    A,
    B,
    first_order,
    total_order,
    output_variance,
) = estimate_sobol_indices(
    base_sample_size,
    interaction_strength,
)

number_parameters = len(PARAMETER_NAMES)

# A and B each contain N runs, and one hybrid C_i matrix is required for
# every parameter.
evaluation_count = (
    base_sample_size
    * (number_parameters + 2)
)

interaction_gap = (
    total_order - first_order
)

with result_col:
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=PARAMETER_NAMES,
            y=first_order,
            name="First order Si — parameter alone",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "First order Si = %{y:.3f}"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Bar(
            x=PARAMETER_NAMES,
            y=total_order,
            name="Total order STi — parameter + interactions",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Total order STi = %{y:.3f}"
                "<extra></extra>"
            ),
        )
    )

    fig.add_hline(
        y=0.0,
        line_width=1,
        line_dash="dot",
    )

    fig.update_layout(
        barmode="group",
        height=420,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=40,
        ),
        xaxis_title="Parameter",
        yaxis_title="Fraction of output variance [-]",
        legend=dict(
            orientation="h",
            y=1.16,
        ),
    )

    fig.update_yaxes(
        range=[-0.08, 1.05],
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="sobol_indices",
        config={
            "displaylogo": False,
        },
    )

metric1, metric2, metric3 = st.columns(3)

metric1.metric(
    "Number of samples N",
    base_sample_size,
)

metric2.metric(
    "Model realizations",
    evaluation_count,
)

metric3.metric(
    "Interaction γ",
    f"{interaction_strength:.2f}",
)

st.caption(
    f"For k = {number_parameters} parameters, the current experiment uses "
    f"N(k+2) = {base_sample_size} × ({number_parameters}+2) = "
    f"{evaluation_count} model realizations."
)

st.markdown(
    load_md(
        MD_DIR,
        "md_sobol_results.md",
        LANGUAGE,
    )
)

results = pd.DataFrame(
    {
        "Parameter": PARAMETER_NAMES,
        "First-order Si — alone": first_order,
        "Total-order STi — alone + interactions": total_order,
        "Interaction gap STi − Si": interaction_gap,
    }
)

st.dataframe(
    results.round(3),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Parameter": st.column_config.TextColumn(
            "Parameter",
        ),
        "First-order Si — alone": st.column_config.NumberColumn(
            "First-order Si — alone",
            help=(
                "Estimated fraction of output variance explained by this "
                "parameter acting alone."
            ),
            format="%.3f",
        ),
        "Total-order STi — alone + interactions": st.column_config.NumberColumn(
            "Total-order STi — alone + interactions",
            help=(
                "Estimated fraction of output variance associated with this "
                "parameter, including all interactions involving it."
            ),
            format="%.3f",
        ),
        "Interaction gap STi − Si": st.column_config.NumberColumn(
            "Interaction gap STi − Si",
            help=(
                "Difference between total-order and first-order indices. "
                "A larger gap indicates stronger interaction effects involving "
                "this parameter."
            ),
            format="%.3f",
        ),
    },
)

st.warning(
    load_md(
        MD_DIR,
        "md_sobol_interaction_gap.md",
        LANGUAGE,
    )
)


# -----------------------------------------------------------------------------
# 4. Sample size and convergence
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[How does the sample size affect the estimates?]",
    divider="blue",
)

st.markdown(
    load_md(
        MD_DIR,
        "md_sobol_convergence_intro.md",
        LANGUAGE,
    )
)

convergence_parameter = st.radio(
    "Parameter to inspect",
    PARAMETER_NAMES,
    horizontal=True,
    key="sobol_convergence_parameter",
)

convergence_index = PARAMETER_NAMES.index(
    convergence_parameter
)

max_sample_size = max(SAMPLE_OPTIONS)

A_max, B_max = generate_sobol_base_samples(
    max_sample_size,
)

first_values = []
total_values = []

for sample_size in SAMPLE_OPTIONS:
    first_n, total_n, _ = estimate_sobol_from_samples(
        A_max[:sample_size],
        B_max[:sample_size],
        interaction_strength,
    )

    first_values.append(
        first_n[convergence_index]
    )
    total_values.append(
        total_n[convergence_index]
    )

# For this simple synthetic model, the exact Sobol' indices are known
# analytically. They are shown only as reference lines so that the meaning
# of convergence is visually clear.
exact_first, exact_total = exact_sobol_indices(
    interaction_strength
)

exact_first_value = exact_first[convergence_index]
exact_total_value = exact_total[convergence_index]

# N is a base sample size, not the number of model realizations.
# With k parameters, the actual computational cost is N(k+2).
evaluation_labels = [
    f"N={n}<br>{n * (number_parameters + 2)} runs"
    for n in SAMPLE_OPTIONS
]

conv_fig = go.Figure()

conv_fig.add_trace(
    go.Scatter(
        x=evaluation_labels,
        y=first_values,
        mode="lines+markers",
        name=f"Estimated Si — {convergence_parameter}",
        line=dict(width=2.5),
        marker=dict(size=8),
        hovertemplate=(
            "%{x}<br>"
            "Estimated Si = %{y:.4f}"
            "<extra></extra>"
        ),
    )
)

conv_fig.add_trace(
    go.Scatter(
        x=evaluation_labels,
        y=total_values,
        mode="lines+markers",
        name=f"Estimated STi — {convergence_parameter}",
        line=dict(width=2.5),
        marker=dict(size=8),
        hovertemplate=(
            "%{x}<br>"
            "Estimated STi = %{y:.4f}"
            "<extra></extra>"
        ),
    )
)

conv_fig.add_hline(
    y=exact_first_value,
    line_dash="dash",
    line_width=1.5,
    annotation_text="Exact Si",
    annotation_position="bottom right",
)

conv_fig.add_hline(
    y=exact_total_value,
    line_dash="dot",
    line_width=1.5,
    annotation_text="Exact STi",
    annotation_position="top right",
)

current_index = SAMPLE_OPTIONS.index(
    base_sample_size
)

current_label = evaluation_labels[current_index]

conv_fig.add_trace(
    go.Scatter(
        x=[
            current_label,
            current_label,
        ],
        y=[
            first_values[current_index],
            total_values[current_index],
        ],
        mode="markers",
        name="Current N",
        marker=dict(
            size=15,
            color="black",
            symbol="circle-open",
            line=dict(width=2),
        ),
        hoverinfo="skip",
    )
)

# Zoom the y-axis to the selected parameter so that changes with N are visible.
all_convergence_values = np.array(
    first_values
    + total_values
    + [exact_first_value, exact_total_value],
    dtype=float,
)

y_min = float(np.min(all_convergence_values))
y_max = float(np.max(all_convergence_values))
y_span = max(y_max - y_min, 0.01)
y_padding = 0.15 * y_span

conv_fig.update_layout(
    height=420,
    margin=dict(
        l=20,
        r=20,
        t=25,
        b=55,
    ),
    xaxis_title="Number of samples N and corresponding model realizations",
    yaxis_title="Estimated sensitivity index",
    legend=dict(
        orientation="h",
        y=1.20,
    ),
)

conv_fig.update_yaxes(
    range=[
        y_min - y_padding,
        y_max + y_padding,
    ]
)

st.plotly_chart(
    conv_fig,
    use_container_width=True,
    key="sobol_convergence",
    config={
        "displaylogo": False,
    },
)

st.caption(
    "The y-axis is automatically zoomed for the selected parameter so that "
    "changes with sample size are visible. Use the main Sobol' bar plot above "
    "to compare the absolute magnitude of the indices between parameters."
)

st.info(
    load_dynamic_md(
        "md_sobol_convergence_dynamic.md",
        {
            "[[PARAMETER]]": convergence_parameter,
            "[[N]]": str(base_sample_size),
        },
    )
)


# -----------------------------------------------------------------------------
# 5. Guided tutorial
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[Guided Sobol' experiment]",
    divider="blue",
)

st.markdown(
    load_md(
        MD_DIR,
        "md_sobol_04.md",
        LANGUAGE,
    )
)

for exercise_number, title in [
    (1, "Remove the interaction"),
    (2, "Increase the interaction strength"),
    (3, "Investigate sample-size convergence"),
    (4, "Compare Morris and Sobol'"),
]:
    with st.container(border=True):
        st.markdown(
            f"#### Exercise {exercise_number} — {title}"
        )
        st.markdown(
            load_md(
                MD_DIR,
                f"md_sobol_tutorial_{exercise_number:02d}.md",
                LANGUAGE,
            )
        )

        with st.expander("💡 Show answer"):
            st.markdown(
                load_md(
                    MD_DIR,
                    f"md_sobol_tutorial_{exercise_number:02d}_answer.md",
                    LANGUAGE,
                )
            )


# -----------------------------------------------------------------------------
# 6. Check understanding
# -----------------------------------------------------------------------------
st.subheader(
    "❓ :blue[Check your understanding]",
    divider="blue",
)

st.markdown(
    load_md(
        MD_DIR,
        "md_sobol_check_understanding.md",
        LANGUAGE,
    )
)

render_toggle_container(
    "sobol_self_assessment",
    "🧠 **Show the Sobol' self-assessment**",
    lambda: render_assessment(SOBOL_ASSESSMENT_FILE),
    default_open=False,
)


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
        "md_sobol_05.md",
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
        "md_sobol_06.md",
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
