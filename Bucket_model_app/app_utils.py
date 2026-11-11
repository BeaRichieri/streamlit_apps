from pathlib import Path
import streamlit as st

def flip_assessment(section_id: str):
    """Flip the boolean flag for a given section_id."""
    key = f"exp_{section_id}"
    st.session_state[key] = not st.session_state.get(key, False)
    
def render_toggle_container(
    section_id: str,
    label: str,
    content_fn,                 # a function that renders the section contents when open
    *,
    default_open: bool = False,
    col_ratio=(25, 1),
    container_border: bool = True,
):
    """
    Renders a toggleable container with two buttons:
    - Left: text button with your label
    - Right: chevron button (▲/▼)
    Each section manages its own state via section_id.

    Parameters
    ----------
    section_id : unique id string, e.g., "general_01"
    label      : button label shown on the left
    content_fn : callable with no args that renders the open content
    default_open : initial open state (only used on first render)
    col_ratio  : column width ratio for (label_button, chevron_button)
    container_border : show a border around the section container
    """
    state_key = f"exp_{section_id}"
    if state_key not in st.session_state:
        st.session_state[state_key] = default_open

    with st.container(border=container_border):
        ass_c1, ass_c2 = st.columns(col_ratio)

        # Left button – same on_click toggler for consistency
        with ass_c1:
            st.button(label,key=f"btn_label_{section_id}",type="tertiary",on_click=flip_assessment,args=(section_id,))

        # Right chevron button – also toggles the same state
        with ass_c2:
            chevron = "▲" if st.session_state[state_key] else "▼"
            st.button(chevron,key=f"btn_chev_{section_id}",type="tertiary",on_click=flip_assessment,args=(section_id,))

        # Conditional content
        if st.session_state[state_key]:
            content_fn()
            

@st.cache_data
def load_md(MD_DIR, filename, language="en"):
    """
    Load a markdown file.

    Search order:
    1. filename_<language>.md
    2. filename.md (default)
    """

    md_dir = Path(MD_DIR)

    base = Path(filename)

    if language.lower() != "en":
        translated = md_dir / f"{base.stem}_{language}{base.suffix}"
        if translated.exists():
            return translated.read_text(encoding="utf-8")

    default = md_dir / filename
    return default.read_text(encoding="utf-8")
    
