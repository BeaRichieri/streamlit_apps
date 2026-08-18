import streamlit as st
from pathlib import Path
from app_utils import load_md, render_toggle_container

# -----------------------------------------------------------------------------
# Fixed language and file locations
# -----------------------------------------------------------------------------
LANGUAGE = "en"
MD_DIR = Path("md")

st.session_state.language = LANGUAGE

# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
st.header(":rainbow[Welcome to the course]", divider = "gray")
st.subheader("Introduction to sensitivity analysis and uncertainty analysis")    

st.write("")

st.markdown(load_md(MD_DIR, "md_start_01.md", LANGUAGE))

st.write("")
st.write("")
st.write("")

# Render footer with logos
columns_lic = st.columns((1,1,1))
with columns_lic[0]:
    st.image('assets/images/eurokarst2026_black.png')
with columns_lic[2]:
    st.image('assets/images/fau-logo.jpg')
    
    
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
    st.image("assets/images/CC_BY-SA_icon.png")
