import json
from pathlib import Path

import streamlit as st
from streamlit_book import multiple_choice

from app_utils import load_md, render_toggle_container

import matplotlib.pyplot as plt
import numpy as np


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
# Fixed axis limits for the two interactive reservoir plots.
# Keeping these limits constant makes parameter-response comparisons easier.
STEADY_STORAGE_XLIM = (0.0, 300.0)
STEADY_FLUX_YLIM = (-3.0, 20.0)

UNSTEADY_TIME_XLIM = (0.0, 60.0)
UNSTEADY_FLUX_YLIM = (0.0, 16.0)
UNSTEADY_STORAGE_YLIM = (0.0, 60.0)



# -----------------------------------------------------------------------------
# Assessment renderer for the established iNUX JSON structure
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
# Markdown page content
# -----------------------------------------------------------------------------
st.markdown(load_md(MD_DIR, "md_lumped_01.md", LANGUAGE))

st.subheader(":blue[Two approaches to hydrological modelling]", divider="blue")
st.markdown(load_md(MD_DIR, "md_lumped_02.md", LANGUAGE))

distributed_col, conceptual_col = st.columns(2, gap="small")

with distributed_col:
    with st.container(border=True):
        st.markdown("#### 🗺️ Distributed models")

        st.image(
            IMAGE_DIR/"distributed_model.png",
            caption=(
                "Example of the spatial distribution of groundwater depth "
                "simulated with a distributed model."
            ),
            use_container_width=True,
        )

        st.markdown(load_md(MD_DIR, "md_lumped_03.md", LANGUAGE))

        with st.expander("Show more"):
            st.markdown(
                load_md(
                    MD_DIR,
                    "md_lumped_03_more.md",
                    LANGUAGE,
                )
            )

with conceptual_col:
    with st.container(border=True):
        st.markdown("#### 🪣 Conceptual models")

        st.image(
            IMAGE_DIR/"conceptual_model1.png",
            caption=(
                "Example of a conceptual representation based on "
                "interconnected storage compartments."
            ),
            use_container_width=True,
        )

        st.markdown(load_md(MD_DIR, "md_lumped_04.md", LANGUAGE))

        with st.expander("Show more"):
            st.markdown(
                load_md(
                    MD_DIR,
                    "md_lumped_04_more.md",
                    LANGUAGE,
                )
            )

with st.expander("Show a detailed comparison"):
    st.markdown(load_md(MD_DIR, "md_lumped_05.md", LANGUAGE))

st.subheader(":blue[What is a conceptual hydrological model?]", divider="blue")
st.markdown(load_md(MD_DIR, "md_lumped_06.md", LANGUAGE))
col1, col2, col3 = st.columns([1, 20, 1])
with col2:
    st.image(
        IMAGE_DIR/"workflow_conceptual_model.png",
        caption="General workflow of a conceptual hydrological model",
        use_container_width=True,
    )
with st.expander("Show more"):
    st.markdown(load_md(MD_DIR, "md_lumped_06_more.md", LANGUAGE))
    

st.subheader(":blue[Fully lumped and semi-distributed models]", divider="blue")

lumped_col, semi_distributed_col = st.columns(2, gap="small")

with lumped_col:
    with st.container(border=True, height=450):
        st.markdown("### Fully lumped")
        st.markdown(load_md(MD_DIR, "md_lumped_07.md", LANGUAGE))

with semi_distributed_col:
    with st.container(border=True, height=450):
        st.markdown("### Semi-distributed")
        st.markdown(load_md(MD_DIR, "md_lumped_08.md", LANGUAGE))


st.subheader(":blue[Storage and discharge in a conceptual reservoir]", divider="blue")
st.markdown(load_md(MD_DIR, "md_lumped_09.md", LANGUAGE))

# -----------------------------------------------------------------------------
# Governing equations
# -----------------------------------------------------------------------------
with st.container(border=True):
    st.markdown("#### Governing equations")

    equation_col1, equation_col2 = st.columns(2, gap="small")

    with equation_col1:
        st.markdown("##### Water balance")

        st.latex(
            r"\frac{dS}{dt}=P-ET-Q"
        )

        st.caption(
            "Change in storage resulting from water input, "
            "evapotranspiration and discharge."
        )

    with equation_col2:
        st.markdown("##### Storage–discharge relationship")

        st.latex(
            r"Q=aS^b"
        )

        st.caption(
            "Relationship controlling how rapidly the reservoir drains."
        )

    with st.expander("Show symbols and parameter meanings"):
        symbol_col1, symbol_col2 = st.columns(2, gap="large")

        with symbol_col1:
            st.markdown(
                """
- $S$: reservoir storage
- $P$: precipitation or water input
- $ET$: evapotranspiration
- $Q$: discharge
"""
            )

        with symbol_col2:
            st.markdown(
                """
- $a$: parameter controlling overall discharge
- $b$: dimensionless nonlinearity parameter
- $b=1$: linear reservoir
- $b>1$: nonlinear reservoir response
"""
            )
        
# -------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Interactive reservoir visualisations
# -----------------------------------------------------------------------------
st.markdown("### Explore the reservoir equations")

st.markdown(
    """
Start with the steady-state relationship between storage and discharge.
Then explore how the reservoir responds dynamically to synthetic
precipitation events.
"""
)

st.markdown(
    """
**Illustrative units used in the visualisations:**  
Storage is expressed in **mm**, time in **days**, and precipitation,
evapotranspiration and discharge in **mm day⁻¹**.
"""
)

with st.expander("Show dimensions and parameter units"):
    st.markdown(
        r"""
- **Storage:** $[S]=L$, expressed here in $\mathrm{mm}$

- **Precipitation, evapotranspiration and discharge:**

  $[P]=[ET]=[Q]=LT^{-1}$

  expressed here in $\mathrm{mm\,day^{-1}}$

- **Time:** $[t]=T$, expressed here in days

- **Nonlinearity parameter:** $[b]=1$

  Therefore, $b$ is dimensionless.

- **Discharge parameter:**

  $[a]=L^{1-b}T^{-1}$

  With the units used here:

  $[a]=\mathrm{mm}^{1-b}\,\mathrm{day}^{-1}$

For the linear case, $b=1$, the dimensions of the discharge parameter
reduce to $[a]=T^{-1}$.
"""
    )

# -----------------------------------------------------------------------------
# Guided tutorial for the interactive plots
# -----------------------------------------------------------------------------
def show_latex_values(*expressions: str) -> None:
    """Display multiple LaTeX expressions in separate Streamlit columns."""
    value_columns = st.columns(len(expressions), gap="small")

    for column, expression in zip(value_columns, expressions):
        with column:
            st.latex(expression)


def show_tutorial_answers(
    key: str,
    answers: list[tuple[str, str]],
) -> None:
    """Display optional suggested answers for one tutorial experiment."""
    show_answers = st.toggle(
        "💡 Show suggested answers",
        key=f"{key}_show_answers",
    )

    if show_answers:
        with st.container(border=True):
            st.markdown("#### Suggested answers")

            for question, answer in answers:
                st.markdown(f"**{question}**")
                st.markdown(answer)



def lumped_tutorial_url(tutorial: str) -> str:
    """Build a URL for a standalone reservoir-tutorial browser tab."""
    return f"./?lumped_tutorial={tutorial}"


@st.fragment
def render_reservoir_interactions() -> None:
    with st.expander(
        "🎓 Guided tutorial: explore the reservoir behaviour",
        expanded=False,
    ):
        st.markdown(
            """
Use the experiments below to investigate the behaviour of the conceptual
reservoir.

Modify the sliders directly in the corresponding interactive plot.
For a clear comparison, change **only one parameter at a time** and
observe how the result changes.

Try to answer each question before opening the suggested answers.
"""
        )

        tutorial_link_col1, tutorial_link_col2 = st.columns(2)

        with tutorial_link_col1:
            st.link_button(
                "↗ Open steady-state tutorial separately",
                lumped_tutorial_url("steady"),
                use_container_width=True,
                help=(
                    "Open the steady-state tutorial in a new browser tab so "
                    "you can keep it next to the interactive graph."
                ),
            )

        with tutorial_link_col2:
            st.link_button(
                "↗ Open unsteady-state tutorial separately",
                lumped_tutorial_url("unsteady"),
                use_container_width=True,
                help=(
                    "Open the unsteady-state tutorial in a new browser tab so "
                    "you can keep it next to the interactive graph."
                ),
            )

        steady_tutorial_tab, unsteady_tutorial_tab = st.tabs(
            [
                "1. Steady-state experiments",
                "2. Unsteady-state experiments",
            ]
        )

        # =========================================================================
        # STEADY-STATE TUTORIAL
        # =========================================================================
        with steady_tutorial_tab:
            # ---------------------------------------------------------------------
            # Experiment 1
            # ---------------------------------------------------------------------
            st.markdown("### Experiment 1 — Linear reservoir")

            st.markdown(
                "In the steady-state plot, begin with approximately:"
            )

            show_latex_values(
                r"a = 0.010",
                r"b = 1.0",
            )

            show_latex_values(
                r"P = 1.5\ \mathrm{mm\,day^{-1}}",
                r"ET = 0.3\ \mathrm{mm\,day^{-1}}",
            )

            st.markdown(
                """
Observe the shape of the storage–discharge curve and the position of
the equilibrium point.

**Questions**

- What is the shape of the discharge curve when **b = 1**?
- At which point does discharge equal the net input **P − ET**?
- What does this intersection represent physically?
"""
            )

            show_tutorial_answers(
                key="steady_experiment_1",
                answers=[
                    (
                        "What is the shape of the discharge curve when b = 1?",
                        (
                            "The relationship is linear. Discharge increases in "
                            "direct proportion to storage, so the "
                            "storage–discharge relationship is represented by a "
                            "straight line."
                        ),
                    ),
                    (
                        "At which point does discharge equal the net input P − ET?",
                        (
                            "Discharge equals the net input at the intersection "
                            "between the storage–discharge curve and the horizontal "
                            "net-input line."
                        ),
                    ),
                    (
                        "What does this intersection represent physically?",
                        (
                            "It represents the steady-state equilibrium. At this "
                            "point, the amount of water entering the reservoir "
                            "equals the amount leaving it, so storage no longer "
                            "changes."
                        ),
                    ),
                ],
            )

            st.divider()

            # ---------------------------------------------------------------------
            # Experiment 2
            # ---------------------------------------------------------------------
            st.markdown("### Experiment 2 — Increase the nonlinearity")

            st.markdown(
                "Keep **a**, **P** and **ET** unchanged, but gradually "
                "increase **b**:"
            )

            st.latex(
                r"b = 1.0 \rightarrow 1.5 \rightarrow 2.0"
            )

            st.markdown(
                """
Observe:

- how the shape of the discharge curve changes;
- how discharge behaves at low storage;
- how discharge behaves at high storage;
- how the equilibrium storage changes.

**Questions**

- Why does discharge become more sensitive to storage when **b > 1**?
- How does the position of the equilibrium point change?
"""
            )

            show_tutorial_answers(
                key="steady_experiment_2",
                answers=[
                    (
                        "Why does discharge become more sensitive to storage "
                        "when b > 1?",
                        (
                            "Because storage is raised to a power greater than "
                            "one. At high storage, an additional increase in "
                            "storage therefore produces a relatively large "
                            "increase in discharge."
                        ),
                    ),
                    (
                        "How does the position of the equilibrium point change?",
                        (
                            "The equilibrium point follows the intersection "
                            "between the modified discharge curve and the unchanged "
                            "net-input line. Its exact movement depends on the "
                            "selected value of b and on the numerical value and "
                            "units of a."
                        ),
                    ),
                ],
            )

            st.divider()

            # ---------------------------------------------------------------------
            # Experiment 3
            # ---------------------------------------------------------------------
            st.markdown("### Experiment 3 — Change the discharge parameter")

            st.markdown(
                "Set **b = 1.0** again and compare different values of **a**:"
            )

            show_latex_values(
                r"a = 0.005",
                r"a = 0.010",
                r"a = 0.030",
            )

            st.markdown(
                """
Keep precipitation and evapotranspiration constant.

Observe:

- how the discharge curve moves;
- how the equilibrium point moves;
- whether the equilibrium storage increases or decreases.

**Questions**

- What happens to the discharge curve when **a** increases?
- Does the equilibrium storage increase or decrease?
- Which reservoir drains more rapidly?
"""
            )

            show_tutorial_answers(
                key="steady_experiment_3",
                answers=[
                    (
                        "What happens to the discharge curve when a increases?",
                        (
                            "The discharge curve moves upward. For the same "
                            "storage, the reservoir produces a larger discharge."
                        ),
                    ),
                    (
                        "Does the equilibrium storage increase or decrease?",
                        (
                            "It decreases. A reservoir with a larger discharge "
                            "parameter requires less storage to release the same "
                            "net water input."
                        ),
                    ),
                    (
                        "Which reservoir drains more rapidly?",
                        (
                            "The reservoir with the larger value of a drains more "
                            "rapidly."
                        ),
                    ),
                ],
            )

            st.divider()

            # ---------------------------------------------------------------------
            # Experiment 4
            # ---------------------------------------------------------------------
            st.markdown("### Experiment 4 — Change the net water input")

            st.markdown(
                """
Keep **a** and **b** constant.

First increase precipitation **P**, and then increase
evapotranspiration **ET**.

Observe how the horizontal line representing the net input **P − ET**
moves.

**Questions**

- What happens to equilibrium storage when precipitation increases?
- What happens when evapotranspiration increases?
- What does the model predict when **P ≤ ET**?
"""
            )

            show_tutorial_answers(
                key="steady_experiment_4",
                answers=[
                    (
                        "What happens to equilibrium storage when precipitation "
                        "increases?",
                        (
                            "The net input increases, so the horizontal line moves "
                            "upward. A higher storage is generally required for "
                            "discharge to equal the larger net input."
                        ),
                    ),
                    (
                        "What happens when evapotranspiration increases?",
                        (
                            "The net input decreases, so the horizontal line moves "
                            "downward and the equilibrium storage decreases."
                        ),
                    ),
                    (
                        "What does the model predict when P ≤ ET?",
                        (
                            "There is no positive net input available to maintain "
                            "storage. Without another source of water, the reservoir "
                            "progressively empties."
                        ),
                    ),
                ],
            )

        # =========================================================================
        # UNSTEADY-STATE TUTORIAL
        # =========================================================================
        with unsteady_tutorial_tab:
            # ---------------------------------------------------------------------
            # Experiment 1
            # ---------------------------------------------------------------------
            st.markdown(
                "### Experiment 1 — Response to one precipitation event"
            )

            st.markdown(
                "Select **Single precipitation event** and begin with "
                "approximately:"
            )

            show_latex_values(
                r"P_{\max} = 8\ \mathrm{mm\,day^{-1}}",
                r"S_0 = 5\ \mathrm{mm}",
            )

            show_latex_values(
                r"a = 0.010",
                r"b = 1.0",
                r"ET = 0.3\ \mathrm{mm\,day^{-1}}",
            )

            st.markdown(
                """
Observe the sequence of changes in precipitation, storage and
discharge.

**Questions**

- Does storage respond immediately to precipitation?
- When does discharge begin to increase?
- Is maximum discharge reached before, during or after the precipitation
  maximum?
- What happens after precipitation stops?
"""
            )

            show_tutorial_answers(
                key="unsteady_experiment_1",
                answers=[
                    (
                        "Does storage respond immediately to precipitation?",
                        (
                            "Yes. Precipitation immediately adds water to the "
                            "reservoir. Storage increases when the input exceeds "
                            "the combined losses through evapotranspiration and "
                            "discharge."
                        ),
                    ),
                    (
                        "When does discharge begin to increase?",
                        (
                            "Discharge begins to increase as soon as storage rises "
                            "because it is calculated from the current storage."
                        ),
                    ),
                    (
                        "When is maximum discharge reached relative to maximum "
                        "precipitation?",
                        (
                            "Maximum discharge is generally delayed relative to "
                            "maximum precipitation because precipitation must first "
                            "increase reservoir storage."
                        ),
                    ),
                    (
                        "What happens after precipitation stops?",
                        (
                            "Storage decreases because water continues to leave "
                            "through discharge and evapotranspiration. Discharge "
                            "therefore declines during the recession."
                        ),
                    ),
                ],
            )

            st.divider()

            # ---------------------------------------------------------------------
            # Experiment 2
            # ---------------------------------------------------------------------
            st.markdown("### Experiment 2 — Slow and fast drainage")

            st.markdown(
                "Keep all other values unchanged and compare:"
            )

            show_latex_values(
                r"a = 0.005",
                r"a = 0.010",
                r"a = 0.030",
            )

            st.markdown(
                """
Observe:

- the maximum storage;
- the maximum discharge;
- the duration of the recession;
- the time required for the reservoir to empty.

**Questions**

- Which value of **a** produces the highest storage?
- Which value produces the strongest discharge response?
- Which reservoir retains water for the longest time?
"""
            )

            show_tutorial_answers(
                key="unsteady_experiment_2",
                answers=[
                    (
                        "Which value of a produces the highest storage?",
                        (
                            "The smallest value of a generally produces the highest "
                            "storage because water is released more slowly."
                        ),
                    ),
                    (
                        "Which value produces the strongest discharge response?",
                        (
                            "The largest value of a produces a stronger and more "
                            "rapid discharge response for the same storage."
                        ),
                    ),
                    (
                        "Which reservoir retains water for the longest time?",
                        (
                            "The reservoir with the smallest value of a retains "
                            "water for the longest time and has the slowest "
                            "recession."
                        ),
                    ),
                ],
            )

            st.divider()

            # ---------------------------------------------------------------------
            # Experiment 3
            # ---------------------------------------------------------------------
            st.markdown("### Experiment 3 — Linear and nonlinear response")

            st.markdown(
                "Return to **a = 0.010** and gradually increase **b**:"
            )

            st.latex(
                r"b = 1.0 \rightarrow 1.5 \rightarrow 2.0"
            )

            st.markdown(
                """
Observe how the discharge response changes during both the rising and
falling parts of the event.

**Questions**

- How does increasing **b** affect discharge when storage is low?
- How does it affect discharge when storage is high?
- Does the nonlinear reservoir produce a sharper discharge peak?
"""
            )

            show_tutorial_answers(
                key="unsteady_experiment_3",
                answers=[
                    (
                        "How does increasing b affect discharge when storage is "
                        "low?",
                        (
                            "For the values used in this demonstration, discharge "
                            "can remain relatively weak at low storage when the "
                            "response is strongly nonlinear."
                        ),
                    ),
                    (
                        "How does increasing b affect discharge when storage is "
                        "high?",
                        (
                            "Discharge increases much more rapidly at high storage "
                            "because storage is raised to a larger exponent."
                        ),
                    ),
                    (
                        "Does the nonlinear reservoir produce a sharper discharge "
                        "peak?",
                        (
                            "It can produce a sharper response when storage becomes "
                            "high. The exact comparison also depends on the selected "
                            "value and units of a."
                        ),
                    ),
                ],
            )

            st.divider()

            # ---------------------------------------------------------------------
            # Experiment 4
            # ---------------------------------------------------------------------
            st.markdown("### Experiment 4 — Antecedent storage")

            st.markdown(
                """
Keep the precipitation scenario and model parameters constant, but
compare different initial storage values:
"""
            )

            show_latex_values(
                r"S_0 = 0\ \mathrm{mm}",
                r"S_0 = 5\ \mathrm{mm}",
                r"S_0 = 15\ \mathrm{mm}",
            )

            st.markdown(
                """
**Questions**

- How does initial storage influence peak discharge?
- Does a wet reservoir respond differently from an initially empty one?
- Why is antecedent storage important when modelling flood response?
"""
            )

            show_tutorial_answers(
                key="unsteady_experiment_4",
                answers=[
                    (
                        "How does initial storage influence peak discharge?",
                        (
                            "Higher initial storage generally produces a larger "
                            "and earlier discharge response because the reservoir "
                            "already contains water when precipitation begins."
                        ),
                    ),
                    (
                        "Does a wet reservoir respond differently from an empty "
                        "one?",
                        (
                            "Yes. A wet reservoir requires less additional "
                            "precipitation to reach storage levels associated with "
                            "high discharge."
                        ),
                    ),
                    (
                        "Why is antecedent storage important when modelling flood "
                        "response?",
                        (
                            "It represents the wetness of the system before an "
                            "event. The same precipitation event can therefore "
                            "produce very different responses under dry and wet "
                            "conditions."
                        ),
                    ),
                ],
            )

            st.divider()

            # ---------------------------------------------------------------------
            # Experiment 5
            # ---------------------------------------------------------------------
            st.markdown("### Experiment 5 — Multiple precipitation events")

            st.markdown(
                """
Compare the following synthetic precipitation scenarios:

- **Single precipitation event**
- **Two precipitation events**
- **Repeated precipitation events**

Keep **a**, **b**, **ET** and the maximum precipitation rate unchanged.

Observe whether the reservoir has enough time to drain between
precipitation events.

**Questions**

- What happens when a new precipitation event occurs while storage is
  still elevated?
- Does the second event generate the same discharge peak as the first?
- Under which conditions does storage accumulate between events?
"""
            )

            show_tutorial_answers(
                key="unsteady_experiment_5",
                answers=[
                    (
                        "What happens when a new precipitation event occurs while "
                        "storage is still elevated?",
                        (
                            "The new precipitation is added to an already wet "
                            "reservoir, so storage and discharge can rise more "
                            "rapidly."
                        ),
                    ),
                    (
                        "Does the second event generate the same discharge peak "
                        "as the first?",
                        (
                            "Not necessarily. If the reservoir has not drained "
                            "completely, the second event can generate a larger "
                            "discharge peak even when its precipitation intensity "
                            "is similar."
                        ),
                    ),
                    (
                        "Under which conditions does storage accumulate between "
                        "events?",
                        (
                            "Storage accumulates when the time between events is "
                            "too short for discharge and evapotranspiration to "
                            "remove the previously stored water."
                        ),
                    ),
                ],
            )

        st.info(
            "Tip: change one control at a time. Before moving a slider, predict "
            "how the storage or discharge curve should respond, and then compare "
            "your prediction with the plotted result."
        )
    
    # =============================================================================
    # 1. STEADY-STATE STORAGE–DISCHARGE RELATIONSHIP
    # =============================================================================
    with st.container(border=True):
        st.markdown("#### 1. Steady-state storage–discharge relationship")

        st.markdown(
            "At steady state, the amount of water stored in the reservoir "
            "does not change:"
        )

        st.latex(r"\frac{dS}{dt}=0")

        st.markdown("The water balance therefore becomes:")

        st.latex(r"P-ET=Q=aS^b")

        st.markdown(
            """
The intersection between the net input $P-ET$ and the discharge curve
represents the equilibrium storage.
"""
        )

        steady_control_col1, steady_control_col2 = st.columns(2)

        with steady_control_col1:
            steady_parameter_a = st.slider(
                "Discharge parameter a",
                min_value=0.001,
                max_value=0.050,
                value=0.010,
                step=0.001,
                format="%.3f",
                key="steady_parameter_a",
                help=(
                    "The dimensions of a are L^(1-b) T^(-1). "
                    "With the units used here, a is expressed as "
                    "mm^(1-b) day^(-1)."
                ),
            )

            steady_parameter_b = st.slider(
                "Nonlinearity parameter b [-]",
                min_value=1.0,
                max_value=3.0,
                value=1.3,
                step=0.1,
                key="steady_parameter_b",
                help="The parameter b is dimensionless.",
            )

        with steady_control_col2:
            constant_precipitation = st.slider(
                "Constant precipitation P [mm day⁻¹]",
                min_value=0.0,
                max_value=5.0,
                value=1.5,
                step=0.1,
                key="steady_precipitation",
            )

            constant_et = st.slider(
                "Constant evapotranspiration ET [mm day⁻¹]",
                min_value=0.0,
                max_value=3.0,
                value=0.3,
                step=0.1,
                key="steady_evapotranspiration",
            )

        steady_a_exponent = 1.0 - steady_parameter_b

        st.markdown(
            rf"""
For the selected value $b={steady_parameter_b:.1f}$, the units of
$a$ are:

$$
[a]=\mathrm{{mm}}^{{{steady_a_exponent:.1f}}}
\mathrm{{day}}^{{-1}}
$$
"""
        )

        net_input = constant_precipitation - constant_et

        if net_input > 0:
            equilibrium_storage = (
                net_input / steady_parameter_a
            ) ** (1.0 / steady_parameter_b)

        else:
            equilibrium_storage = None

        storage_curve = np.linspace(
            STEADY_STORAGE_XLIM[0],
            STEADY_STORAGE_XLIM[1],
            300,
        )

        discharge_curve = (
            steady_parameter_a
            * storage_curve ** steady_parameter_b
        )

        steady_figure, steady_axis = plt.subplots(
            figsize=(9, 4.5)
        )

        steady_axis.plot(
            storage_curve,
            discharge_curve,
            linewidth=2.5,
            label=r"Discharge $Q=aS^b$",
        )

        steady_axis.axhline(
            net_input,
            linestyle="--",
            linewidth=2,
            label=r"Net input $P-ET$",
        )

        if equilibrium_storage is not None:
            equilibrium_discharge = net_input

            steady_axis.scatter(
                equilibrium_storage,
                equilibrium_discharge,
                s=80,
                zorder=3,
                label="Equilibrium",
            )

            steady_axis.annotate(
                (
                    "Equilibrium\n"
                    f"S = {equilibrium_storage:.2f} mm\n"
                    f"Q = {equilibrium_discharge:.2f} mm day⁻¹"
                ),
                xy=(
                    equilibrium_storage,
                    equilibrium_discharge,
                ),
                xytext=(12, 12),
                textcoords="offset points",
            )

        steady_axis.set_xlabel(r"Storage $S$ [mm]")

        steady_axis.set_ylabel(
            r"Discharge or net input [mm day$^{-1}$]"
        )

        steady_axis.set_xlim(*STEADY_STORAGE_XLIM)
        steady_axis.set_ylim(*STEADY_FLUX_YLIM)

        steady_axis.grid(alpha=0.25)
        steady_axis.legend()

        steady_figure.tight_layout()

        st.pyplot(
            steady_figure,
            use_container_width=True,
        )

        plt.close(steady_figure)

        if equilibrium_storage is not None:
            st.success(
                "At equilibrium, discharge equals the net input. "
                f"The equilibrium storage is approximately "
                f"{equilibrium_storage:.2f} mm."
            )

        else:
            st.info(
                "Because precipitation is lower than or equal to "
                "evapotranspiration, there is no positive equilibrium storage. "
                "The reservoir will progressively empty."
            )


    # Add space between the two visualisations
    st.markdown(
        "<div style='height: 25px;'></div>",
        unsafe_allow_html=True,
    )


    # =============================================================================
    # 2. UNSTEADY RESERVOIR RESPONSE
    # =============================================================================
    with st.container(border=True):
        st.markdown("#### 2. Unsteady reservoir response")

        st.markdown(
            """
Under unsteady conditions, precipitation, storage and discharge vary
over time:
"""
        )

        st.latex(r"\frac{dS}{dt}=P-ET-Q")

        st.markdown(
            """
At every time step, discharge is calculated from the current storage:
"""
        )

        st.latex(r"Q=aS^b")

        unsteady_control_col1, unsteady_control_col2 = st.columns(2)

        with unsteady_control_col1:
            rainfall_scenario = st.selectbox(
                "Synthetic precipitation scenario",
                [
                    "Single precipitation event",
                    "Two precipitation events",
                    "Repeated precipitation events",
                ],
                key="unsteady_rainfall_scenario",
            )

            rainfall_peak = st.slider(
                "Maximum precipitation rate [mm day⁻¹]",
                min_value=1.0,
                max_value=15.0,
                value=8.0,
                step=0.5,
                key="unsteady_rainfall_peak",
            )

            initial_storage = st.slider(
                "Initial storage S₀ [mm]",
                min_value=0.0,
                max_value=20.0,
                value=5.0,
                step=0.5,
                key="unsteady_initial_storage",
            )

        with unsteady_control_col2:
            unsteady_parameter_a = st.slider(
                "Discharge parameter a",
                min_value=0.001,
                max_value=0.050,
                value=0.010,
                step=0.001,
                format="%.3f",
                key="unsteady_parameter_a",
                help=(
                    "The dimensions of a are L^(1-b) T^(-1). "
                    "With the units used here, a is expressed as "
                    "mm^(1-b) day^(-1)."
                ),
            )

            unsteady_parameter_b = st.slider(
                "Nonlinearity parameter b [-]",
                min_value=1.0,
                max_value=3.0,
                value=1.3,
                step=0.1,
                key="unsteady_parameter_b",
                help="The parameter b is dimensionless.",
            )

            unsteady_et_rate = st.slider(
                "Evapotranspiration rate ET [mm day⁻¹]",
                min_value=0.0,
                max_value=1.5,
                value=0.3,
                step=0.1,
                key="unsteady_et_rate",
            )

        unsteady_a_exponent = 1.0 - unsteady_parameter_b

        st.markdown(
            rf"""
For the selected value $b={unsteady_parameter_b:.1f}$, the units of
$a$ are:

$$
[a]=\mathrm{{mm}}^{{{unsteady_a_exponent:.1f}}}
\mathrm{{day}}^{{-1}}
$$
"""
        )

        st.caption(
            "The values and precipitation events are synthetic. "
            "They are intended to demonstrate model behaviour rather than "
            "represent a calibrated reservoir."
        )

        # -------------------------------------------------------------------------
        # Synthetic precipitation
        # -------------------------------------------------------------------------
        simulation_duration = 60.0
        time_step = 0.1

        time = np.arange(
            0.0,
            simulation_duration + time_step,
            time_step,
        )

        def precipitation_event(
            time_values: np.ndarray,
            centre: float,
            width: float,
            peak: float,
        ) -> np.ndarray:
            """Create a smooth synthetic precipitation event."""
            return peak * np.exp(
                -0.5
                * ((time_values - centre) / width) ** 2
            )

        if rainfall_scenario == "Single precipitation event":
            precipitation = precipitation_event(
                time,
                centre=15.0,
                width=1.8,
                peak=rainfall_peak,
            )

        elif rainfall_scenario == "Two precipitation events":
            precipitation = (
                precipitation_event(
                    time,
                    centre=14.0,
                    width=1.8,
                    peak=0.7 * rainfall_peak,
                )
                + precipitation_event(
                    time,
                    centre=36.0,
                    width=2.5,
                    peak=rainfall_peak,
                )
            )

        else:
            precipitation = (
                precipitation_event(
                    time,
                    centre=10.0,
                    width=1.5,
                    peak=0.6 * rainfall_peak,
                )
                + precipitation_event(
                    time,
                    centre=25.0,
                    width=2.0,
                    peak=rainfall_peak,
                )
                + precipitation_event(
                    time,
                    centre=43.0,
                    width=1.8,
                    peak=0.8 * rainfall_peak,
                )
            )

        # -------------------------------------------------------------------------
        # Reservoir simulation
        # -------------------------------------------------------------------------
        storage = np.zeros_like(time)
        discharge = np.zeros_like(time)

        evapotranspiration = np.full_like(
            time,
            unsteady_et_rate,
        )

        storage[0] = initial_storage

        for index in range(len(time) - 1):
            discharge[index] = (
                unsteady_parameter_a
                * storage[index] ** unsteady_parameter_b
            )

            storage_change = (
                precipitation[index]
                - evapotranspiration[index]
                - discharge[index]
            )

            storage[index + 1] = max(
                0.0,
                storage[index]
                + storage_change * time_step,
            )

        discharge[-1] = (
            unsteady_parameter_a
            * storage[-1] ** unsteady_parameter_b
        )

        # -------------------------------------------------------------------------
        # Plot
        # -------------------------------------------------------------------------
        unsteady_figure, flux_axis = plt.subplots(
            figsize=(9, 4.5)
        )

        storage_axis = flux_axis.twinx()

        flux_axis.plot(
            time,
            precipitation,
            color="lightblue",
            linewidth=2,
            label=r"Precipitation $P$",
        )

        flux_axis.plot(
            time,
            evapotranspiration,
            linestyle=":",
            linewidth=2,
            label=r"Evapotranspiration $ET$",
        )

        flux_axis.plot(
            time,
            discharge,
            linestyle="--",
            linewidth=2,
            label=r"Discharge $Q$",
        )

        storage_axis.plot(
            time,
            storage,
            linewidth=2.5,
            label=r"Storage $S$",
        )

        flux_axis.set_xlabel(r"Time $t$ [days]")

        flux_axis.set_ylabel(
            r"Water flux [mm day$^{-1}$]"
        )

        storage_axis.set_ylabel(
            r"Storage $S$ [mm]"
        )

        flux_axis.set_xlim(*UNSTEADY_TIME_XLIM)
        flux_axis.set_ylim(*UNSTEADY_FLUX_YLIM)
        storage_axis.set_ylim(*UNSTEADY_STORAGE_YLIM)

        flux_axis.grid(alpha=0.25)

        flux_handles, flux_labels = (
            flux_axis.get_legend_handles_labels()
        )

        storage_handles, storage_labels = (
            storage_axis.get_legend_handles_labels()
        )

        flux_axis.legend(
            flux_handles + storage_handles,
            flux_labels + storage_labels,
            loc="upper right",
        )

        unsteady_figure.tight_layout()

        st.pyplot(
            unsteady_figure,
            use_container_width=True,
        )

        plt.close(unsteady_figure)

        st.success(
            r"""
The precipitation event first increases storage. As storage rises,
discharge also increases according to $Q=aS^b$. After the event,
discharge and evapotranspiration progressively empty the reservoir.
"""
        )




render_reservoir_interactions()

#--------------------------------------------------------------------
st.subheader(":blue[How complex should a conceptual model be?]", divider="blue")
st.markdown(load_md(MD_DIR, "md_lumped_10.md", LANGUAGE))
with st.expander("Show more"):
    st.markdown(load_md(MD_DIR, "md_lumped_11.md", LANGUAGE))


st.subheader(":blue[How are model parameters determined?]", divider="blue")
st.markdown(load_md(MD_DIR, "md_lumped_12.md", LANGUAGE))
with st.expander("Show more"):
    st.markdown(load_md(MD_DIR, "md_lumped_12_more.md", LANGUAGE))


st.subheader(":blue[Why do sensitivity and uncertainty matter?]", divider="blue")
st.markdown(load_md(MD_DIR, "md_lumped_13.md", LANGUAGE))
with st.expander("Show more"):
    st.markdown(load_md(MD_DIR, "md_lumped_13_more.md", LANGUAGE))


st.subheader(":blue[Why are conceptual models useful for karst systems?]", divider="blue")
st.markdown(load_md(MD_DIR, "md_lumped_14.md", LANGUAGE))
with st.expander("Show more"):
    st.markdown(load_md(MD_DIR, "md_lumped_14_more.md", LANGUAGE))



st.subheader("🎯 :blue[Main take-home messages]", divider="blue")
st.markdown(load_md(MD_DIR, "md_lumped_15.md", LANGUAGE))


st.subheader("❓ :blue[Check your understanding]", divider="blue")
st.markdown(load_md(MD_DIR, "md_lumped_16.md", LANGUAGE))

render_assessment_fragment(
    QUESTIONS_DIR/"lumped_models_ass.json",
    "lumped_models_self_assessment",
    "🧠 **Show the self-assessment**",
    default_open=False,
)


st.subheader("📖 :blue[Further learning material]", divider="blue")
st.markdown(load_md(MD_DIR, "md_lumped_17.md", LANGUAGE))


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
