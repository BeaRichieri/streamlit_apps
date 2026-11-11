import os
from pathlib import Path

import streamlit as st


def _navigate_to(path: str):
    """Change page and scroll to the top on next render."""
    if path != st.session_state.selected_path:
        st.session_state.selected_path = path
        st.session_state.scroll_to_top = True
        st.session_state.prev_path = path
    st.rerun()


if "directories_initialized" not in st.session_state:
    #BASE_DIR = Path("Wavelet_app")
    
    #if RUNNING_LOCAL:
    BASE_DIR = Path("C:/Users/beatr/Documents/GitHub/streamlit_apps/Wavelet_app")

    st.session_state.BASE_DIR = BASE_DIR
    st.session_state.CONTENT_DIR = BASE_DIR / "content"
    st.session_state.ASSETS_DIR = BASE_DIR / "assets"
    st.session_state.IMAGE_DIR = BASE_DIR / "assets/images"
    st.session_state.MD_DIR = BASE_DIR / "md"
    st.session_state.QUESTIONS_DIR = BASE_DIR / "questions"

    st.session_state.directories_initialized = True


BASE_DIR = st.session_state.BASE_DIR
CONTENT_DIR = st.session_state.CONTENT_DIR
ASSETS_DIR = st.session_state.ASSETS_DIR
IMAGE_DIR = st.session_state.IMAGE_DIR
MD_DIR = st.session_state.MD_DIR
QUESTIONS_DIR = st.session_state.QUESTIONS_DIR

DEFAULT_START_PAGE = CONTENT_DIR / "start.py"


# --- MUST be first: layout setup wide / centered ---
if "layout_choice" not in st.session_state:
    st.session_state.layout_choice = "centered"

st.set_page_config(
    page_title="Wavelet decomposition of time series",
    page_icon="🌊",
    layout=st.session_state.layout_choice,
)
st.sidebar.markdown("# :rainbow[Wavelet decomposition of time series]")


# --- CSS Styling ---
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] div.stButton > button {
        width: 100% !important;
        justify-content: flex-start !important;
        text-align: left !important;
        background-color: transparent !important;
        border: none !important;
        border-radius: 0.55rem !important;
        padding: 0.40rem 0.65rem !important;
        margin: 0 !important;
        font-size: 1rem !important;
        font-weight: 400 !important;
        line-height: 1.2 !important;
        color: inherit !important;
    }

    section[data-testid="stSidebar"]
    div.stButton > button[kind="primary"] {
        background-color: rgba(120, 130, 150, 0.18) !important;
        font-weight: 700 !important;
    }

    section[data-testid="stSidebar"]
    div.stButton > button:hover {
        background-color: rgba(120, 130, 150, 0.10) !important;
        color: inherit !important;
    }

    section[data-testid="stSidebar"]
    div.stButton > button[kind="primary"]:hover {
        background-color: rgba(120, 130, 150, 0.23) !important;
    }

    section[data-testid="stSidebar"] div.stButton {
        margin: 0 !important;
        padding: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

pages = {
    "Welcome": CONTENT_DIR / "start.py",
    "🌊 Wavelet decomposition": CONTENT_DIR / "wavelet_decomposition.py",
    "ℹ️ About": CONTENT_DIR / "about.py",
}

if "selected_path" not in st.session_state:
    st.session_state.selected_path = DEFAULT_START_PAGE
if "prev_path" not in st.session_state:
    st.session_state.prev_path = st.session_state.selected_path
if "scroll_to_top" not in st.session_state:
    st.session_state.scroll_to_top = False

st.sidebar.markdown("<div style='margin-top: 2.0rem;'></div>", unsafe_allow_html=True)

for index, (label, path) in enumerate(pages.items()):
    is_selected = st.session_state.selected_path == path

    clicked = st.sidebar.button(
        label.strip(),
        key=f"nav_{index}",
        type="primary" if is_selected else "secondary",
        use_container_width=True,
    )

    if clicked and not is_selected:
        _navigate_to(path)

if st.session_state.selected_path:
    path = st.session_state.selected_path
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            exec(file.read(), globals())
    else:
        st.error(f"❌ File not found: `{path}`")

st.sidebar.markdown("---")
layout_options = ["centered", "wide"]
selected_layout = st.sidebar.radio(
    "Page layout",
    layout_options,
    index=layout_options.index(st.session_state.layout_choice),
)
if selected_layout != st.session_state.layout_choice:
    st.session_state.layout_choice = selected_layout
    st.rerun()
