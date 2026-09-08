from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st

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

BASE_DIR = st.session_state.BASE_DIR
CONTENT_DIR = st.session_state.CONTENT_DIR
ASSETS_DIR = st.session_state.ASSETS_DIR
IMAGE_DIR = st.session_state.IMAGE_DIR
MD_DIR = st.session_state.MD_DIR
QUESTIONS_DIR = st.session_state.QUESTIONS_DIR

st.session_state.language = LANGUAGE



PARAMETER_NAMES = ["x1", "x2", "x3"]


def load_dynamic_md(filename: str, replacements: dict[str, str]) -> str:
    """Load Markdown and replace simple teaching placeholders dynamically."""
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


def synthetic_model(x):
    x1, x2, x3 = np.asarray(x, dtype=float)
    return 2.0 * x1 + 1.50 * x1**2 + 0.20 * x2 + 2.0 * np.sin(np.pi * x3)


def local_sensitivity(reference, parameter_index, delta):
    reference = np.asarray(reference, dtype=float)

    x0 = float(reference[parameter_index])
    lower_bound = 0.0
    upper_bound = 1.0

    # ---------------------------------------------------------
    # Forward difference near the lower boundary
    # ---------------------------------------------------------
    if x0 - delta < lower_bound:
        x_plus = reference.copy()
        x_plus[parameter_index] = x0 + delta

        return float(
            (
                synthetic_model(x_plus)
                - synthetic_model(reference)
            )
            / delta
        )

    # ---------------------------------------------------------
    # Backward difference near the upper boundary
    # ---------------------------------------------------------
    if x0 + delta > upper_bound:
        x_minus = reference.copy()
        x_minus[parameter_index] = x0 - delta

        return float(
            (
                synthetic_model(reference)
                - synthetic_model(x_minus)
            )
            / delta
        )

    # ---------------------------------------------------------
    # Central difference inside the parameter domain
    # ---------------------------------------------------------
    x_minus = reference.copy()
    x_plus = reference.copy()

    x_minus[parameter_index] = x0 - delta
    x_plus[parameter_index] = x0 + delta

    return float(
        (
            synthetic_model(x_plus)
            - synthetic_model(x_minus)
        )
        / (2.0 * delta)
    )



def finite_difference_details(reference, parameter_index, delta):
    """Return the points and outputs used to estimate one local sensitivity."""
    reference = np.asarray(reference, dtype=float)

    x0 = float(reference[parameter_index])
    lower_bound = 0.0
    upper_bound = 1.0

    y0 = float(synthetic_model(reference))

    # Forward difference near the lower boundary.
    if x0 - delta < lower_bound:
        x_a = x0
        x_b = min(x0 + delta, upper_bound)

        point_a = reference.copy()
        point_b = reference.copy()
        point_b[parameter_index] = x_b

        y_a = y0
        y_b = float(synthetic_model(point_b))

        slope = (y_b - y_a) / (x_b - x_a)

        return {
            "method": "forward",
            "x_a": x_a,
            "x_b": x_b,
            "y_a": y_a,
            "y_b": y_b,
            "slope": float(slope),
        }

    # Backward difference near the upper boundary.
    if x0 + delta > upper_bound:
        x_a = max(x0 - delta, lower_bound)
        x_b = x0

        point_a = reference.copy()
        point_b = reference.copy()
        point_a[parameter_index] = x_a

        y_a = float(synthetic_model(point_a))
        y_b = y0

        slope = (y_b - y_a) / (x_b - x_a)

        return {
            "method": "backward",
            "x_a": x_a,
            "x_b": x_b,
            "y_a": y_a,
            "y_b": y_b,
            "slope": float(slope),
        }

    # Central difference inside the parameter domain.
    x_a = x0 - delta
    x_b = x0 + delta

    point_a = reference.copy()
    point_b = reference.copy()
    point_a[parameter_index] = x_a
    point_b[parameter_index] = x_b

    y_a = float(synthetic_model(point_a))
    y_b = float(synthetic_model(point_b))

    slope = (y_b - y_a) / (x_b - x_a)

    return {
        "method": "central",
        "x_a": x_a,
        "x_b": x_b,
        "y_a": y_a,
        "y_b": y_b,
        "slope": float(slope),
    }


st.markdown(load_md(MD_DIR, "md_local_01.md", LANGUAGE))

# -----------------------------------------------------------------------------
# Learning objectives
# -----------------------------------------------------------------------------
st.subheader(":blue[Learning objectives]", divider="blue")
st.markdown(
    load_md(
        MD_DIR,
        "md_local_learning_objectives.md",
        LANGUAGE,
    )
)

st.subheader(":blue[Synthetic model]", divider="blue")
st.latex(
    r"Y=2x_1+1.50x_1^2+0.20x_2+2\sin(\pi x_3),"
    r"\qquad x_1,x_2,x_3\in[0,1]"
)

st.subheader(":blue[Define the local experiment]", divider="blue")
st.markdown(load_md(MD_DIR, "md_local_02.md", LANGUAGE))

control_col, sensitivity_col = st.columns([0.85, 1.35], gap="large")

with control_col:
    st.markdown("##### Reference parameter set")

    x1 = st.slider(
        "x1",
        min_value=0.0,
        max_value=1.0,
        value=0.50,
        step=0.01,
        key="local_x1",
    )
    x2 = st.slider(
        "x2",
        min_value=0.0,
        max_value=1.0,
        value=0.50,
        step=0.01,
        key="local_x2",
    )
    x3 = st.slider(
        "x3",
        min_value=0.0,
        max_value=1.0,
        value=0.50,
        step=0.01,
        key="local_x3",
    )

    delta = st.slider(
        "Perturbation Δx",
        min_value=0.01,
        max_value=0.20,
        value=0.05,
        step=0.01,
        key="local_delta",
    )

reference = np.array([x1, x2, x3], dtype=float)
reference_output = float(synthetic_model(reference))
sensitivities = np.array(
    [local_sensitivity(reference, i, delta) for i in range(3)],
    dtype=float,
)

with sensitivity_col:
    st.markdown("##### Local sensitivities at the selected point")

    fig_bar = go.Figure()
    fig_bar.add_trace(
        go.Bar(
            x=PARAMETER_NAMES,
            y=np.abs(sensitivities),
            customdata=sensitivities,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "|local sensitivity| = %{y:.3f}<br>"
                "signed sensitivity = %{customdata:.3f}"
                "<extra></extra>"
            ),
        )
    )
    fig_bar.update_layout(
        height=340,
        margin=dict(l=20, r=20, t=15, b=30),
        xaxis_title="Parameter",
        yaxis_title="|local sensitivity|",
        showlegend=False,
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True,
        key="local_sensitivity_bars",
        config={"displaylogo": False},
    )

metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric("Model output Y", f"{reference_output:.3f}")
metric2.metric("S(x1)", f"{sensitivities[0]:.3f}")
metric3.metric("S(x2)", f"{sensitivities[1]:.3f}")
metric4.metric("S(x3)", f"{sensitivities[2]:.3f}")

st.subheader(":blue[See why the reference point matters]", divider="blue")

st.markdown(
    load_md(
        MD_DIR,
        "md_local_03_intro.md",
        LANGUAGE,
    )
)

selected_parameter = st.radio(
    "Parameter to inspect",
    PARAMETER_NAMES,
    horizontal=True,
    key="local_selected_parameter",
)

selected_index = PARAMETER_NAMES.index(selected_parameter)
selected_reference_value = float(reference[selected_index])

difference_details = finite_difference_details(
    reference,
    selected_index,
    delta,
)

grid = np.linspace(0.0, 1.0, 301)
response_values = []

for value in grid:
    point = reference.copy()
    point[selected_index] = value
    response_values.append(synthetic_model(point))

response_values = np.asarray(response_values, dtype=float)

response_figure = go.Figure()

# Full one-dimensional response curve.
response_figure.add_trace(
    go.Scatter(
        x=grid,
        y=response_values,
        mode="lines",
        name=f"Model response when varying {selected_parameter}",
        line=dict(width=3),
        hovertemplate=(
            f"{selected_parameter} = %{{x:.3f}}<br>"
            "Y = %{y:.3f}<extra></extra>"
        ),
    )
)

# Finite-difference line between the points used in the calculation.
response_figure.add_trace(
    go.Scatter(
        x=[
            difference_details["x_a"],
            difference_details["x_b"],
        ],
        y=[
            difference_details["y_a"],
            difference_details["y_b"],
        ],
        mode="lines",
        name="Finite-difference slope",
        line=dict(
            dash="dash",
            width=2.5,
        ),
        hoverinfo="skip",
    )
)

# Points used in the finite-difference calculation.
response_figure.add_trace(
    go.Scatter(
        x=[
            difference_details["x_a"],
            difference_details["x_b"],
        ],
        y=[
            difference_details["y_a"],
            difference_details["y_b"],
        ],
        mode="markers",
        name="Perturbation points",
        marker=dict(
            size=10,
            color="#F28E2B",
        ),
        hovertemplate=(
            f"{selected_parameter} = %{{x:.3f}}<br>"
            "Y = %{y:.3f}<extra></extra>"
        ),
    )
)

# Current reference point.
response_figure.add_trace(
    go.Scatter(
        x=[selected_reference_value],
        y=[reference_output],
        mode="markers",
        name="Reference point",
        marker=dict(
            size=12,
            color="black",
            symbol="circle",
        ),
        hovertemplate=(
            f"Reference {selected_parameter} = %{{x:.3f}}<br>"
            "Y = %{y:.3f}<extra></extra>"
        ),
    )
)

response_figure.update_layout(
    height=460,
    margin=dict(l=20, r=20, t=20, b=40),
    xaxis_title=f"{selected_parameter} value",
    yaxis_title="Model output Y",
    hovermode="closest",
    legend=dict(
        orientation="h",
        y=1.12,
    ),
)

response_figure.update_xaxes(
    range=[0.0, 1.0],
    fixedrange=False,
)

st.plotly_chart(
    response_figure,
    use_container_width=True,
    key="local_selected_response_curve",
    config={"displaylogo": False},
)

method_labels = {
    "central": "central finite difference",
    "forward": "forward finite difference",
    "backward": "backward finite difference",
}

explanation_col1, explanation_col2 = st.columns(2, gap="small")

with explanation_col1:
    st.markdown("##### What is held fixed?")
    other_parameters = [
        name
        for name in PARAMETER_NAMES
        if name != selected_parameter
    ]

    st.markdown(
        load_dynamic_md(
            "md_local_03_fixed.md",
            {
                "[[PARAMETER]]": selected_parameter,
                "[[X1]]": f"{x1:.2f}",
                "[[X2]]": f"{x2:.2f}",
                "[[X3]]": f"{x3:.2f}",
            },
        )
    )

with explanation_col2:
    st.markdown("##### How is the local slope estimated?")

    st.markdown(
        load_dynamic_md(
            "md_local_03_slope.md",
            {
                "[[PARAMETER]]": selected_parameter,
                "[[REFERENCE_VALUE]]": f"{selected_reference_value:.2f}",
                "[[METHOD]]": method_labels[difference_details["method"]],
                "[[X_A]]": f"{difference_details['x_a']:.2f}",
                "[[X_B]]": f"{difference_details['x_b']:.2f}",
                "[[INDEX]]": selected_parameter[-1],
                "[[SLOPE]]": f"{difference_details['slope']:.3f}",
            },
        )
    )

difference_caption_files = {
    "central": "md_local_03_central.md",
    "forward": "md_local_03_forward.md",
    "backward": "md_local_03_backward.md",
}

st.caption(
    load_md(
        MD_DIR,
        difference_caption_files[difference_details["method"]],
        LANGUAGE,
    )
)

st.info(load_md(MD_DIR, "md_local_03.md", LANGUAGE))

if selected_parameter == "x3" and abs(x3 - 0.5) <= 0.02:
    st.warning(load_md(MD_DIR, "md_local_04.md", LANGUAGE))

st.subheader("🎯 :blue[Main take-home messages]", divider="blue")
st.markdown(load_md(MD_DIR, "md_local_05.md", LANGUAGE))

st.subheader("📖 :blue[Further learning material]", divider="blue")
st.markdown(load_md(MD_DIR, "md_local_06.md", LANGUAGE))


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
    st.image(str(IMAGE_DIR / "CC_BY-SA_icon.png"))

