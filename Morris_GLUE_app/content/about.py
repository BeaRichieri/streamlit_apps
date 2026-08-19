import streamlit as st
from streamlit_scroll_to_top import scroll_to_here

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

#---------- Track the current page
# PAGE_ID = "ABOUT"

#Do (optional) things/settings if the user comes from another page
# if "current_page" not in st.session_state:
    # st.session_state.current_page = PAGE_ID
# if st.session_state.current_page != PAGE_ID:
    # st.session_state.current_page = PAGE_ID
    
# ---------- Start the page with scrolling here
if st.session_state.scroll_to_top:
    scroll_to_here(0, key='top')
    st.session_state.scroll_to_top = False
#Empty space at the top
st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

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


# ------------------------------------------------------------
# Format authors
# ------------------------------------------------------------
author_list = []

for name, indices in authors.items():
    superscript = ",".join(str(i) for i in indices)
    author_list.append(f"{name}<sup>{superscript}</sup>")

# ------------------------------------------------------------
# Format institutions
# ------------------------------------------------------------
institution_list = []

for i, inst in institutions.items():
    institution_list.append(f"<sup>{i}</sup> {inst}")
institution_text = ", ".join(institution_list)

st.title('About')

st.subheader('Description', divider = 'blue')

st.markdown(
    """
    The Module **Introduction to sensitivity analysis and uncertainty analysis** includes interactive tools to facilitate the understanding of the Morris screening method and the GLUE method.
    """
)
st.subheader('Development', divider = 'blue')

st.markdown(
    """
    The Module **Introduction to sensitivity analysis and uncertainty analysis** was developed by Beatrice Richieri and Thomas Reimann as a Streamlit application and adapted to the interactive education format for Eurokarst 2026. 
    """
)


st.markdown('---')


# Render footer with logos
columns_lic = st.columns((1,1,1))
with columns_lic[0]:
    st.image(IMAGE_DIR/"eurokarst2026_black.png")
with columns_lic[2]:
    st.image(IMAGE_DIR/"fau-logo.jpg")
    
    
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
    st.image(IMAGE_DIR"CC_BY-SA_icon.png")
