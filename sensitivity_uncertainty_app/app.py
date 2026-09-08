import os
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


def _navigate_to(path: Path):
    """Change page and scroll to the top on next render."""
    if path != st.session_state.selected_path:
        st.session_state.selected_path = path
        st.session_state.scroll_to_top = True
        st.session_state.prev_path = path
    st.rerun()


# -----------------------------------------------------------------------------
# Application directories
# -----------------------------------------------------------------------------
if "directories_initialized" not in st.session_state:
    #BASE_DIR = Path("sensitivity_uncertainty_app")

    # For local use with an absolute path, replace the line above with:
    BASE_DIR = Path("C:/Users/beatr/Documents/Eurokarst2026/Course/sensitivity_uncertainty_app")

    st.session_state.BASE_DIR = BASE_DIR
    st.session_state.CONTENT_DIR = BASE_DIR / "content"
    st.session_state.ASSETS_DIR = BASE_DIR / "assets"
    st.session_state.IMAGE_DIR = BASE_DIR / "assets" / "images"
    st.session_state.MD_DIR = BASE_DIR / "md"
    st.session_state.QUESTIONS_DIR = BASE_DIR / "questions"

    st.session_state.directories_initialized = True

CONTENT_DIR = st.session_state.CONTENT_DIR
ASSETS_DIR = st.session_state.ASSETS_DIR
IMAGE_DIR = st.session_state.IMAGE_DIR
MD_DIR = st.session_state.MD_DIR
QUESTIONS_DIR = st.session_state.QUESTIONS_DIR

DEFAULT_START_PAGE = CONTENT_DIR / "start.py"


# -----------------------------------------------------------------------------
# Page configuration
# -----------------------------------------------------------------------------
if "layout_choice" not in st.session_state:
    st.session_state.layout_choice = "centered"

st.set_page_config(
    page_title="Introduction to sensitivity and uncertainty analyses",
    page_icon="🧮",
    layout=st.session_state.layout_choice,
)

st.sidebar.markdown(
    "# :rainbow[Introduction to sensitivity and uncertainty analyses]"
)


# -----------------------------------------------------------------------------
# CSS styling
# -----------------------------------------------------------------------------
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

    section[data-testid="stSidebar"] div.stButton > button:hover {
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


# -----------------------------------------------------------------------------
# Page definitions
# -----------------------------------------------------------------------------
pages = {
    "Welcome": CONTENT_DIR / "start.py",

    # Sensitivity analysis
    "📊 Introduction": CONTENT_DIR / "sensitivity_intro.py",
    "📍 Local sensitivity": CONTENT_DIR / "sensitivity_local.py",
    "🧭 Morris method": CONTENT_DIR / "sensitivity_morris.py",
    "📈 Sobol' method": CONTENT_DIR / "sensitivity_sobol.py",

    # Parameter uncertainty
    "🎲 Introduction": CONTENT_DIR / "uncertainty_intro.py",
    "🔍 Equifinality": CONTENT_DIR / "uncertainty_equifinality.py",
    "🎯 GLUE": CONTENT_DIR / "uncertainty_glue.py",

    # Additional information
    "ℹ️ About": CONTENT_DIR / "about.py",
}

SENSITIVITY_FIRST_PAGE = CONTENT_DIR / "sensitivity_intro.py"
UNCERTAINTY_FIRST_PAGE = CONTENT_DIR / "uncertainty_intro.py"
ABOUT_PAGE = CONTENT_DIR / "about.py"


# -----------------------------------------------------------------------------
# State tracking
# -----------------------------------------------------------------------------
if "selected_path" not in st.session_state:
    st.session_state.selected_path = DEFAULT_START_PAGE

valid_paths = set(pages.values())
if st.session_state.selected_path not in valid_paths:
    st.session_state.selected_path = DEFAULT_START_PAGE

if "prev_path" not in st.session_state:
    st.session_state.prev_path = st.session_state.selected_path

if "scroll_to_top" not in st.session_state:
    st.session_state.scroll_to_top = False


# -----------------------------------------------------------------------------
# Sidebar navigation
# -----------------------------------------------------------------------------
st.sidebar.markdown(
    "<div style='margin-top: 2.0rem;'></div>",
    unsafe_allow_html=True,
)

for index, (label, path) in enumerate(pages.items()):

    if path == SENSITIVITY_FIRST_PAGE:
        st.sidebar.markdown("### :blue[Sensitivity analysis]")

    if path == UNCERTAINTY_FIRST_PAGE:
        st.sidebar.markdown("### :blue[Parameter uncertainty]")

    if path == ABOUT_PAGE:
        st.sidebar.markdown("### :blue[Additional information]")

    is_selected = st.session_state.selected_path == path

    clicked = st.sidebar.button(
        label.strip(),
        key=f"nav_{index}",
        type="primary" if is_selected else "secondary",
        use_container_width=True,
    )

    if clicked and not is_selected:
        _navigate_to(path)


# -----------------------------------------------------------------------------
# Run selected page
# -----------------------------------------------------------------------------
if st.session_state.selected_path:
    path = st.session_state.selected_path

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            exec(file.read(), globals())
    else:
        st.error(f"❌ File not found: `{path}`")


# -----------------------------------------------------------------------------
# Scroll to top after navigation
# -----------------------------------------------------------------------------
if st.session_state.scroll_to_top:
    components.html(
        """
        <script>
            function scrollStreamlitMainToTop() {
                const main = window.parent.document.querySelector(
                    'section[data-testid="stMain"]'
                );

                if (main) {
                    main.scrollTop = 0;
                    main.scrollLeft = 0;
                }
            }

            scrollStreamlitMainToTop();
            setTimeout(scrollStreamlitMainToTop, 100);
        </script>
        """,
        height=0,
    )

    st.session_state.scroll_to_top = False


# -----------------------------------------------------------------------------
# Layout switcher
# -----------------------------------------------------------------------------
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
