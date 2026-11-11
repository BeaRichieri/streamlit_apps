import json
from pathlib import Path

import streamlit as st
from streamlit_book import multiple_choice

from app_utils import load_md, render_toggle_container


# Authors, institutions, and year
year = 2026 
authors = {
    "Beatrice Richieri": [1],  # Author 1 belongs to Institution 1
    "Thomas Reimann": [2]
}
institutions = {
    1: "FAU Erlangen",
    2: "TU Dresden"
}
index_symbols = ["¹", "²", "³", "⁴", "⁵", "⁶", "⁷", "⁸", "⁹"]
author_list = [f"{name}{''.join(index_symbols[i-1] for i in indices)}" for name, indices in authors.items()]
institution_list = [f"{index_symbols[i-1]} {inst}" for i, inst in institutions.items()]
institution_text = " | ".join(institution_list)  # Institutions in one line


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
st.markdown(load_md(MD_DIR, "md_intro_01.md", LANGUAGE))

st.subheader(":blue[Why karst matters?]", divider = "blue")

text_col, image_col = st.columns([2, 3], gap="large")
with text_col:
    st.markdown(load_md(MD_DIR, "md_intro_02.md", LANGUAGE))
with image_col:
    st.image(
        IMAGE_DIR/"intro_1.png",
        caption="Distribution of karst systems in Europe (Chen et al., 2017)",
        use_container_width=True,
    )
#col1, col2, col3 = st.columns([1, 3, 1])
#with col2:
 #   st.image(
  #      "assets/images/intro_1.png",
   #     caption=" Distribution in Europa of karst systems (Chen et al., 2017)",
   #     use_container_width=True,
   # )
with st.expander("Show more"):
    st.markdown(load_md(MD_DIR, "md_intro_03.md", LANGUAGE))

st.subheader(":blue[What is karst?]", divider = "blue")
st.markdown(load_md(MD_DIR, "md_intro_04.md", LANGUAGE))
img_col1, img_col2, img_col3 = st.columns(3, gap="medium")
with img_col1:
    st.image(
        IMAGE_DIR/"karst_photo1.png",
        caption="Karst outlet in the Triglav National Park, Slovenia",
        use_container_width=True,
    )
with img_col2:
    st.image(
        IMAGE_DIR/"karst_photo2.png",
        caption="Karst surface landforms in the Bavarian Alps, Germany",
        use_container_width=True,
    )
with img_col3:
    st.image(
        IMAGE_DIR/"karst_photo3.png",
        caption="Karst cave in the Pyrenees, France",
        use_container_width=True,
    )
with st.expander("Show more"):
    st.markdown(load_md(MD_DIR, "md_intro_05.md", LANGUAGE))
    

st.subheader(":blue[How does karst form?]", divider = "blue")
st.markdown(load_md(MD_DIR, "md_intro_06.md", LANGUAGE))
with st.expander("Show more"):
    st.markdown(load_md(MD_DIR, "md_intro_07.md", LANGUAGE))
    
st.subheader(":blue[How does a karst system evolve?]", divider = "blue")
st.markdown(load_md(MD_DIR, "md_intro_08.md", LANGUAGE))
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.image(
        IMAGE_DIR/"karstification.png",
        caption=" Karstification over time (Hartmann et al., 2014)",
        use_container_width=True,
    )
with st.expander("Show more"):
    st.markdown(load_md(MD_DIR, "md_intro_09.md", LANGUAGE))
    
st.subheader(":blue[Triple porosity]", divider = "blue")
st.markdown(load_md(MD_DIR, "md_intro_10.md", LANGUAGE))
with st.expander("Show more"):
    st.markdown(load_md(MD_DIR, "md_intro_11.md", LANGUAGE))
    
st.subheader(":blue[Recharge of karst system]", divider = "blue")
st.markdown(load_md(MD_DIR, "md_intro_12.md", LANGUAGE))
with st.expander("Show more"):
    st.markdown(load_md(MD_DIR, "md_intro_13.md", LANGUAGE))
    
st.subheader(":blue[Internal structure of a karst system]", divider = "blue")
st.markdown(load_md(MD_DIR, "md_intro_14.md", LANGUAGE))
col1, col2, col3 = st.columns([1, 5, 1])
with col2:
    st.image(
        IMAGE_DIR/"karst_conceptual_scheme.png",
        caption=" Conceptual scheme of a karst system",
        use_container_width=True,
    )
with st.expander("Show more"):
    st.markdown(load_md(MD_DIR, "md_intro_15.md", LANGUAGE))
    
st.subheader(":blue[The dual behaviour of karst systems]", divider = "blue")
st.markdown(load_md(MD_DIR, "md_intro_16.md", LANGUAGE))
with st.expander("Show more"):
    st.markdown(load_md(MD_DIR, "md_intro_17.md", LANGUAGE))
    
st.subheader("🎯:blue[Main take-home messages]", divider = "blue")   
st.markdown(load_md(MD_DIR, "md_intro_18.md", LANGUAGE))
    
st.subheader("❓:blue[Check your understanding]", divider = "blue")      
st.markdown(load_md(MD_DIR, "md_intro_19.md", LANGUAGE))    
render_assessment_fragment(
    QUESTIONS_DIR/"intro_ass.json",
    "karst_intro_self_assessment_1",
    "🧠 **Show the self-assessment 1**",
    default_open=False,
)



st.subheader("📖:blue[Further learning material]", divider = "blue")      
st.markdown(load_md(MD_DIR, "md_intro_20.md", LANGUAGE))    

#st.header("Why Karst matters?", divider = "blue")

#col1, col2, col3 = st.columns([1, 5, 1])

#with col2:
  #  st.image(
  #      "assets/images/karst_conceptual_scheme.png",
   #     caption="Conceptual scheme of the karst system",
   #     use_container_width=True,
  #  )

#st.markdown(load_md(MD_DIR, "md_intro_01.md", LANGUAGE))

#with st.expander("Show more"):
  #  st.markdown(load_md(MD_DIR, "md_intro_02.md", LANGUAGE))

#st.subheader("Section B", divider = "blue")
    
#with st.expander("Show more"):
  #  st.markdown(load_md(MD_DIR, "md_intro_02.md", LANGUAGE))

#st.markdown(load_md(MD_DIR, "md_intro_01.md", LANGUAGE))





# Render footer with authors, institutions, and license logo in a single line
columns_lic = st.columns((4,1))
with columns_lic[0]:
    st.markdown(f'Developed by {", ".join(author_list)} ({year}). <br> {institution_text}', unsafe_allow_html=True)
with columns_lic[1]:
    st.image(IMAGE_DIR/'CC_BY-SA_icon.png')
