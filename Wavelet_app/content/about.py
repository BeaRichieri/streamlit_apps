import streamlit as st

LANGUAGE = "en"

BASE_DIR = st.session_state.BASE_DIR
CONTENT_DIR = st.session_state.CONTENT_DIR
ASSETS_DIR = st.session_state.ASSETS_DIR
IMAGE_DIR = st.session_state.IMAGE_DIR
MD_DIR = st.session_state.MD_DIR
QUESTIONS_DIR = st.session_state.QUESTIONS_DIR

st.session_state.language = LANGUAGE

year = 2026
authors = {
    "Beatrice Richieri": [1],
    "Thomas Reimann": [2],
}
institutions = {
    1: "FAU Erlangen",
    2: "TU Dresden",
}

author_list = []
for name, indices in authors.items():
    superscript = ",".join(str(i) for i in indices)
    author_list.append(f"{name}<sup>{superscript}</sup>")

institution_list = []
for index, institution in institutions.items():
    institution_list.append(f"<sup>{index}</sup> {institution}")
institution_text = ", ".join(institution_list)

st.title("About")

st.subheader("Description", divider="blue")
st.markdown(
    """
The module **Wavelet decomposition of time series** is an interactive teaching
application designed to introduce multi-scale time-series analysis using a
synthetic example.

The current version focuses on the **discrete wavelet transform (DWT)**,
including approximation and detail components, scale-dependent energy, and
signal reconstruction from selected wavelet levels.
"""
)

st.subheader("Development", divider="blue")
st.markdown(
    """
The module was developed as a Streamlit application by Beatrice Richieri and
Thomas Reimann and follows the same interactive educational format used in the
other course applications.
"""
)

st.markdown("---")

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
