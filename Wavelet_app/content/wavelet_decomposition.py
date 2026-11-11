import json
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st

try:
    import pywt
except ImportError:
    pywt = None


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
# Assessment renderer
# -----------------------------------------------------------------------------
def render_assessment(filename: Path) -> None:
    """Render multiple-choice questions using native Streamlit components."""
    with filename.open("r", encoding="utf-8") as file:
        questions = json.load(file)

    for question_index, question_data in enumerate(questions):
        st.markdown(f"**{question_data['question']}**")

        options = list(question_data["options"].keys())
        answer = st.radio(
            "Choose one answer:",
            options,
            index=None,
            key=f"wavelet_assessment_{question_index}",
            label_visibility="collapsed",
        )

        if answer is not None:
            is_correct = bool(question_data["options"][answer])

            if is_correct:
                st.success(question_data.get("success", "✅ Correct."))
            else:
                st.error(question_data.get("error", "❌ Not quite."))

        if question_index < len(questions) - 1:
            st.markdown("---")


# -----------------------------------------------------------------------------
# Synthetic signal
# -----------------------------------------------------------------------------
def build_synthetic_signal(
    n_points: int,
    slow_period: float,
    medium_period: float,
    fast_period: float,
    slow_amplitude: float,
    medium_amplitude: float,
    fast_amplitude: float,
    noise_std: float,
    transient_strength: float,
):
    rng = np.random.default_rng(2026)
    t = np.arange(n_points, dtype=float)

    slow = slow_amplitude * np.sin(2.0 * np.pi * t / slow_period)
    medium = medium_amplitude * np.sin(2.0 * np.pi * t / medium_period)
    fast = fast_amplitude * np.sin(2.0 * np.pi * t / fast_period)

    center = 0.64 * n_points
    width = 0.075 * n_points
    envelope = np.exp(-0.5 * ((t - center) / width) ** 2)
    transient = transient_strength * envelope * np.sin(2.0 * np.pi * t / 8.0)

    noise = rng.normal(0.0, noise_std, size=n_points)
    signal = slow + medium + fast + transient + noise

    return t, signal, slow, medium, fast, transient, noise


def reconstruction_components(signal, wavelet_name, level):
    coeffs = pywt.wavedec(signal, wavelet_name, level=level, mode="symmetric")
    components = {}

    # Approximation at the coarsest selected level.
    coeff_list = [np.zeros_like(c) for c in coeffs]
    coeff_list[0] = coeffs[0]
    approx = pywt.waverec(coeff_list, wavelet_name, mode="symmetric")[: len(signal)]
    components[f"A{level}"] = approx

    # Details D_level ... D1.
    for detail_level in range(level, 0, -1):
        coeff_list = [np.zeros_like(c) for c in coeffs]
        coeff_index = level - detail_level + 1
        coeff_list[coeff_index] = coeffs[coeff_index]
        detail = pywt.waverec(coeff_list, wavelet_name, mode="symmetric")[: len(signal)]
        components[f"D{detail_level}"] = detail

    return coeffs, components


def energy_fraction(components):
    energies = {
        name: float(np.sum(values ** 2))
        for name, values in components.items()
    }
    total = sum(energies.values())
    if total <= 0:
        return {name: 0.0 for name in energies}
    return {name: value / total for name, value in energies.items()}


def add_line(fig, x, y, name, width=2.0, opacity=1.0, dash=None):
    line = dict(width=width)
    if dash is not None:
        line["dash"] = dash
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            name=name,
            opacity=opacity,
            line=line,
        )
    )


# -----------------------------------------------------------------------------
# Page title and overview
# -----------------------------------------------------------------------------
st.title("🌊 Wavelet decomposition of a time series")
st.markdown(
    """
Wavelet analysis allows us to describe a time series simultaneously in **time**
and **scale**. Instead of asking only *which frequencies are present?*, wavelets
also help us ask *when are processes at different time scales active?*

This tutorial introduces the idea through a synthetic signal whose components
are known in advance. We can therefore decompose the signal and check whether
the wavelet representation separates slow and fast variability as expected.
"""
)


# -----------------------------------------------------------------------------
# Learning objectives
# -----------------------------------------------------------------------------
st.subheader(":blue[Learning objectives]", divider="blue")
st.markdown(
    """
By the end of this page, you should be able to:

- explain why wavelets are useful for **non-stationary time series**;
- distinguish **approximation** and **detail** components in a discrete wavelet transform;
- understand how the decomposition level changes the time scale represented;
- reconstruct a signal from selected wavelet components;
- interpret the relative energy stored at different scales.
"""
)


# -----------------------------------------------------------------------------
# Before we start
# -----------------------------------------------------------------------------
st.subheader("🧭 :blue[Before we start]", divider="blue")

intro_col1, intro_col2 = st.columns(2, gap="small")
BOX_HEIGHT = 290

with intro_col1:
    with st.container(border=True, height=BOX_HEIGHT):
        st.markdown("### ⏱️ Time-domain view")
        st.markdown(
            """
A normal time-series plot tells us **how the signal changes through time**.
It is excellent for seeing events and trends, but different oscillatory
processes can overlap and be difficult to separate visually.
"""
        )

with intro_col2:
    with st.container(border=True, height=BOX_HEIGHT):
        st.markdown("### 🌊 Time-scale view")
        st.markdown(
            """
Wavelet decomposition separates variability into components associated with
different **scales**. Because the components remain localized in time, we can
also see when fast or slow behaviour is strongest.
"""
        )

st.info(
    "A wavelet decomposition is especially useful when the statistical behaviour "
    "of a signal changes through time, for example when short high-frequency events "
    "occur only during part of the record."
)


# -----------------------------------------------------------------------------
# Step 1: synthetic signal
# -----------------------------------------------------------------------------
st.subheader(":blue[Step 1 — Build a synthetic time series]", divider="blue")
st.markdown(
    """
We start from a signal composed of known processes:

- a **slow oscillation**;
- a **medium-scale oscillation**;
- a **fast oscillation**;
- a short **high-frequency transient event**;
- optional random noise.

Because we know the ingredients, this is a useful teaching example: after
decomposition we can compare the wavelet components with the processes that
were actually used to generate the signal.
"""
)

control_col, plot_col = st.columns([0.72, 1.55], gap="small")

with control_col:
    st.markdown("##### Synthetic signal settings")

    n_points = st.select_slider(
        "Number of time steps",
        options=[256, 512, 1024],
        value=512,
        key="wavelet_n_points",
    )

    slow_period = st.slider(
        "Slow period",
        80,
        220,
        160,
        10,
        key="wavelet_slow_period",
    )
    medium_period = st.slider(
        "Medium period",
        24,
        80,
        48,
        4,
        key="wavelet_medium_period",
    )
    fast_period = st.slider(
        "Fast period",
        4,
        24,
        12,
        2,
        key="wavelet_fast_period",
    )

    slow_amplitude = st.slider(
        "Slow amplitude",
        0.0,
        2.0,
        1.2,
        0.1,
        key="wavelet_slow_amp",
    )
    medium_amplitude = st.slider(
        "Medium amplitude",
        0.0,
        1.5,
        0.7,
        0.1,
        key="wavelet_medium_amp",
    )
    fast_amplitude = st.slider(
        "Fast amplitude",
        0.0,
        1.0,
        0.35,
        0.05,
        key="wavelet_fast_amp",
    )
    transient_strength = st.slider(
        "Transient strength",
        0.0,
        1.5,
        0.8,
        0.1,
        key="wavelet_transient_strength",
    )
    noise_std = st.slider(
        "Noise standard deviation",
        0.0,
        0.8,
        0.15,
        0.05,
        key="wavelet_noise",
    )

t, signal, slow, medium, fast, transient, noise = build_synthetic_signal(
    n_points=n_points,
    slow_period=slow_period,
    medium_period=medium_period,
    fast_period=fast_period,
    slow_amplitude=slow_amplitude,
    medium_amplitude=medium_amplitude,
    fast_amplitude=fast_amplitude,
    noise_std=noise_std,
    transient_strength=transient_strength,
)

with plot_col:
    st.markdown("##### Synthetic time series")
    fig_signal = go.Figure()
    add_line(fig_signal, t, signal, "Combined signal", width=2.5)
    fig_signal.update_layout(
        height=420,
        margin=dict(l=20, r=20, t=10, b=30),
        xaxis_title="Time step",
        yaxis_title="Signal value",
        hovermode="x unified",
    )
    st.plotly_chart(
        fig_signal,
        use_container_width=True,
        key="wavelet_signal",
        config={"displaylogo": False},
    )

with st.expander("Show the known components used to build the synthetic signal"):
    fig_components = go.Figure()
    add_line(fig_components, t, slow, "Slow component", width=2.0)
    add_line(fig_components, t, medium, "Medium component", width=2.0)
    add_line(fig_components, t, fast, "Fast component", width=2.0)
    add_line(fig_components, t, transient, "Transient event", width=2.0)
    fig_components.update_layout(
        height=420,
        margin=dict(l=20, r=20, t=10, b=30),
        xaxis_title="Time step",
        yaxis_title="Component value",
        hovermode="x unified",
        legend=dict(orientation="h", y=1.12),
    )
    st.plotly_chart(
        fig_components,
        use_container_width=True,
        key="wavelet_known_components",
        config={"displaylogo": False},
    )

st.info(
    "🧭 **Try it yourself:** increase the transient strength while keeping the "
    "background oscillations unchanged. Notice that the frequency content of the "
    "signal is no longer constant through time."
)


# -----------------------------------------------------------------------------
# Step 2: DWT concept
# -----------------------------------------------------------------------------
st.subheader(":blue[Step 2 — What does the discrete wavelet transform do?]", divider="blue")

st.markdown(
    """
At one decomposition step, the signal is passed through a pair of filters:

- a **low-pass filter**, which retains the smoother part of the signal;
- a **high-pass filter**, which retains the faster fluctuations.

The low-frequency result is called the **approximation** and the high-frequency
result is called the **detail**. The approximation can then be decomposed again.
"""
)

flow_col1, flow_col2, flow_col3 = st.columns(3, gap="small")
FLOW_HEIGHT = 215

with flow_col1:
    with st.container(border=True, height=FLOW_HEIGHT):
        st.markdown("### 1️⃣ Original signal")
        st.markdown("Contains variability at all represented time scales.")

with flow_col2:
    with st.container(border=True, height=FLOW_HEIGHT):
        st.markdown("### 2️⃣ Filter + downsample")
        st.markdown("Separate smoother and faster variability at the current level.")

with flow_col3:
    with st.container(border=True, height=FLOW_HEIGHT):
        st.markdown("### 3️⃣ Approximation + detail")
        st.markdown("Repeat the process on the approximation to reach coarser scales.")

st.latex(
    r"x(t) \longrightarrow A_1 + D_1"
    r"\longrightarrow A_2 + D_2 + D_1"
    r"\longrightarrow \cdots"
    r"\longrightarrow A_J + D_J+\cdots+D_1"
)

st.warning(
    "The level number is a **scale index**, not a frequency in physical units. "
    "For a regularly sampled series, higher decomposition levels correspond to "
    "progressively slower variability."
)


# -----------------------------------------------------------------------------
# Step 3: interactive decomposition
# -----------------------------------------------------------------------------
st.subheader(":blue[Step 3 — Decompose the synthetic signal]", divider="blue")

if pywt is None:
    st.error(
        "This page requires the `PyWavelets` package. Add `PyWavelets` to your "
        "requirements.txt file and reload the app."
    )
    st.stop()

wavelet_options = ["haar", "db2", "db4", "sym4", "coif1"]
settings_col, explanation_col = st.columns([0.9, 1.3], gap="small")

with settings_col:
    wavelet_name = st.selectbox(
        "Wavelet",
        wavelet_options,
        index=2,
        key="wavelet_family",
    )

    wavelet_obj = pywt.Wavelet(wavelet_name)
    maximum_level = pywt.dwt_max_level(len(signal), wavelet_obj.dec_len)
    allowed_max = max(1, min(maximum_level, 7))

    level = st.slider(
        "Decomposition level",
        min_value=1,
        max_value=allowed_max,
        value=min(5, allowed_max),
        step=1,
        key="wavelet_level",
    )

with explanation_col:
    st.markdown("##### How to read the selected decomposition")
    st.markdown(
        f"""
With **{wavelet_name}** and **{level} decomposition levels**, the signal is
represented by:

- one coarse approximation, **A{level}**;
- details **D{level}, D{level-1}, …, D1**.

**D1** contains the fastest variability represented by the transform, while
**D{level}** contains slower detail variability. **A{level}** is the smoothest
remaining component.
"""
    )

coeffs, components = reconstruction_components(signal, wavelet_name, level)
fractions = energy_fraction(components)

ordered_names = [f"A{level}"] + [f"D{i}" for i in range(level, 0, -1)]

st.markdown("##### Reconstructed wavelet components")

for name in ordered_names:
    fig = go.Figure()
    add_line(fig, t, components[name], name, width=2.0)
    fig.update_layout(
        height=190,
        margin=dict(l=20, r=20, t=5, b=25),
        xaxis_title="Time step" if name == ordered_names[-1] else None,
        yaxis_title=name,
        showlegend=False,
    )
    st.plotly_chart(
        fig,
        use_container_width=True,
        key=f"wavelet_component_{name}",
        config={"displaylogo": False},
    )

st.info(
    "🧭 **Explore the levels:** change the decomposition level and watch how "
    "variability is redistributed between the coarse approximation and the detail "
    "components. Then change the fast-period slider in Step 1 and identify which "
    "detail levels respond most strongly."
)


# -----------------------------------------------------------------------------
# Step 4: energy distribution
# -----------------------------------------------------------------------------
st.subheader(":blue[Step 4 — How much variability is stored at each scale?]", divider="blue")

st.markdown(
    """
A simple way to summarize the decomposition is to calculate the squared
amplitude of each reconstructed component. Here we show the fraction of total
reconstructed wavelet energy associated with each scale.

This is not a replacement for a formal spectral analysis, but it is useful for
seeing which scales dominate the synthetic example.
"""
)

energy_fig = go.Figure()
energy_fig.add_trace(
    go.Bar(
        x=ordered_names,
        y=[100.0 * fractions[name] for name in ordered_names],
        hovertemplate="%{x}<br>Energy fraction = %{y:.1f}%<extra></extra>",
    )
)
energy_fig.update_layout(
    height=360,
    margin=dict(l=20, r=20, t=10, b=30),
    xaxis_title="Wavelet component",
    yaxis_title="Energy fraction (%)",
    showlegend=False,
)
st.plotly_chart(
    energy_fig,
    use_container_width=True,
    key="wavelet_energy",
    config={"displaylogo": False},
)

dominant_component = max(fractions, key=fractions.get)
st.metric(
    "Largest reconstructed energy fraction",
    dominant_component,
    f"{100.0 * fractions[dominant_component]:.1f}%",
)


# -----------------------------------------------------------------------------
# Step 5: reconstruct from selected scales
# -----------------------------------------------------------------------------
st.subheader(":blue[Step 5 — Reconstruct the signal from selected scales]", divider="blue")

st.markdown(
    """
Because the wavelet transform is additive, we can reconstruct a new signal from
only the components we want to retain. This is one of the most useful practical
ideas behind wavelet analysis: we can isolate slow behaviour, emphasize events,
or remove high-frequency noise.
"""
)

selected_components = st.multiselect(
    "Components to include in the reconstruction",
    options=ordered_names,
    default=ordered_names,
    key="wavelet_selected_components",
)

if selected_components:
    reconstructed = np.sum(
        [components[name] for name in selected_components],
        axis=0,
    )
else:
    reconstructed = np.zeros_like(signal)

reconstruction_fig = go.Figure()
add_line(
    reconstruction_fig,
    t,
    signal,
    "Original signal",
    width=2.0,
    opacity=0.45,
)
add_line(
    reconstruction_fig,
    t,
    reconstructed,
    "Selected-scale reconstruction",
    width=2.7,
)
reconstruction_fig.update_layout(
    height=410,
    margin=dict(l=20, r=20, t=10, b=30),
    xaxis_title="Time step",
    yaxis_title="Signal value",
    hovermode="x unified",
    legend=dict(orientation="h", y=1.12),
)
st.plotly_chart(
    reconstruction_fig,
    use_container_width=True,
    key="wavelet_reconstruction",
    config={"displaylogo": False},
)

st.info(
    """
🧭 **Try three experiments**

1. Keep only **A** to obtain a smooth, low-frequency representation.
2. Remove **D1** and possibly **D2** to see a simple wavelet-denoising idea.
3. Keep only one or two **detail components** and identify where the transient
   event becomes visible.
"""
)


# -----------------------------------------------------------------------------
# Guided interpretation
# -----------------------------------------------------------------------------
st.subheader(":blue[Guided interpretation]", divider="blue")

with st.expander("Question 1 — Where should the fastest oscillations appear?"):
    st.markdown(
        """
They should appear mainly in the **lowest-level detail components**, especially
D1 and nearby levels. These components represent the finest scales resolved by
the selected wavelet decomposition.
"""
    )

with st.expander("Question 2 — Where should the slow oscillation appear?"):
    st.markdown(
        f"""
The slow component should be concentrated in the **coarse approximation A{level}**
and, depending on its period and the selected level, possibly in the highest
detail levels.
"""
    )

with st.expander("Question 3 — Why is the transient event especially interesting?"):
    st.markdown(
        """
Because it exists only during a limited part of the record. A Fourier spectrum
can show that high-frequency variability exists, but wavelet components retain
its **time localization**, so we can also see **when** that variability occurs.
"""
    )

with st.expander("Question 4 — Does one wavelet family always give the correct answer?"):
    st.markdown(
        """
No. The result depends on the selected wavelet, decomposition level, boundary
treatment, sampling interval, and the process being investigated. Wavelet
selection should therefore be treated as a modelling choice rather than a
purely cosmetic setting.
"""
    )


# -----------------------------------------------------------------------------
# Self-check
# -----------------------------------------------------------------------------
st.subheader("❓ :blue[Check your understanding]", divider="blue")
st.markdown(
    "Use these questions to check whether you understood the main concepts."
)

assessment_path = QUESTIONS_DIR / "wavelet_ass.json"
if assessment_path.exists():
    with st.expander("🧠 Show the self-assessment"):
        render_assessment(assessment_path)
else:
    st.caption(
        "Self-assessment file not found. Add `wavelet_ass.json` to the questions folder."
    )


# -----------------------------------------------------------------------------
# Take-home messages
# -----------------------------------------------------------------------------
st.subheader("🎯 :blue[Main take-home messages]", divider="blue")

st.markdown(
    """
- Wavelet decomposition separates a time series into **scale-dependent components**
  while preserving their location in time.
- The discrete wavelet transform produces **approximation** and **detail**
  coefficients recursively.
- **Low-level details** represent faster variability; **higher levels** represent
  progressively slower scales.
- The coarse approximation describes the smoothest part of the signal retained
  at the selected level.
- Because the signal can be reconstructed from selected components, wavelets are
  useful for **multi-scale interpretation, event isolation, and denoising**.
- Results depend on methodological choices such as the **wavelet family,
  decomposition level, and boundary treatment**.
"""
)


# -----------------------------------------------------------------------------
# Further learning material
# -----------------------------------------------------------------------------
st.subheader("📖 :blue[Further learning material]", divider="blue")

st.markdown(
    """
For deeper study:

- **Mallat, S. (1989).** A theory for multiresolution signal decomposition:
  the wavelet representation. *IEEE Transactions on Pattern Analysis and
  Machine Intelligence*, 11(7), 674–693.
- **Daubechies, I. (1992).** *Ten Lectures on Wavelets*. SIAM.
- **Percival, D. B. & Walden, A. T. (2000).** *Wavelet Methods for Time Series
  Analysis*. Cambridge University Press.
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
    icon_path = IMAGE_DIR / "CC_BY-SA_icon.png"
    if icon_path.exists():
        st.image(icon_path)
