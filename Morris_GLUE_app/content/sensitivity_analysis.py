import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
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
# Assessment renderer: established iNUX / streamlit-book JSON structure
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
# Small visual helpers
# -----------------------------------------------------------------------------
def centred_arrow(symbol: str = "→", padding_top: float = 2.0) -> None:
    st.markdown(
        f"<div style='text-align:center; padding-top:{padding_top}rem; "
        f"font-size:1.7rem'>{symbol}</div>",
        unsafe_allow_html=True,
    )


def visual_box(title: str, lines: list[str]) -> None:
    line_html = "<br>".join(lines)
    st.markdown(
        "<div style='text-align:center'>"
        f"<b>{title}</b><br>{line_html}</div>",
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Synthetic Morris example
# -----------------------------------------------------------------------------
MORRIS_PARAMETER_NAMES = ["x1", "x2", "x3"]
MORRIS_PARAMETER_DESCRIPTIONS = {
    "x1": "nonlinear but monotonic influence",
    "x2": "weak linear and additive influence",
    "x3": "strong nonlinear and non-monotonic influence",
}


def synthetic_morris_model(x):
    """Synthetic model with three deliberately different sensitivity behaviours.

    x1: nonlinear but monotonic
    x2: linear and additive
    x3: strongly nonlinear and non-monotonic
    """
    x1, x2, x3 = x

    return (
        2.0 * x1
        + 1.50 * x1**2
        + 0.20 * x2
        + 2.0 * np.sin(np.pi * x3)
    )


def generate_morris_trajectories(
    num_trajectories: int,
    num_levels: int,
    seed: int = 2026,
):
    """Generate simple randomized OAT trajectories on a Morris grid.

    The parameter space is normalized to [0, 1]^k. For an even number l of
    grid levels, the Morris step is Delta = l / [2(l - 1)], equivalent to
    l/2 grid intervals. Each trajectory changes one parameter at a time.
    """
    if num_levels % 2 != 0:
        raise ValueError("The number of Morris grid levels must be even.")

    rng = np.random.default_rng(seed)
    k = len(MORRIS_PARAMETER_NAMES)
    grid = np.linspace(0.0, 1.0, num_levels)
    step_index = num_levels // 2
    delta = step_index / (num_levels - 1)

    trajectories = []
    records = []

    for trajectory_id in range(num_trajectories):
        order = rng.permutation(k)
        directions = rng.choice([-1, 1], size=k)
        current_index = np.zeros(k, dtype=int)

        for parameter_index in range(k):
            direction = directions[parameter_index]
            if direction > 0:
                current_index[parameter_index] = int(
                    rng.integers(0, num_levels - step_index)
                )
            else:
                current_index[parameter_index] = int(
                    rng.integers(step_index, num_levels)
                )

        points = [grid[current_index].copy()]
        outputs = [synthetic_morris_model(points[0])]

        for parameter_index in order:
            previous_point = points[-1]
            previous_output = outputs[-1]

            current_index = current_index.copy()
            current_index[parameter_index] += (
                directions[parameter_index] * step_index
            )
            next_point = grid[current_index].copy()
            next_output = synthetic_morris_model(next_point)

            signed_step = next_point[parameter_index] - previous_point[parameter_index]
            elementary_effect = (
                (next_output - previous_output) / signed_step
            )

            records.append(
                {
                    "trajectory": trajectory_id + 1,
                    "parameter_index": parameter_index,
                    "parameter": MORRIS_PARAMETER_NAMES[parameter_index],
                    "start": previous_point.copy(),
                    "end": next_point.copy(),
                    "start_output": float(previous_output),
                    "end_output": float(next_output),
                    "step": float(abs(signed_step)),
                    "elementary_effect": float(elementary_effect),
                }
            )

            points.append(next_point)
            outputs.append(next_output)

        trajectories.append(np.asarray(points))

    return trajectories, records, float(delta)


def morris_metrics(records: list[dict]) -> pd.DataFrame:
    rows = []

    for parameter_index, parameter_name in enumerate(MORRIS_PARAMETER_NAMES):
        effects = np.array(
            [
                record["elementary_effect"]
                for record in records
                if record["parameter_index"] == parameter_index
            ],
            dtype=float,
        )

        mu = float(np.mean(effects))
        mu_star = float(np.mean(np.abs(effects)))
        sigma = float(np.std(effects, ddof=1)) if len(effects) > 1 else 0.0

        rows.append(
            {
                "Parameter": parameter_name,
                "μ": mu,
                "μ*": mu_star,
                "σ": sigma,
                "Teaching role": MORRIS_PARAMETER_DESCRIPTIONS[parameter_name],
            }
        )

    return pd.DataFrame(rows)

@st.fragment
def render_morris_playground() -> None:
    st.markdown("##### Learn Morris step by step with a synthetic model")

    st.markdown(
        """
Instead of starting from the general equations, we build the Morris method
step by step using a simple synthetic example. 

The question for Morris is: **which parameters influence the model output
most strongly, and how does their influence change across the parameter
space?**
"""
    )

    # -------------------------------------------------------------------------
    # Step 1: Synthetic model
    # -------------------------------------------------------------------------
    st.markdown("#### Step 1 — Start from a model")

    st.markdown(
        """
We consider a synthetic model with three parameters $x_1$, $x_2$, and $x_3$.
All three parameters vary between **0 and 1**, and the model produces one
scalar output $Y$:
"""
    )

    st.latex(
        r"Y=f(x_1,x_2,x_3)"
        r"=2x_1+1.50x_1^2+0.20x_2+2\sin(\pi x_3)"
    )


    # -------------------------------------------------------------------------
    # Step 2: Define and visualize the Morris experiment
    # -------------------------------------------------------------------------
    st.markdown("#### Step 2 — Define and explore the Morris experiment")

    st.markdown(
        """
Morris explores the parameter space on a **discrete grid** along **trajectories**.

A trajectory starts at one point in the parameter space and changes **one parameter at a time**:
"""
    )

    st.latex(
        r"(x_1,x_2,x_3)"
        r"\;\rightarrow\;"
        r"\text{change one parameter}"
        r"\;\rightarrow\;"
        r"\text{change a second parameter}"
        r"\;\rightarrow\;"
        r"\text{change the third parameter}"
    )

    st.markdown(
        """
Choose the number of **trajectories $r$** and the number of
**grid levels $l$**, and observe directly how the resulting trajectories
explore the three-dimensional parameter space.
"""
    )

    st.info(
        """
🧭 **Try it yourself**

- **How can you explore more locations in the parameter space?**  
  Increase and decrease $r$ and observe how the number of trajectories changes.

- **How can you sample the parameter space with a finer grid?**  
  Increase and decrease $l$ and observe the spacing of the possible parameter values.

- **Does a finer grid always ensure better coverage of the parameter space?**  
  Keep $r$ small and increase $l$. Then increase $r$ again and compare the coverage.
"""
    )



    settings_col, trajectory_col = st.columns(
        [0.70, 1.45],
        gap="small",
    )

    with settings_col:
        st.markdown("##### Experiment settings")

        num_trajectories = st.slider(
            "Number of trajectories r",
            min_value=1,
            max_value=40,
            value=4,
            step=1,
            key="sensitivity_morris_r",
        )

        num_levels = st.slider(
            "Number of grid levels l",
            min_value=2,
            max_value=20,
            value=4,
            step=2,
            key="sensitivity_morris_levels",
        )


    trajectories, records, delta = generate_morris_trajectories(
        num_trajectories,
        num_levels,
    )

    metrics_df = morris_metrics(records)
    number_parameters = len(MORRIS_PARAMETER_NAMES)
    number_evaluations = num_trajectories * (number_parameters + 1)

    with trajectory_col:
        st.markdown("##### Morris trajectories")

        figure = go.Figure()

        for trajectory_index, trajectory in enumerate(
            trajectories,
            start=1,
        ):
            figure.add_trace(
                go.Scatter3d(
                    x=trajectory[:, 0],
                    y=trajectory[:, 1],
                    z=trajectory[:, 2],
                    mode="lines+markers",
                    name=f"Trajectory {trajectory_index}",
                    showlegend=trajectory_index <= 6,
                    marker=dict(
                        size=4,
                    ),
                    line=dict(
                        width=3,
                    ),
                    opacity=0.80,
                )
            )

        figure.update_layout(
            height=470,
            margin=dict(
                l=0,
                r=0,
                t=10,
                b=0,
            ),
            scene=dict(
                xaxis=dict(
                    title="x₁",
                    range=[0, 1],
                    dtick=1 / (num_levels - 1),
                ),
                yaxis=dict(
                    title="x₂",
                    range=[0, 1],
                    dtick=1 / (num_levels - 1),
                ),
                zaxis=dict(
                    title="x₃",
                    range=[0, 1],
                    dtick=1 / (num_levels - 1),
                ),
            ),
            legend=dict(
                orientation="h",
                y=-0.08,
            ),
        )

        st.plotly_chart(
            figure,
            use_container_width=True,
            key="sensitivity_morris_trajectories",
            config={
                "displaylogo": False,
                "scrollZoom": False,
            },
        )

        if num_trajectories <= 6:
            st.caption(
                f"All {num_trajectories} trajectories are shown "
                "and listed in the legend."
            )
        else:
            st.caption(
                f"All {num_trajectories} trajectories are shown. "
                "Only the first six are listed in the legend."
            )

    # -------------------------------------------------------------------------
    # Explain the experiment after the user has seen the controls and grid
    # -------------------------------------------------------------------------
    st.markdown("##### What do these settings mean?")

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric(
            "Parameters n",
            number_parameters,
        )

    with metric_col2:
        st.metric(
            "Trajectories r",
            num_trajectories,
        )

    with metric_col3:
        st.metric(
            "Step Δ",
            f"{delta:.3f}",
        )

        with st.popover("How is Δ calculated?"):
            st.markdown(
                """
Each parameter varies between 0 and 1 on a grid with $l$ discrete levels.
For the standard Morris construction, $l$ is even and the step size is
"""
            )

            st.latex(r"\Delta=\frac{l}{2(l-1)}")

            st.markdown(
                f"""
With $l={num_levels}$ levels, the current step is

$\\Delta={delta:.3f}$.
"""
            )

    with metric_col4:
        st.metric(
            "Model realizations",
            number_evaluations,
        )

        with st.popover("How are realizations calculated?"):
            st.markdown(
                """
Along one trajectory, the model is evaluated once at the starting point and
then once after changing each of the $n$ parameters. Therefore each trajectory
contains $n+1$ model evaluations:
"""
            )

            st.latex(r"N_{\mathrm{eval}}=r(n+1)")

            st.markdown(
                f"""
For $r={num_trajectories}$ trajectories and $n={number_parameters}$ parameters:

$N_{{\\mathrm{{eval}}}}={num_trajectories}\\times({number_parameters}+1)
={number_evaluations}$ model realizations.
"""
            )

    st.caption(
        "Click the controls below Step Δ and Model realizations to see how "
        "these quantities are calculated."
    )


    # -------------------------------------------------------------------------
    # Step 3: One elementary effect
    # -------------------------------------------------------------------------
    st.markdown("#### Step 3 — Look at one elementary effect")

    st.markdown(
        """
For one step of a trajectory, only one parameter changes. The change in
model output, divided by the parameter step, is the **elementary effect**.
For parameter $k$:
"""
    )

    st.latex(
        r"EE_k(x)="
        r"\frac{"
        r"f(x_1,\ldots,x_{k-1},x_k+\Delta,x_{k+1},\ldots,x_n)-f(x)"
        r"}{\Delta}"
        r"="
        r"\frac{f(x+\Delta e_k)-f(x)}{\Delta}"
    )

    st.markdown(
        """
Here, $k$ identifies the parameter that changes and $e_k$ is the unit
vector that changes only parameter $k$.
"""
    )

    selected_parameter = st.selectbox(
        "Parameter to inspect",
        MORRIS_PARAMETER_NAMES,
        key="sensitivity_morris_selected_parameter",
    )

    example_record = next(
        record
        for record in records
        if record["parameter"] == selected_parameter
    )

    parameter_index = MORRIS_PARAMETER_NAMES.index(selected_parameter)
    parameter_number = parameter_index + 1

    # The trajectory generator permits positive and negative directions.
    # For the teaching display, orient the selected step from the lower
    # parameter value to the higher one so that it matches the manuscript
    # notation x_k + Delta while preserving the same elementary effect.
    raw_signed_step = (
        example_record["end"][parameter_index]
        - example_record["start"][parameter_index]
    )

    if raw_signed_step >= 0.0:
        display_start = example_record["start"]
        display_end = example_record["end"]
        display_start_output = example_record["start_output"]
        display_end_output = example_record["end_output"]
    else:
        display_start = example_record["end"]
        display_end = example_record["start"]
        display_start_output = example_record["end_output"]
        display_end_output = example_record["start_output"]

    display_step = (
        display_end[parameter_index]
        - display_start[parameter_index]
    )

    display_effect = (
        (display_end_output - display_start_output)
        / display_step
    )

    start_values = ", ".join(
        f"{value:.2f}"
        for value in display_start
    )

    end_values = ", ".join(
        f"{value:.2f}"
        for value in display_end
    )


    st.markdown(
        f"""
For the displayed effect of **{selected_parameter}** ($k={parameter_number}$):

Parameter vector before the change:
"""
    )
    st.latex(rf"x=({start_values})")

    st.markdown("Parameter vector after the change:")
    st.latex(rf"x+\Delta e_{{{parameter_number}}}=({end_values})")

    st.markdown("The corresponding model outputs are:")
    st.latex(
        rf"f(x)={display_start_output:.3f},"
        #rf"\qquad"
        rf"f(x+\Delta e_{{{parameter_number}}})={display_end_output:.3f}"
    )

    st.markdown("Therefore:")
    st.latex(
        rf"EE_{{{parameter_number}}}(x)"
        rf"=\frac{{{display_end_output:.3f}-{display_start_output:.3f}}}"
        rf"{{{display_step:.3f}}}"
        rf"={display_effect:.3f}"
    )

    # -------------------------------------------------------------------------
    # Step 4: From elementary effects to global measures
    # -------------------------------------------------------------------------
    st.markdown("#### Step 4 — Repeat the effects across the parameter space")

    st.markdown(
        """
One elementary effect describes sensitivity at only **one location** in the
parameter space. Morris repeats the calculation along $r$ trajectories, so
each parameter $k$ has a set of elementary effects
$EE_k^1(x),\\ldots,EE_k^r(x)$.

Two metrics are used to evaluate the sensitivity of each parameter $k$:
"""
    )

    metric_explain_col1, metric_explain_col2 = st.columns(2, gap="small")

    MORRIS_METRIC_BOX_HEIGHT = 440

    with metric_explain_col1:
        with st.container(border=True, height=MORRIS_METRIC_BOX_HEIGHT):
            st.markdown("##### Overall influence: $\\mu_k^*$")
            st.latex(
                r"\mu_k^*="
                r"\frac{1}{r}"
                r"\sum_{j=1}^{r}"
                r"\left|EE_k^j(x)\right|"
            )
            st.markdown(
                """
$\\mu_k^*$ is the **mean absolute elementary effect**. A large value means
that changing parameter $k$ generally produces a large change in the model
output.
"""
            )

    with metric_explain_col2:
        with st.container(border=True, height=MORRIS_METRIC_BOX_HEIGHT):
            st.markdown("##### Variability of the effect: $\\sigma_k$")
            st.latex(
                r"\sigma_k="
                r"\sqrt{"
                r"\frac{1}{r-1}"
                r"\sum_{j=1}^{r}"
                r"\left(EE_k^j(x)-\mu_k\right)^2"
                r"}"
            )
            st.markdown(
                """
$\\sigma_k$ is the **standard deviation of the elementary effects**. The signed
mean used in this expression is
"""
            )
            st.latex(
                r"\mu_k="
                r"\frac{1}{r}"
                r"\sum_{j=1}^{r}"
                r"EE_k^j(x)"
            )
            st.markdown(
                """
A large $\\sigma_k$ means that the effect of parameter $k$ changes strongly
depending on where the model is evaluated.
"""
            )

    # -------------------------------------------------------------------------
    # Step 5: Morris results and interpretation
    # -------------------------------------------------------------------------
    st.markdown("#### Step 5 — Interpret the Morris results")

    st.markdown(
        """
The two Morris metrics answer two complementary questions:

- $\\mu_k^*$ describes **how influential** parameter $k$ is overall;
- $\\sigma_k$ describes **how much the elementary effect changes** across the
  parameter space.

The ratio $\\sigma_k/\\mu_k^*$ is then used as an interpretation aid. It is
important to distinguish **linearity** from **monotonicity**: they are related,
but they are not the same property.
"""
    )

    mu_star_values = metrics_df["μ*"].to_numpy(dtype=float)
    sigma_values = metrics_df["σ"].to_numpy(dtype=float)

    ratio_values = np.divide(
        sigma_values,
        mu_star_values,
        out=np.zeros_like(sigma_values),
        where=mu_star_values > 0.0,
    )

    # ---------------------------------------------------------------------
    # Results plots
    # ---------------------------------------------------------------------
    result_col1, result_col2 = st.columns(
        [0.85, 1.25],
        gap="small",
    )

    with result_col1:
        st.markdown("##### Overall parameter influence")

        fig_mu = go.Figure()

        fig_mu.add_trace(
            go.Bar(
                x=metrics_df["Parameter"],
                y=mu_star_values,
                name="μ*",
                customdata=np.column_stack([sigma_values, ratio_values]),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "μ* = %{y:.3f}<br>"
                    "σ = %{customdata[0]:.3f}<br>"
                    "σ/μ* = %{customdata[1]:.3f}"
                    "<extra></extra>"
                ),
            )
        )

        fig_mu.update_layout(
            xaxis_title="Parameter",
            yaxis_title="μ*",
            height=410,
            margin=dict(
                l=10,
                r=10,
                t=10,
                b=40,
            ),
            showlegend=False,
        )

        st.plotly_chart(
            fig_mu,
            use_container_width=True,
            key="sensitivity_morris_mu_star",
            config={"displaylogo": False},
        )

        st.caption(
            "Larger μ* means a stronger overall influence on the analysed model output."
        )

    with result_col2:
        st.markdown("##### Response characteristics from μ* and σ")

        fig_sigma = go.Figure()

        max_value = float(
            max(
                np.max(mu_star_values),
                np.max(sigma_values),
                0.5,
            )
        )
        axis_max = 1.15 * max_value
        x_line = np.linspace(0.0, axis_max, 200)

        for ratio, dash_style in [
            (1.0, "solid"),
            (0.5, "dash"),
            (0.1, "dashdot"),
        ]:
            fig_sigma.add_trace(
                go.Scatter(
                    x=x_line,
                    y=ratio * x_line,
                    mode="lines",
                    name=f"σ/μ* = {ratio:.1f}",
                    line=dict(
                        width=1.8,
                        dash=dash_style,
                    ),
                    hoverinfo="skip",
                )
            )

        fig_sigma.add_trace(
            go.Scatter(
                x=mu_star_values,
                y=sigma_values,
                mode="markers+text",
                text=metrics_df["Parameter"],
                textposition="top center",
                customdata=np.column_stack([ratio_values]),
                marker=dict(
                    size=13,
                ),
                name="Parameters",
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "μ* = %{x:.3f}<br>"
                    "σ = %{y:.3f}<br>"
                    "σ/μ* = %{customdata[0]:.3f}"
                    "<extra></extra>"
                ),
            )
        )

        # Region labels following the interpretation shown in the reference figure.
        fig_sigma.add_annotation(
            x=0.82 * axis_max,
            y=0.055 * axis_max,
            text="Linear / nearly linear",
            showarrow=False,
            opacity=0.55,
        )
        fig_sigma.add_annotation(
            x=0.82 * axis_max,
            y=0.30 * axis_max,
            text="Monotonic",
            showarrow=False,
            opacity=0.55,
        )
        fig_sigma.add_annotation(
            x=0.78 * axis_max,
            y=0.70 * axis_max,
            text="Almost monotonic",
            showarrow=False,
            opacity=0.55,
        )
        fig_sigma.add_annotation(
            x=0.42 * axis_max,
            y=0.90 * axis_max,
            text="Nonlinear / interactions",
            showarrow=False,
            opacity=0.55,
        )

        fig_sigma.update_layout(
            xaxis_title="μ*",
            yaxis_title="σ",
            height=465,
            margin=dict(
                l=10,
                r=10,
                t=10,
                b=85,
            ),
            legend=dict(
                orientation="h",
                x=0.0,
                y=-0.18,
            ),
        )

        fig_sigma.update_xaxes(
            range=[0.0, axis_max],
            constrain="domain",
        )
        fig_sigma.update_yaxes(
            range=[0.0, axis_max],
            scaleanchor="x",
            scaleratio=1,
        )

        st.plotly_chart(
            fig_sigma,
            use_container_width=True,
            key="sensitivity_morris_mu_sigma",
            config={"displaylogo": False},
        )

        st.caption(
            "The 0.1, 0.5 and 1.0 lines are visual reference lines for "
            "constant σ/μ* ratios."
        )

    # ---------------------------------------------------------------------
    # Short interpretation introduction
    # ---------------------------------------------------------------------
    st.markdown("##### How to interpret the $\\mu^*$–$\\sigma$ plot")

    st.markdown(
        """
The position of a parameter in the $\\mu^*$–$\\sigma$ plane gives information
not only about its **overall influence**, but also about whether its elementary
effects are approximately **linear/additive, monotonic, or increasingly
non-monotonic and interaction-dominated**. The reference lines of constant
$\\sigma/\\mu^*$ help interpret these different response regimes.
"""
    )

    # ---------------------------------------------------------------------
    # Visual interpretation regions
    # ---------------------------------------------------------------------
    st.markdown("##### Visual interpretation of the reference lines")

    region_col1, region_col2, region_col3, region_col4 = st.columns(
        4,
        gap="small",
    )
    
    MORRIS_REGION_BOX_HEIGHT = 460

    with region_col1:
        with st.container(border=True, height=MORRIS_REGION_BOX_HEIGHT):
            st.markdown("**Linear / nearly linear**")
            st.latex(r"\frac{\sigma}{\mu^*}\approx 0")
            st.markdown(
                """
Elementary effects are constant or almost constant.

**Interpretation:** linear/additive, or very close to it.
"""
            )

    with region_col2:
        with st.container(border=True, height=MORRIS_REGION_BOX_HEIGHT):
            st.markdown("**Monotonic**")
            st.latex(r"0<\frac{\sigma}{\mu^*}<0.5")
            st.markdown(
                """
Elementary effects vary, but keep a consistent overall direction.

**Interpretation:** nonlinear behaviour may be present, but the response
remains monotonic.
"""
            )

    with region_col3:
        with st.container(border=True, height=MORRIS_REGION_BOX_HEIGHT):
            st.markdown("**Almost monotonic**")
            st.latex(
                r"0.5\lesssim\frac{\sigma}{\mu^*}\lesssim 1"
            )
            st.markdown(
                """
Elementary effects vary strongly.

**Interpretation:** increasing non-monotonicity and/or stronger interactions.
"""
            )

    with region_col4:
        with st.container(border=True, height=MORRIS_REGION_BOX_HEIGHT):
            st.markdown("**Strong nonlinear / interactions**")
            st.latex(r"\frac{\sigma}{\mu^*}\gtrsim 1")
            st.markdown(
                """
Elementary effects show very strong variability across the parameter space.

**Interpretation:** pronounced nonlinearity, non-monotonicity and/or interactions.
"""
            )

    st.info(
        """
🧭 **Now interpret the results**

Use the two plots and the reference regions above to answer:

- **Which parameter is the most sensitive?**
- **Which parameter is the least sensitive?**
- **Which parameter shows a linear and additive response?**
- **Which parameter is nonlinear but still monotonic?**
- **Which parameter shows the strongest nonlinear and non-monotonic response?**

Try changing $r$ and $l$ and check whether your interpretation remains stable.
"""
    )


# -----------------------------------------------------------------------------
# Page title and overview
# -----------------------------------------------------------------------------
st.markdown(load_md(MD_DIR, "md_sensitivity_01.md", LANGUAGE))


# -----------------------------------------------------------------------------
# Learning objectives
# -----------------------------------------------------------------------------
st.subheader(":blue[Learning objectives]", divider="blue")
st.markdown(load_md(MD_DIR, "md_sensitivity_02.md", LANGUAGE))


# -----------------------------------------------------------------------------
# Diagnostic assessment
# -----------------------------------------------------------------------------
st.subheader("🧭 :blue[Before we start]", divider="blue")
st.markdown(load_md(MD_DIR, "md_sensitivity_03.md", LANGUAGE))

render_toggle_container(
    "sensitivity_intro_pre_assessment",
    "🧠 **Show the diagnostic assessment**",
    lambda: render_assessment(QUESTIONS_DIR / "sensitivity_intro_pre_ass.json"),
    default_open=False,
)


# -----------------------------------------------------------------------------
# Forward and inverse modelling
# -----------------------------------------------------------------------------
st.subheader(":blue[Forward and inverse modelling]", divider="blue")
st.markdown(load_md(MD_DIR, "md_sensitivity_04.md", LANGUAGE))

# forward_col, inverse_col = st.columns(2, gap="small")

# with forward_col:
    # with st.container(border=True):
        # st.markdown("### ➡️ Forward modelling")
        # flow = st.columns([1.2, 0.28, 1.2, 0.28, 1.2])
        # with flow[0]:
            # visual_box("Inputs + parameters", ["P(t), ET(t)", "θ"])
        # with flow[1]:
            # centred_arrow()
        # with flow[2]:
            # visual_box("Model", ["governing equations", "model structure"])
        # with flow[3]:
            # centred_arrow()
        # with flow[4]:
            # visual_box("Simulation", ["Qsim(t)", "internal states"])

        # st.markdown(
            # "**Question answered:** If the inputs, model structure and parameters "
            # "are known, what response does the model produce?"
        # )

# with inverse_col:
    # with st.container(border=True):
        # st.markdown("### ↩️ Inverse modelling")
        # flow = st.columns([1.15, 0.25, 1.25, 0.25, 1.15])
        # with flow[0]:
            # visual_box("Observations", ["Qobs(t)", "other data"])
        # with flow[1]:
            # centred_arrow()
        # with flow[2]:
            # visual_box("Parameter estimation", ["run model", "compare", "update/select"])
        # with flow[3]:
            # centred_arrow()
        # with flow[4]:
            # visual_box("Plausible θ", ["one optimum", "or an ensemble"])

        # st.markdown(
            # "**Question answered:** Which parameter values or model states are "
            # "consistent with the available observations?"
        # )
        
col1, col2, col3 = st.columns([1, 20, 1])
with col2:
    st.image(IMAGE_DIR / 
        "forward_inverse_modeling.png",
        caption="Forward and inverse modelling.",
        use_container_width=True,
    )

st.info(
    "Forward and inverse modelling should not be equated with deterministic and "
    "stochastic modelling. A forward model can be deterministic or stochastic, "
    "and an inverse problem can be solved with deterministic optimisation or "
    "probabilistic / ensemble approaches."
)

with st.expander("Why can inverse modelling be difficult?"):
    st.markdown(load_md(MD_DIR, "md_sensitivity_05.md", LANGUAGE))


# -----------------------------------------------------------------------------
# Sensitivity analysis basics
# -----------------------------------------------------------------------------
st.subheader(":blue[What is parameter sensitivity analysis?]", divider="blue")
st.markdown(load_md(MD_DIR, "md_sensitivity_06.md", LANGUAGE))

question_col1, question_col2, question_col3 = st.columns(3, gap="small")

SENSITIVITY_OVERVIEW_BOX_HEIGHT = 300

with question_col1:
    with st.container(border=True, height=SENSITIVITY_OVERVIEW_BOX_HEIGHT):
        st.markdown("### 🎯 What is the aim?")
        st.markdown(
            "Identify how variation in model parameters changes a "
            "selected model output or performance measure."
        )

with question_col2:
    with st.container(border=True, height=SENSITIVITY_OVERVIEW_BOX_HEIGHT):
        st.markdown("### 🔍 Why do it?")
        st.markdown(
            "Understand model behaviour, screen influential parameters, reduce "
            "dimensionality and focus calibration or data-collection efforts."
        )

with question_col3:
    with st.container(border=True, height=SENSITIVITY_OVERVIEW_BOX_HEIGHT):
        st.markdown("### 🧭 Are all methods the same?")
        st.markdown(
            "No. Methods differ in how they sample the parameter space, what "
            "sensitivity measure they calculate and how much computation they need."
        )

st.warning(
    "Sensitivity is conditional on the analysed output, parameter ranges, forcing "
    "data, model structure and time period. A parameter can appear unimportant for "
    "one objective and be important for another process or observation."
)


# -----------------------------------------------------------------------------
# Common sensitivity-analysis families
# -----------------------------------------------------------------------------
st.subheader(":blue[Common sensitivity-analysis approaches]", divider="blue")
st.markdown(load_md(MD_DIR, "md_sensitivity_07.md", LANGUAGE))


# --- 1. Local versus global ---------------------------------------------------

st.markdown("### 1. Local vs global sensitivity analysis")

st.markdown(
    """
The first distinction concerns **which part of the parameter space is explored**.
"""
)

local_col, global_col = st.columns(2, gap="small")

LOCAL_GLOBAL_BOX_HEIGHT = 600

with local_col:
    with st.container(border=True, height=LOCAL_GLOBAL_BOX_HEIGHT):
        st.markdown("#### 📍 Local sensitivity analysis")

        st.markdown(
            """
A local sensitivity analysis investigates how the model output changes when
parameters are varied **close to one reference parameter set**.

Typically, one parameter is perturbed at a time while the others are kept fixed.

**Main characteristics**

- explores sensitivity around a specific parameter set;
- usually computationally inexpensive;
- useful for understanding the response of the model near a calibrated or
  reference solution;
- may miss sensitivities occurring in other regions of the parameter space;
- interactions and nonlinear behaviour are difficult to identify.
"""
        )


with global_col:
    with st.container(border=True, height=LOCAL_GLOBAL_BOX_HEIGHT):
        st.markdown("#### 🌍 Global sensitivity analysis")

        st.markdown(
            """
A global sensitivity analysis explores parameter effects over their
**entire predefined ranges**.

Parameters are varied at different locations in the multidimensional
parameter space.

**Main characteristics**

- explores the full parameter ranges;
- accounts for changes in sensitivity across the parameter space;
- can reveal nonlinear model responses;
- can investigate parameter interactions;
- generally requires more model evaluations than a local analysis.
"""
        )


st.info(
    "Morris and Sobol' are both global sensitivity-analysis methods: "
    "they explore parameter effects across predefined parameter ranges rather "
    "than only around a single reference parameter set."
)


# --- 2. Screening versus variance decomposition -------------------------------

st.markdown("### 2. What information should the sensitivity analysis provide?")

st.markdown(
    """
Global sensitivity methods can also be distinguished according to the
**type and level of information** they provide.
"""
)

screen_col, quantitative_col = st.columns(2, gap="small")

METHOD_COMPARISON_BOX_HEIGHT = 660

with screen_col:
    with st.container(border=True, height=METHOD_COMPARISON_BOX_HEIGHT):
        st.markdown("#### 🔎 Screening and ranking — Morris")

        st.markdown(
            """
The **Morris method** is designed primarily as a **global screening method**.

It evaluates elementary effects at several locations in the parameter space
and allows us to identify:

- parameters with a strong influence on the model output;
- parameters with little influence that may potentially be fixed;
- possible nonlinear effects and/or parameter interactions.

The main result is therefore a **ranking of parameter importance**, supported
by the Morris sensitivity measures such as $\\mu_k^{*}$ and $\\sigma_k$.

Morris is particularly useful when the model contains many parameters and a
more computationally expensive sensitivity analysis would be impractical.
"""
        )


with quantitative_col:
    with st.container(border=True, height=METHOD_COMPARISON_BOX_HEIGHT):
        st.markdown("#### 📊 Variance-based quantification — Sobol'")

        st.markdown(
            """
Variance-based methods, such as the **Sobol' method**, quantify how much of the
variability in the model output can be attributed to individual parameters and
their interactions.

Typical Sobol' indices include:

- **first-order sensitivity index** — contribution of one parameter alone;
- **total-order sensitivity index** — contribution of that parameter together
  with all its interactions with other parameters.

These methods provide a more complete **quantitative decomposition of output
variance**, but usually require substantially more model evaluations.
"""
        )


st.success(
    "**Key distinction:** Morris is mainly used to efficiently **screen and rank** "
    "parameters, whereas variance-based methods such as Sobol' quantify "
    "**how much of the output variance** is associated with each parameter "
    "and its interactions."
)

# -----------------------------------------------------------------------------
# Morris method — learn from the synthetic example first, formalize afterwards
# -----------------------------------------------------------------------------
st.subheader(":blue[Morris method: the idea]", divider="blue")

st.markdown(
    """
The Morris method is a **global screening method** that explores how changes
in model parameters influence a selected model output. It does this by moving
through the parameter space along **trajectories** and changing **one parameter at a time**.
"""
)

render_morris_playground()


# -----------------------------------------------------------------------------
# Morris self-check
# -----------------------------------------------------------------------------
with st.expander("🧠 Check your understanding — Morris method"):
    st.markdown(
        """
Use these questions to check whether you understood the main ideas of the
Morris method before completing this section.
"""
    )
    render_assessment(QUESTIONS_DIR/"sensitivity_morris_ass.json")


# -----------------------------------------------------------------------------
# Take-home messages
# -----------------------------------------------------------------------------
st.subheader("🎯 :blue[Main take-home messages]", divider="blue")

st.markdown(
    """
- **Sensitivity analysis asks how changes in model parameters affect a selected
  model output.** Its results are always conditional on the analysed output,
  parameter ranges, forcing data, model structure and time period.

- **Local and global sensitivity analyses explore different parts of the
  parameter space.** Local methods investigate behaviour around one reference
  parameter set, whereas global methods explore the predefined parameter ranges.

- **Morris is primarily a global screening and ranking method.** It is useful
  for identifying influential parameters and for reducing the dimensionality
  of problems with many parameters.

- In the Morris method, parameters are changed **one at a time along
  trajectories** on a discrete grid. Each trajectory with $n$ parameters
  requires $n+1$ model evaluations.

- The mean absolute elementary effect $\\mu_k^*$ describes the **overall
  influence** of parameter $k$. Larger values indicate a stronger effect on the
  analysed model output.

- The standard deviation $\\sigma_k$ describes how strongly the elementary
  effects vary across the parameter space. This variability can indicate
  **nonlinear responses and/or parameter interactions**.

- The $\\mu^*$-$\\sigma$ plot combines information about parameter importance
  and response characteristics. The ratio $\\sigma/\\mu^*$ can be used as a
  practical aid for distinguishing approximately linear, monotonic and
  increasingly non-monotonic response regimes.

- **Morris and Sobol' provide different levels of information.** Morris is an
  efficient screening method, whereas variance-based methods such as Sobol'
  provide a quantitative decomposition of output variance but usually require
  substantially more model evaluations.
"""
)


# -----------------------------------------------------------------------------
# Further learning material
# -----------------------------------------------------------------------------
st.subheader("📖 :blue[Further learning material]", divider="blue")

st.markdown(
    """
For a deeper introduction to sensitivity analysis and the Morris method:

- **Morris, M. D. (1991).** Factorial Sampling Plans for Preliminary
  Computational Experiments. *Technometrics*, 33(2), 161–174.  
  The original paper introducing the Elementary Effects method.

- **Campolongo, F., Cariboni, J., & Saltelli, A. (2007).** An effective
  screening design for sensitivity analysis of large models.
  *Environmental Modelling & Software*, 22(10), 1509–1518.  
  A widely used development of the Morris screening approach.

- **Saltelli, A., Ratto, M., Andres, T., Campolongo, F., Cariboni, J.,
  Gatelli, D., Saisana, M., & Tarantola, S. (2008).**
  *Global Sensitivity Analysis: The Primer*. Wiley.  
  A general introduction to global sensitivity analysis, including Morris
  and variance-based methods.

- **Pianosi, F., Beven, K., Freer, J., Hall, J. W., Rougier, J.,
  Stephenson, D. B., & Wagener, T. (2016).** Sensitivity analysis of
  environmental models: A systematic review with practical workflow.
  *Environmental Modelling & Software*, 79, 214–232.  
  A practical overview of sensitivity-analysis concepts and method selection.

- **Sobol', I. M. (2001).** Global sensitivity indices for nonlinear
  mathematical models and their Monte Carlo estimates.
  *Mathematics and Computers in Simulation*, 55(1–3), 271–280.  
  A key reference for variance-based global sensitivity analysis.
"""
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
    st.image(IMAGE_DIR / "CC_BY-SA_icon.png")
