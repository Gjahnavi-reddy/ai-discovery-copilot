"""Automated UI test for Streamlit application."""

import os
from streamlit.testing.v1 import AppTest

APP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "app.py"))


def test_streamlit_app_loads_and_sidebar_renders():
    """Verify Streamlit app runs cleanly without exceptions and renders sidebar properly."""
    at = AppTest.from_file(APP_PATH)
    at.run()

    # 1. Verify zero exceptions during execution
    assert len(at.exception) == 0, f"Encountered unexpected exceptions: {at.exception}"

    # 2. Verify sidebar branding
    sidebar_md_texts = [m.value for m in at.sidebar.markdown]
    assert any("CYNBIT TECHNOLOGIES" in t for t in sidebar_md_texts), "Sidebar missing CYNBIT TECHNOLOGIES branding"
    assert any("AI Discovery Copilot" in t for t in sidebar_md_texts), "Sidebar missing AI Discovery Copilot title"
    assert not any("DeltaGenerator" in t for t in sidebar_md_texts), "Sidebar contains raw DeltaGenerator output"
    assert not any("st.image" in t for t in sidebar_md_texts), "Sidebar contains raw Python code"

    # 3. Verify sidebar controls
    assert len(at.sidebar.selectbox) >= 1
    assert len(at.sidebar.radio) >= 1
    assert at.sidebar.radio[0].value == "Deterministic Local Heuristic (Offline)"

    # 4. Verify main dashboard structure
    assert len(at.tabs) == 6
    assert len(at.slider) == 4
    assert len(at.download_button) == 4
