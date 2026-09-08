from pathlib import Path

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


st.markdown(load_md(MD_DIR, "md_uncertainty_01.md", LANGUAGE))

st.subheader(":blue[Learning objectives]", divider="blue")
st.markdown(load_md(MD_DIR, "md_uncertainty_02.md", LANGUAGE))

st.subheader("🧭 :blue[Before we start]", divider="blue")
st.markdown(load_md(MD_DIR, "md_uncertainty_03.md", LANGUAGE))

intro_col1, intro_col2 = st.columns(2, gap="small")
with intro_col1:
    with st.container(border=True, height=320):
        st.markdown("### 📊 Sensitivity analysis")
        st.markdown(load_md(MD_DIR, "md_uncertainty_04.md", LANGUAGE))

with intro_col2:
    with st.container(border=True, height=320):
        st.markdown("### 🎲 Parameter uncertainty")
        st.markdown(load_md(MD_DIR, "md_uncertainty_05.md", LANGUAGE))

st.subheader(":blue[Where does model uncertainty come from?]", divider="blue")
st.markdown(load_md(MD_DIR, "md_uncertainty_06.md", LANGUAGE))

columns = st.columns(4, gap="small")
sources = [
    ("🌧️ Input", "uncertainty in forcing data and boundary conditions"),
    ("🎛️ Parameter", "unknown or poorly constrained parameter values"),
    ("🧩 Structure", "simplifications and alternative model concepts"),
    ("📏 Observation", "measurement and observation uncertainty"),
]
for column, (title, description) in zip(columns, sources):
    with column:
        with st.container(border=True, height=210):
            st.markdown(f"#### {title}")
            st.markdown(description)

st.info(load_md(MD_DIR, "md_uncertainty_07.md", LANGUAGE))

st.subheader(":blue[What is parameter uncertainty?]", divider="blue")
col1, col2, col3 = st.columns([1, 20, 1])
with col2:
    st.image(
        str(IMAGE_DIR / "ensamble_1.png"),
        use_container_width=True,
    )

st.subheader(
    ":blue[From parameter uncertainty to equifinality]",
    divider="blue",
)
st.info(
    load_md(
        MD_DIR,
        "md_ua_intro_equifinality_bridge.md",
        LANGUAGE,
    )
)

st.subheader("🎯 :blue[Main take-home messages]", divider="blue")
st.markdown(load_md(MD_DIR, "md_ua_intro_takehome.md", LANGUAGE))


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

