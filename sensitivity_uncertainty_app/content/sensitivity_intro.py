import json
from pathlib import Path

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


PRE_ASSESSMENT_FILE = QUESTIONS_DIR / "sensitivity_intro_pre_ass.json"


def render_assessment(filename: Path) -> None:
    with filename.open("r", encoding="utf-8") as file:
        questions = json.load(file)

    for start_index in range(0, len(questions), 2):
        columns = st.columns(2)
        for column, question_data in zip(columns, questions[start_index:start_index + 2]):
            with column:
                multiple_choice(
                    question=question_data["question"],
                    options_dict=question_data["options"],
                    success=question_data.get("success", "✅ Correct."),
                    error=question_data.get("error", "❌ Not quite."),
                )


import plotly.graph_objects as go


def parameter_space_sampling_figure(mode: str) -> go.Figure:
    """Small conceptual figure showing how the parameter space is sampled."""
    figure = go.Figure()

    # Delineate the full parameter space with a grey box.
    figure.add_shape(
        type="rect",
        x0=0.08, y0=0.12, x1=0.92, y1=0.86,
        line=dict(color="gray", width=1.2),
        fillcolor="rgba(240,240,240,0.25)",
    )

    point_size = 7

    if mode == "local":
        # Samples concentrated around one local reference region.
        local_points_x = [0.44, 0.50, 0.56, 0.50, 0.50]
        local_points_y = [0.49, 0.59, 0.49, 0.39, 0.49]

        figure.add_trace(
            go.Scatter(
                x=local_points_x,
                y=local_points_y,
                mode="markers",
                marker=dict(size=point_size),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    elif mode == "global":
        # Samples spread across the full parameter space.
        global_points_x = [0.16, 0.24, 0.34, 0.42, 0.50, 0.60, 0.70, 0.80, 0.36, 0.68]
        global_points_y = [0.32, 0.66, 0.47, 0.28, 0.58, 0.41, 0.74, 0.56, 0.78, 0.33]

        figure.add_trace(
            go.Scatter(
                x=global_points_x,
                y=global_points_y,
                mode="markers",
                marker=dict(size=point_size),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    figure.add_annotation(
        x=0.5,
        y=0.03,
        text="parameter space",
        showarrow=False,
        font=dict(size=10, color="gray"),
    )

    figure.update_layout(
        height=150,
        margin=dict(l=4, r=4, t=4, b=2),
        showlegend=False,
        xaxis=dict(
            range=[0, 1],
            visible=False,
            fixedrange=True,
        ),
        yaxis=dict(
            range=[0, 1],
            visible=False,
            fixedrange=True,
            scaleanchor="x",
            scaleratio=1,
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    return figure


def method_purpose_figure(mode: str) -> go.Figure:
    """Small conceptual figure showing screening/ranking vs variance quantification."""
    figure = go.Figure()

    if mode == "screening":
        parameter_names = ["x1", "x2", "x3", "x4"]
        importance = [0.85, 0.60, 0.28, 0.10]

        figure.add_trace(
            go.Bar(
                x=importance,
                y=parameter_names,
                orientation="h",
                hoverinfo="skip",
                showlegend=False,
            )
        )

        figure.add_annotation(
            x=0.50,
            y=1.10,
            xref="paper",
            yref="paper",
            text="rank influential parameters",
            showarrow=False,
            font=dict(size=10, color="gray"),
        )

        figure.update_xaxes(
            range=[0, 1.0],
            visible=False,
            fixedrange=True,
        )
        figure.update_yaxes(
            autorange="reversed",
            fixedrange=True,
        )

    elif mode == "variance":
        labels = ["x1", "x2", "x3", "interactions"]
        widths = [0.35, 0.15, 0.30, 0.20]
        colors = [
            "rgba(31,119,180,0.80)",
            "rgba(255,127,14,0.80)",
            "rgba(44,160,44,0.80)",
            "rgba(148,103,189,0.80)",
        ]

        start = 0.0
        for label, width, color in zip(labels, widths, colors):
            figure.add_shape(
                type="rect",
                x0=start,
                x1=start + width,
                y0=0.35,
                y1=0.65,
                line=dict(color="gray", width=1.0),
                fillcolor=color,
            )
            figure.add_annotation(
                x=start + width / 2.0,
                y=0.50,
                text=label,
                showarrow=False,
                font=dict(size=10, color="white"),
            )
            start += width

        figure.add_shape(
            type="rect",
            x0=0.0,
            x1=1.0,
            y0=0.35,
            y1=0.65,
            line=dict(color="gray", width=1.2),
            fillcolor="rgba(0,0,0,0)",
        )

        figure.add_annotation(
            x=0.50,
            y=0.92,
            xref="paper",
            yref="paper",
            text="quantify contributions to output variance",
            showarrow=False,
            font=dict(size=10, color="gray"),
        )

        figure.update_xaxes(
            range=[0, 1],
            visible=False,
            fixedrange=True,
        )
        figure.update_yaxes(
            range=[0, 1],
            visible=False,
            fixedrange=True,
        )

    figure.update_layout(
        height=150,
        margin=dict(l=10, r=10, t=8, b=4),
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    return figure


st.markdown(load_md(MD_DIR, "md_sa_intro_01.md", LANGUAGE))

st.subheader(":blue[Learning objectives]", divider="blue")
st.markdown(load_md(MD_DIR, "md_sa_intro_02.md", LANGUAGE))

st.subheader("🧭 :blue[Before we start]", divider="blue")
render_toggle_container(
    "sensitivity_intro_pre_assessment",
    "🧠 **Show the diagnostic assessment**",
    lambda: render_assessment(PRE_ASSESSMENT_FILE),
    default_open=False,
)

st.subheader(":blue[What is parameter sensitivity analysis?]", divider="blue")
st.markdown(load_md(MD_DIR, "md_sensitivity_06.md", LANGUAGE))

st.subheader(":blue[Forward and inverse modelling]", divider="blue")
st.markdown(load_md(MD_DIR, "md_sensitivity_04.md", LANGUAGE))

col1, col2, col3 = st.columns([1, 20, 1])
with col2:
    st.image(
        str(IMAGE_DIR / "forward_inverse_modeling.png"),
        caption="Forward and inverse modelling.",
        use_container_width=True,
    )

with st.expander("Why can inverse modelling be difficult?"):
    st.markdown(load_md(MD_DIR, "md_sensitivity_05.md", LANGUAGE))

st.subheader(":blue[How can sensitivity methods be organized?]", divider="blue")
st.markdown(load_md(MD_DIR, "md_sa_intro_03.md", LANGUAGE))

st.markdown("### Where in the parameter space is sensitivity evaluated?")
local_col, global_col = st.columns(2, gap="small")

with local_col:
    with st.container(border=True, height=500):
        st.plotly_chart(
            parameter_space_sampling_figure("local"),
            use_container_width=True,
            key="sa_intro_local_sampling",
            config={"displaylogo": False, "staticPlot": True},
        )

        st.markdown(
            load_md(
                MD_DIR,
                "md_sa_intro_04.md",
                LANGUAGE,
            )
        )

with global_col:
    with st.container(border=True, height=500):
        st.plotly_chart(
            parameter_space_sampling_figure("global"),
            use_container_width=True,
            key="sa_intro_global_sampling",
            config={"displaylogo": False, "staticPlot": True},
        )

        st.markdown(
            load_md(
                MD_DIR,
                "md_sa_intro_05.md",
                LANGUAGE,
            )
        )

st.markdown("### What information should the analysis provide?")
screen_col, sobol_col = st.columns(2, gap="small")

with screen_col:
    with st.container(border=True, height=430):
        st.plotly_chart(
            method_purpose_figure("screening"),
            use_container_width=True,
            key="sa_intro_screening_figure",
            config={"displaylogo": False, "staticPlot": True},
        )

        st.markdown(load_md(MD_DIR, "md_sa_intro_06.md", LANGUAGE))

with sobol_col:
    with st.container(border=True, height=430):
        st.plotly_chart(
            method_purpose_figure("variance"),
            use_container_width=True,
            key="sa_intro_variance_figure",
            config={"displaylogo": False, "staticPlot": True},
        )

        st.markdown(load_md(MD_DIR, "md_sa_intro_07.md", LANGUAGE))

st.markdown("### Method overview")
st.dataframe(
    {
        "Method": ["Local OAT", "Morris", "Sobol'"],
        "Scope": ["Local", "Global", "Global"],
        "Main result": [
            "Local derivative / response",
            "Screening and ranking",
            "Variance decomposition",
        ],
        "Computational cost": ["Low", "Moderate", "High"],
    },
    use_container_width=True,
    hide_index=True,
)

st.subheader("🎯 :blue[Main take-home messages]", divider="blue")
st.info(load_md(MD_DIR, "md_sa_intro_08.md", LANGUAGE))

st.subheader("📖 :blue[Further learning material]", divider="blue")
st.markdown(load_md(MD_DIR, "md_sa_intro_09.md", LANGUAGE))


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

