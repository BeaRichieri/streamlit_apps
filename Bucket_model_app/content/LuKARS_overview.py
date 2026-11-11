#### ADD LOGO

from pathlib import Path

import streamlit as st

from app_utils import load_md


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
# Page title and introduction
# -----------------------------------------------------------------------------
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    st.image(
        IMAGE_DIR/"LuKARS3_logo.jpg",
        use_container_width=True,
    )
    

st.markdown(
    load_md(
        MD_DIR,
        "md_lukars_overview_01.md",
        LANGUAGE,
    )
)


# -----------------------------------------------------------------------------
# Purpose
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[Purpose of the educational platform]",
    divider="blue",
)

st.markdown(
    load_md(
        MD_DIR,
        "md_lukars_overview_02.md",
        LANGUAGE,
    )
)


# -----------------------------------------------------------------------------
# Main learning dimensions
# -----------------------------------------------------------------------------
col1, col2, col3 = st.columns([1, 20, 1])
with col2:
    st.image(
        IMAGE_DIR/"educational_purposes_1.png",
       # caption="General workflow of a conceptual hydrological model",
        use_container_width=True,
    )
    


# -----------------------------------------------------------------------------
# Learning objectives
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[Learning objectives]",
    divider="blue",
)

st.markdown(
    load_md(
        MD_DIR,
        "md_lukars_overview_06.md",
        LANGUAGE,
    )
)


# -----------------------------------------------------------------------------
# App organization
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[How the LuKARS section is organised]",
    divider="blue",
)

st.markdown(
    load_md(
        MD_DIR,
        "md_lukars_overview_07.md",
        LANGUAGE,
    )
)


col1, col2, col3 = st.columns([1, 20, 1])
with col2:
    st.image(
        IMAGE_DIR/"LuKARS_learning_path_1.png",
       # caption="General workflow of a conceptual hydrological model",
        use_container_width=True,
    )
    

# -----------------------------------------------------------------------------
# Suggested learning path
# -----------------------------------------------------------------------------
st.subheader(
    ":blue[Suggested learning path]",
    divider="blue",
)

st.markdown(
    load_md(
        MD_DIR,
        "md_lukars_overview_08.md",
        LANGUAGE,
    )
)

with st.expander("Show course-use recommendations"):
    st.markdown(
        load_md(
            MD_DIR,
            "md_lukars_overview_09.md",
            LANGUAGE,
        )
    )


# -----------------------------------------------------------------------------
# Key message
# -----------------------------------------------------------------------------
st.info(
    """
Use the sidebar to continue with **Model description** before starting one
of the interactive case studies.
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
    st.image(IMAGE_DIR/"CC_BY-SA_icon.png")
