"""
Home Page
=========
Simple, clean, responsive home page for corn farmers.
"""

import streamlit as st


def show_home_page():

    st.markdown("""
    <style>
    .block-container {
        padding-top: 4rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        max-width: 900px !important;
        margin: 0 auto !important;
    }

    /* ── Hero card ── */
    .home-hero {
        background: #f0f7f2;
        border-left: 5px solid #2d6a4f;
        border-radius: 12px;
        padding: 1.8rem 1.5rem;
        margin-bottom: 2rem;
    }
    .home-hero h1 {
        color: #1b4332;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        line-height: 1.3;
    }
    .home-hero p {
        color: #444;
        font-size: 0.95rem;
        margin: 0 0 1.2rem 0;
        line-height: 1.65;
    }
    .hero-cta, .hero-cta:link, .hero-cta:visited {
        background: #2d6a4f;
        color: #fff !important;
        text-decoration: none !important;
        padding: 0.65rem 1.5rem;
        border-radius: 8px;
        font-size: 0.95rem;
        font-weight: 600;
        display: inline-block;
    }
    .hero-cta:hover { background: #1b4332; color: #fff !important; text-decoration: none !important; }

    /* ── Larger text on desktop ── */
    @media (min-width: 640px) {
        .home-hero { padding: 2.2rem 2rem; }
        .home-hero h1 { font-size: 1.9rem; }
    }

    /* ── Section label ── */
    .slabel {
        color: #2d6a4f;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin: 0 0 0.75rem 0;
    }

    /* ── Step cards: 1 col mobile → 3 col desktop ── */
    .steps-row {
        display: grid;
        grid-template-columns: 1fr;
        gap: 0.85rem;
        margin-bottom: 2rem;
    }
    @media (min-width: 640px) {
        .steps-row { grid-template-columns: repeat(3, 1fr); }
    }
    .step-card {
        background: #fff;
        border: 1px solid #dde8e1;
        border-radius: 10px;
        padding: 1.2rem 1rem;
        text-align: center;
    }
    .step-num {
        width: 36px; height: 36px;
        background: #2d6a4f;
        color: #fff;
        border-radius: 50%;
        font-size: 1rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.6rem;
    }
    .step-card h3 { color: #1b4332; font-size: 0.92rem; font-weight: 700; margin: 0 0 0.3rem 0; }
    .step-card p  { color: #666; font-size: 0.82rem; line-height: 1.5; margin: 0; }

    /* ── Benefit items: 1 col mobile → 2 col desktop ── */
    .benefits-row {
        display: grid;
        grid-template-columns: 1fr;
        gap: 0.85rem;
        margin-bottom: 2rem;
    }
    @media (min-width: 640px) {
        .benefits-row { grid-template-columns: repeat(2, 1fr); }
    }
    .benefit-item {
        background: #f9faf9;
        border: 1px solid #dde8e1;
        border-radius: 10px;
        padding: 1rem;
        display: flex;
        gap: 0.75rem;
        align-items: flex-start;
    }
    .bicon { font-size: 1.25rem; flex-shrink: 0; margin-top: 0.1rem; }
    .benefit-item h4 { color: #1b4332; font-size: 0.88rem; font-weight: 700; margin: 0 0 0.2rem 0; }
    .benefit-item p  { color: #666; font-size: 0.81rem; line-height: 1.5; margin: 0; }

    /* ── Footer note ── */
    .home-note {
        text-align: center;
        color: #aaa;
        font-size: 0.74rem;
        padding: 1rem 0 0.5rem 0;
        border-top: 1px solid #eee;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Hero ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="home-hero">
        <h1>🌽 Corn Input Optimizer</h1>
        <p>Find the best fertilizer combination for your cornfield.<br>
        Enter your farm details and get a clear, practical recommendation — fast.</p>
        <a class="hero-cta" href="?page=optimize" target="_self">Start Optimizing →</a>
    </div>
    """, unsafe_allow_html=True)

    # ── How It Works ─────────────────────────────────────────────────────────
    st.markdown('<p class="slabel">How It Works</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="steps-row">
        <div class="step-card">
            <div class="step-num">1</div>
            <h3>Enter Farm Details</h3>
            <p>Input your farm size, soil type, budget, and planting season.</p>
        </div>
        <div class="step-card">
            <div class="step-num">2</div>
            <h3>Run Optimization</h3>
            <p>The algorithm tests different combinations to find the best plan for your farm.</p>
        </div>
        <div class="step-card">
            <div class="step-num">3</div>
            <h3>Get Your Plan</h3>
            <p>See which fertilizers to buy, how much to apply, and your expected profit.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── What You'll Get ───────────────────────────────────────────────────────
    st.markdown('<p class="slabel">What You\'ll Get</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="benefits-row">
        <div class="benefit-item">
            <div class="bicon">🧪</div>
            <div><h4>Fertilizer Recommendation</h4>
            <p>Which fertilizers to buy, how many sacks, and the full NPK breakdown.</p></div>
        </div>
        <div class="benefit-item">
            <div class="bicon">📈</div>
            <div><h4>Expected Yield</h4>
            <p>Projected corn yield in kg/ha based on your specific inputs.</p></div>
        </div>
        <div class="benefit-item">
            <div class="bicon">💰</div>
            <div><h4>Cost &amp; Profit Breakdown</h4>
            <p>Total input cost, expected revenue, and estimated net profit.</p></div>
        </div>
        <div class="benefit-item">
            <div class="bicon">📊</div>
            <div><h4>Visual Comparison</h4>
            <p>Charts comparing GA vs Memetic Algorithm results side by side.</p></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="home-note">
        Based on DA Region 6 validated data (2026) &nbsp;·&nbsp; For corn farmers in the Philippines
    </div>
    """, unsafe_allow_html=True)


