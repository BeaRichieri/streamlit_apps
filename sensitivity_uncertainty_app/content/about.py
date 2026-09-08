import streamlit as st
from pathlib import Path

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


st.title("About")

st.subheader("Description", divider="blue")
st.markdown(load_md(MD_DIR, "md_about_01.md", LANGUAGE))

st.subheader("Development", divider="blue")
st.markdown(load_md(MD_DIR, "md_about_02.md", LANGUAGE))

st.markdown("---")

columns_lic = st.columns((1, 1, 1))
with columns_lic[0]:
    st.image(str(IMAGE_DIR / "eurokarst2026_black.png"))
with columns_lic[2]:
    st.image(str(IMAGE_DIR / "fau-logo.jpg"))


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

