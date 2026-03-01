"""
Corn Input Optimizer — Streamlit Website
=========================================
Main entry point. Configures the Streamlit multipage app.
"""

import streamlit as st

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="Maiztimate",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Shared CSS applied to every page ────────────────────────────────────────
st.markdown("""
<style>
/* ── Global Reset ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide ALL Streamlit default chrome — no black bar */
#MainMenu {visibility: hidden; height: 0;}
footer {visibility: hidden; height: 0;}
header[data-testid="stHeader"] {
    display: none !important;
    height: 0 !important;
}
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* Kill the dark app background */
.stApp {
    background: #ffffff;
}
[data-testid="stAppViewContainer"] > div:first-child {
    background: transparent !important;
}

/* ── Top Navigation Bar ───────────────────────────────────── */
.navbar {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    z-index: 999;
    background: linear-gradient(135deg, #2d6a4f 0%, #40916c 100%);
    height: 56px;
    padding: 0 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 12px rgba(0,0,0,0.15);
    box-sizing: border-box;
}
.navbar-brand {
    color: white;
    font-size: 1.25rem;
    font-weight: 700;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.navbar-links {
    display: flex;
    gap: 1.5rem;
}
.navbar-links a {
    color: rgba(255,255,255,0.85);
    text-decoration: none;
    font-weight: 500;
    font-size: 0.95rem;
    padding: 0.4rem 0.8rem;
    border-radius: 6px;
    transition: all 0.2s;
}
.navbar-links a:hover, .navbar-links a.active {
    background: rgba(255,255,255,0.15);
    color: white;
}

/* Push page content below fixed navbar (used by optimize page) */
.block-container {
    padding-top: 4.5rem !important;
}

/* ── Input field overrides (replace Streamlit dark defaults) ── */

/* Catch ALL border-rendering elements inside number inputs */
[data-testid="stNumberInput"] > div,
[data-testid="stNumberInput"] [data-baseweb="input"],
[data-testid="stNumberInput"] [data-baseweb="base-input"] {
    background: #f5f7f5 !important;
    border: 1px solid #cdddd4 !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    outline: none !important;
}
[data-testid="stNumberInput"] > div:focus-within,
[data-testid="stNumberInput"] [data-baseweb="input"]:focus-within,
[data-testid="stNumberInput"] [data-baseweb="base-input"]:focus-within {
    border-color: #52b788 !important;
    box-shadow: 0 0 0 2px rgba(82,183,136,0.2) !important;
    background: #ffffff !important;
}
[data-testid="stNumberInput"] input {
    background: #f5f7f5 !important;
    color: #1b4332 !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}
[data-testid="stNumberInput"] > div:focus-within input {
    background: #ffffff !important;
}
/* Stepper buttons */
[data-testid="stNumberInput"] button {
    background: #eaf4ef !important;
    border: none !important;
    border-left: 1px solid #cdddd4 !important;
    color: #2d6a4f !important;
    box-shadow: none !important;
}
[data-testid="stNumberInput"] button:hover {
    background: #d0e9d8 !important;
}

/* Selectbox — catch all wrapper variants */
[data-testid="stSelectbox"] > div > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div:first-child {
    background: #f5f7f5 !important;
    border: 1px solid #cdddd4 !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    outline: none !important;
}
[data-testid="stSelectbox"] > div > div:focus-within,
[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within > div:first-child {
    border-color: #52b788 !important;
    box-shadow: 0 0 0 2px rgba(82,183,136,0.2) !important;
    background: #ffffff !important;
}
[data-testid="stSelectbox"] span,
[data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stSelectbox"] [data-baseweb="select"] div,
[data-testid="stSelectbox"] [data-baseweb="select"] p,
[data-testid="stSelectbox"] [data-baseweb="value"] *,
[data-testid="stSelectbox"] [data-baseweb="single-value"],
[data-testid="stSelectbox"] [data-baseweb="placeholder"] {
    color: #1b4332 !important;
}
[data-testid="stSelectbox"] svg {
    fill: #2d6a4f !important;
    color: #2d6a4f !important;
}

/* Dropdown option list */
[data-baseweb="popover"] ul {
    background: #ffffff !important;
}
[data-baseweb="popover"] li {
    color: #333 !important;
}
[data-baseweb="popover"] li:hover,
[data-baseweb="popover"] li[aria-selected="true"] {
    background: #eaf4ef !important;
    color: #1b4332 !important;
}

/* Form submit button */
[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #2d6a4f, #40916c) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.65rem 1.5rem !important;
    transition: opacity 0.2s !important;
}
[data-testid="stFormSubmitButton"] button:hover {
    opacity: 0.9 !important;
}

/* Labels */
[data-testid="stNumberInput"] label,
[data-testid="stSelectbox"] label {
    color: #444 !important;
    font-size: 0.87rem !important;
    font-weight: 500 !important;
}

/* ── Card style ───────────────────────────────────────────── */
.card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 1px 6px rgba(0,0,0,0.08);
    margin-bottom: 1rem;
}

/* ── Result highlight boxes ───────────────────────────────── */
.metric-box {
    background: linear-gradient(135deg, #d8f3dc 0%, #b7e4c7 100%);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    text-align: center;
    border-left: 5px solid #2d6a4f;
}
.metric-box h3 {
    color: #1b4332;
    margin: 0 0 0.25rem 0;
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.metric-box p {
    color: #2d6a4f;
    margin: 0;
    font-size: 1.6rem;
    font-weight: 700;
}

.metric-box-cost {
    background: linear-gradient(135deg, #fde8e8 0%, #f5c6c6 100%);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    text-align: center;
    border-left: 5px solid #c0392b;
}
.metric-box-cost h3 {
    color: #922b21;
    margin: 0 0 0.25rem 0;
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.metric-box-cost p {
    color: #c0392b;
    margin: 0;
    font-size: 1.6rem;
    font-weight: 700;
}

.metric-box-profit {
    background: linear-gradient(135deg, #d4edda 0%, #a3d9a5 100%);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    text-align: center;
    border-left: 5px solid #1e7e34;
}
.metric-box-profit h3 {
    color: #155724;
    margin: 0 0 0.25rem 0;
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.metric-box-profit p {
    color: #1e7e34;
    margin: 0;
    font-size: 1.6rem;
    font-weight: 700;
}

/* ── Section headers ──────────────────────────────────────── */
.section-header {
    color: #1b4332;
    font-size: 1.3rem;
    font-weight: 700;
    margin: 1.5rem 0 0.75rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #b7e4c7;
}

/* ── Fertilizer table ─────────────────────────────────────── */
.fert-table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.5rem 0;
}
.fert-table th {
    background: #2d6a4f;
    color: white;
    padding: 0.6rem 1rem;
    text-align: left;
    font-size: 0.85rem;
    font-weight: 600;
}
.fert-table td {
    padding: 0.55rem 1rem;
    border-bottom: 1px solid #e8e8e8;
    font-size: 0.9rem;
    color: #333;
}
.fert-table tr:nth-child(even) {
    background: #f8faf8;
}
.fert-table tr:hover {
    background: #e8f5e9;
}

/* ── Info tip ─────────────────────────────────────────────── */
.info-tip {
    background: #e8f4f8;
    border-left: 4px solid #2196F3;
    border-radius: 0 8px 8px 0;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.85rem;
    color: #1565C0;
}

/* ── Primary action button ────────────────────────────────── */
div.stButton > button {
    background: linear-gradient(135deg, #2d6a4f 0%, #40916c 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 2rem;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.2s;
}
div.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(45,106,79,0.35);
    color: white;
}

/* ── Selectbox / Input styling ────────────────────────────── */
.stSelectbox > div > div {
    border-radius: 8px;
}
.stNumberInput > div > div > input {
    border-radius: 8px;
}
/* ── Footer ───────────────────────────────────────────────── */
.footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: linear-gradient(135deg, #2d6a4f 0%, #40916c 100%);
    color: rgba(255,255,255,0.85);
    text-align: center;
    padding: 1rem;
    font-size: 0.85rem;
    line-height: 1.4;
    z-index: 100;
    box-sizing: border-box;
}
.footer strong {
    color: white;
    font-weight: 600;
}</style>
""", unsafe_allow_html=True)


# ── Determine current page from query params (single source of truth) ──────
_qp = st.query_params.get("page", "home")
if _qp not in ("home", "optimize"):
    _qp = "home"
st.session_state.page = _qp


def navigate_to(page_name: str):
    st.session_state.page = page_name


# ── Render navbar ──────────────────────────────────────────────────────────
def render_navbar():
    home_active = "active" if st.session_state.page == "home" else ""
    optimize_active = "active" if st.session_state.page == "optimize" else ""
    st.markdown(f"""
    <div class="navbar">
        <span class="navbar-brand">Maiztimate</span>
        <div class="navbar-links">
            <a href="?page=home" target="_self" class="{home_active}">Home</a>
            <a href="?page=optimize" target="_self" class="{optimize_active}">Optimization</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


render_navbar()

# ── Route to the correct page ──────────────────────────────────────────────
if st.session_state.page == "optimize":
    from pages.optimize import show_optimize_page
    show_optimize_page()
else:
    from pages.home import show_home_page
    show_home_page()

# ── Footer with slogan ─────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <strong>Maiztimate</strong> — <em>Sa mais, dapat segurado ang imo ginansya, indi lang basta-basta.</em>
</div>
""", unsafe_allow_html=True)
