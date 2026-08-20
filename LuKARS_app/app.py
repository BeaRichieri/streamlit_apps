import streamlit as st
import os
import streamlit.components.v1 as components
from pathlib import Path

def _navigate_to(path: str):
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
    BASE_DIR = Path("LuKARS_app")

    # For local use with an absolute path, replace the line above with:
    #BASE_DIR = Path("C:/Users/beatr/Documents/Eurokarst2026/Course/LuKARS_Multipage_App")

    st.session_state.BASE_DIR = BASE_DIR
    st.session_state.CONTENT_DIR = BASE_DIR / "content"
    st.session_state.ASSETS_DIR = BASE_DIR / "assets"
    st.session_state.IMAGE_DIR = BASE_DIR / "assets" / "images"
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
BAGET_PAGE = CONTENT_DIR / "Baget.py"  # for live plots

# --- MUST be first: layout setup wide / centered ---
if "layout_choice" not in st.session_state:
    st.session_state.layout_choice = "centered"

st.set_page_config(page_title="Karst Flow Conceptual Modelling", page_icon="💦", layout=st.session_state.layout_choice)

# -----------------------------------------------------------------------------
# Standalone lumped-model tutorial
# -----------------------------------------------------------------------------
_lumped_tutorial = (
    st.query_params.get("lumped_tutorial", "")
    if hasattr(st, "query_params")
    else ""
)

if _lumped_tutorial in {"steady", "unsteady"}:

    tutorial_files = {
        "steady": MD_DIR / "md_lumped_tutorial_steady.md",
        "unsteady": MD_DIR / "md_lumped_tutorial_unsteady.md",
    }

    tutorial_file = tutorial_files[_lumped_tutorial]

    # Hide normal app elements
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {
            display: none !important;
        }

        [data-testid="stHeader"] {
            display: none !important;
        }

        .block-container {
            max-width: 900px !important;
            padding-top: 2rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if tutorial_file.exists():
        st.markdown(
            tutorial_file.read_text(encoding="utf-8"),
            unsafe_allow_html=True,
        )
    else:
        st.error(f"Tutorial file not found: `{tutorial_file}`")

    st.stop()

st.sidebar.markdown("# :rainbow[Karst Flow Conceptual Modelling]")

# -----------------------------------------------------------------------------
# Live companion routing
# -----------------------------------------------------------------------------
_live_plot = (
    st.query_params.get("live_plot", "")
    if hasattr(st, "query_params")
    else ""
)

_live_id = (
    st.query_params.get("live_id", "")
    if hasattr(st, "query_params")
    else ""
)

_tutorial_exercise = (
    st.query_params.get("tutorial_exercise", "")
    if hasattr(st, "query_params")
    else ""
)

_route_to_baget = (
    (
        _live_plot in {"discharge", "fluxes", "storages"}
        and _live_id
    )
    or _tutorial_exercise in {"1", "2", "3", "4", "5"}
)

if _route_to_baget:
    if os.path.exists(BAGET_PAGE):
        with open(BAGET_PAGE, "r", encoding="utf-8") as f:
            exec(f.read(), globals())
    else:
        st.error(f"❌ File not found: `{BAGET_PAGE}`")

    st.stop()

# --- CSS Styling ---
st.markdown(
    """
    <style>
    /* All sidebar navigation buttons */
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

    /* Selected page */
    section[data-testid="stSidebar"]
    div.stButton > button[kind="primary"] {
        background-color: rgba(120, 130, 150, 0.18) !important;
        font-weight: 700 !important;
    }

    /* Hover effect */
    section[data-testid="stSidebar"]
    div.stButton > button:hover {
        background-color: rgba(120, 130, 150, 0.10) !important;
        color: inherit !important;
    }

    /* Keep selected page highlighted when hovering */
    section[data-testid="stSidebar"]
    div.stButton > button[kind="primary"]:hover {
        background-color: rgba(120, 130, 150, 0.23) !important;
    }

    /* Reduce vertical space between navigation buttons */
    section[data-testid="stSidebar"] div.stButton {
        margin: 0 !important;
        padding: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
# --- Flat page definitions ---
pages = {
    "Welcome": CONTENT_DIR / "start.py",
    "💦 Introduction to karst": CONTENT_DIR / "intro.py",
    "📦 Lumped conceptual models": CONTENT_DIR / "lumped_models.py",
    "📍 Overview": CONTENT_DIR / "LuKARS_overview.py",
    "📖 Model description": CONTENT_DIR / "model_description.py",
    #"🪨 Kerschbaum case study": CONTENT_DIR / "Kerschbaum.py",
    "⛰️ Baget case study": BAGET_PAGE,
    #"📁 Upload your own data": CONTENT_DIR / "own_data.py",
    "ℹ️ About": CONTENT_DIR / "about.py",
}

# --- State tracking ---
if "selected_path" not in st.session_state:
    st.session_state.selected_path = DEFAULT_START_PAGE
if "prev_path" not in st.session_state:
    st.session_state.prev_path = st.session_state.selected_path
if "scroll_to_top" not in st.session_state:
    st.session_state.scroll_to_top = False

# Space before the first button
st.sidebar.markdown("<div style='margin-top: 2.0rem;'></div>", unsafe_allow_html=True)

# --- Overview and About buttons (at top)
#if st.sidebar.button("Welcome", key="btn_overview"):
   # st.session_state.selected_path = DEFAULT_START_PAGE
    #st.rerun()   
   # _navigate_to(DEFAULT_START_PAGE)

# --- Sidebar navigation ---
for index, (label, path) in enumerate(pages.items()):

    if "💦️ Introduction to karst" in label:
        st.sidebar.markdown(
            "#### :blue[Choose from the topics below]"
        )

    is_selected = st.session_state.selected_path == path
    clean_label = label.strip()

    clicked = st.sidebar.button(
        clean_label,
        key=f"nav_{index}",
        type="primary" if is_selected else "secondary",
        use_container_width=True,
    )

    if clicked and not is_selected:
        _navigate_to(path)

    # Insert section headings after specific pages
    if "📦 Lumped conceptual models" in label:
        st.sidebar.markdown("**LuKARS Flow Model**")


    #if "🧮 Morris and GLUE application" in label:
     #   st.sidebar.markdown("**Additional Information**")
        
# --- Run selected page ---
if st.session_state.selected_path:
    path = st.session_state.selected_path

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            exec(f.read(), globals())
    else:
        st.error(f"❌ File not found: `{path}`")

# --- Scroll to top once after page navigation ---
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

            // Run immediately and once more after rendering has settled.
            scrollStreamlitMainToTop();
            setTimeout(scrollStreamlitMainToTop, 100);
        </script>
        """,
        height=0,
    )

    st.session_state.scroll_to_top = False
    
# --- Layout switcher at bottom of the sidebar ---
st.sidebar.markdown('---')
layout_options = ["centered", "wide"]
selected_layout = st.sidebar.radio("Page layout", layout_options, index=layout_options.index(st.session_state.layout_choice))
if selected_layout != st.session_state.layout_choice:
    st.session_state.layout_choice = selected_layout
    st.rerun()