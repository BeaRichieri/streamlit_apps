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
index_symbols = ["¹", "²", "³"]

author_list = [
    f"{name}{''.join(index_symbols[i - 1] for i in indices)}"
    for name, indices in authors.items()
]
institution_list = [
    f"{index_symbols[i - 1]} {institution}"
    for i, institution in institutions.items()
]
institution_text = " | ".join(institution_list)

st.header(":rainbow[Welcome to the course]", divider="gray")
st.subheader("Wavelet decomposition of time series")

st.markdown(
    """
This interactive module introduces **wavelet decomposition** through a synthetic
time-series example.

You will build a signal containing processes at different time scales, apply a
discrete wavelet transform, inspect approximation and detail components, and
reconstruct the signal from selected scales.

The emphasis is on **learning by exploration** rather than on treating the
wavelet transform as a black box.
"""
)

st.info(
    "Open **Wavelet decomposition** from the sidebar to start the interactive tutorial."
)

st.write("")
st.write("")

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
