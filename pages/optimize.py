"""
Optimize Page
==============
Farmer enters conditions → Algorithm runs → Results displayed.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from config.params import (
    CHROMOSOME_CONSTRAINTS, MONTH_NAMES, CORN_MARKET_PRICE,
    RECOMMENDED_N, RECOMMENDED_P, RECOMMENDED_K,
    WET_SEASON_MONTHS, DRY_SEASON_MONTHS,
)

def _season_label(month: int) -> str:
    return "Wet Season" if month in WET_SEASON_MONTHS else "Dry Season"


@st.cache_data
def _load_fertilizer_data():
    """Load fertilizer data with caching to avoid repeated CSV reads."""
    data_dir = Path(__file__).parent.parent / "data"
    return pd.read_csv(data_dir / "region_6_fertilizers.csv")


@st.cache_data
def _load_seed_data():
    """Load seed variety data with caching to avoid repeated CSV reads."""
    data_dir = Path(__file__).parent.parent / "data"
    return pd.read_csv(data_dir / "seed_varieties.csv").set_index("name")


def _format_peso(value: float) -> str:
    return f"₱{value:,.2f}"


def _format_kg(value: float) -> str:
    return f"{value:,.0f} kg"

def show_optimize_page():

    st.markdown("""
    <style>
    .block-container {
        padding-top: 4rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        max-width: 960px !important;
        margin: 0 auto !important;
    }

    /* ── Page title ── */
    .page-title {
        margin-bottom: 1.5rem;
    }
    .page-title h1 {
        color: #1b4332;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0 0 0.25rem 0;
    }
    .page-title p {
        color: #666;
        font-size: 0.9rem;
        margin: 0;
    }
    @media (min-width: 640px) {
        .page-title h1 { font-size: 1.8rem; }
    }

    /* ── Form section group ── */
    .form-group {
        background: #f8faf8;
        border: 1px solid #dde8e1;
        border-radius: 12px;
        padding: 1.2rem 1.2rem 0.4rem 1.2rem;
        margin-bottom: 1rem;
    }
    .form-group-title {
        color: #1b4332;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.1px;
        margin: 0 0 0.9rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #b7e4c7;
    }

    /* ── Info tip ── */
    .tip-box {
        background: #eaf4ef;
        border-left: 4px solid #52b788;
        border-radius: 0 8px 8px 0;
        padding: 0.6rem 0.9rem;
        margin-bottom: 0.9rem;
        font-size: 0.83rem;
        color: #2d6a4f;
    }

    /* ── Results section header ── */
    .res-header {
        color: #1b4332;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.1px;
        margin: 1.5rem 0 0.75rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 2px solid #b7e4c7;
    }

    /* ── Metric cards ── */
    .metric-row {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.85rem;
        margin-bottom: 1.5rem;
    }
    @media (min-width: 640px) {
        .metric-row { grid-template-columns: repeat(4, 1fr); }
    }
    .mcard {
        border-radius: 10px;
        padding: 1rem 1rem;
        text-align: center;
    }
    .mcard-green  { background: #e8f5e9; border: 1px solid #a5d6a7; }
    .mcard-red    { background: #fdecea; border: 1px solid #f5c6c6; }
    .mcard-profit { background: #e3f2e3; border: 1px solid #81c784; }
    .mcard label {
        color: #555;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        display: block;
        margin-bottom: 0.3rem;
    }
    .mcard .mval-green  { color: #1b5e20; font-size: 1.25rem; font-weight: 700; margin: 0; }
    .mcard .mval-red    { color: #b71c1c; font-size: 1.25rem; font-weight: 700; margin: 0; }
    .mcard .mval-profit { color: #1b5e20; font-size: 1.4rem;  font-weight: 700; margin: 0; }

    /* ── Clean table ── */
    .clean-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.88rem;
    }
    .clean-table th {
        background: #2d6a4f;
        color: #fff;
        padding: 0.55rem 0.9rem;
        text-align: left;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .clean-table td {
        padding: 0.5rem 0.9rem;
        border-bottom: 1px solid #eef2ee;
        color: #333;
    }
    .clean-table tr:nth-child(even) td { background: #f5faf5; }
    .clean-table tr:last-child td { background: #e8f5e9; font-weight: 700; }

    /* ── Info card ── */
    .icard {
        background: #f8faf8;
        border: 1px solid #dde8e1;
        border-radius: 10px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.85rem;
    }
    .icard h4 {
        color: #2d6a4f;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin: 0 0 0.5rem 0;
    }
    .icard p { color: #555; font-size: 0.87rem; line-height: 1.75; margin: 0; }

    /* ── Summary cards grid ── */
    .summary-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 0.85rem;
        margin-bottom: 1.5rem;
    }
    @media (min-width: 640px) {
        .summary-grid { grid-template-columns: repeat(3, 1fr); }
    }

    /* ── Disclaimer ── */
    .disclaimer {
        text-align: center;
        color: #aaa;
        font-size: 0.73rem;
        padding: 1rem 0 0.5rem 0;
        border-top: 1px solid #eee;
        margin-top: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="page-title">
        <h1>🌾 Optimize Your Farm</h1>
        <p>Fill in your farm details below, then press <strong>Optimize</strong>.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("farm_form"):

        st.markdown('<p class="form-group-title">Farm Information</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            farm_area = st.number_input(
                "Farm Size (hectares)",
                min_value=1, max_value=100, value=1, step=1,
                help="Minimum 1 hectare"
            )
        with c2:
            seed_variety = st.selectbox(
                "Corn Variety",
                options=["Hybrid", "Glutinous", "OPV"],
                index=0,
                help="Hybrid is the most common commercial variety"
            )
        with c3:
            topography = st.selectbox(
                "Land Type",
                options=["Plain", "Elevated"],
                index=0,
                help="Plain = flat farmland · Elevated = hilly / upland"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<p class="form-group-title">Soil Conditions</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="tip-box">
            💡 <strong>Tip:</strong> If you don't know your exact soil nutrients, use the default values —
            they represent typical moderate-fertility soil in Region 6.
        </div>
        """, unsafe_allow_html=True)

        c4, c5 = st.columns(2)
        with c4:
            soil_type = st.selectbox(
                "Soil Type",
                options=["Loamy", "Sandy", "Clay"],
                index=0,
                help="Loamy is best for corn. Sandy drains fast. Clay retains water."
            )
        with c5:
            soil_ph = st.number_input(
                "Soil pH",
                min_value=4.0, max_value=9.0, value=6.5, step=0.1,
                help="Ideal range: 6.0 – 7.0"
            )

        c6, c7, c8 = st.columns(3)
        with c6:
            initial_n = st.number_input(
                "Nitrogen in Soil (kg/ha)",
                min_value=0.0, max_value=200.0, value=80.0, step=5.0
            )
        with c7:
            initial_p = st.number_input(
                "Phosphorus in Soil (kg/ha)",
                min_value=0.0, max_value=100.0, value=25.0, step=2.0
            )
        with c8:
            initial_k = st.number_input(
                "Potassium in Soil (kg/ha)",
                min_value=0.0, max_value=200.0, value=60.0, step=5.0
            )

        npk_warnings = []
        if initial_n > RECOMMENDED_N:
            npk_warnings.append(f"N: {initial_n:.0f} > {RECOMMENDED_N}")
        if initial_p > RECOMMENDED_P:
            npk_warnings.append(f"P: {initial_p:.0f} > {RECOMMENDED_P}")
        if initial_k > RECOMMENDED_K:
            npk_warnings.append(f"K: {initial_k:.0f} > {RECOMMENDED_K}")
        
        if npk_warnings:
            st.info(f"⚠️ Soil nutrient(s) exceed recommended: {', '.join(npk_warnings)} kg/ha", icon="ℹ️")

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<p class="form-group-title">Planting Conditions</p>', unsafe_allow_html=True)
        c9, c10 = st.columns(2)
        with c9:
            planting_month = st.selectbox(
                "Planting Month",
                options=list(range(1, 13)),
                format_func=lambda m: f"{MONTH_NAMES[m]}  ({_season_label(m)})",
                index=5,
                help="Wet season (May–Nov) has more rain. Dry season (Dec–Apr) may need irrigation."
            )
        with c10:
            irrigation = st.selectbox(
                "Irrigation Available?",
                options=["No", "Yes"],
                index=0,
                help="Irrigation helps during dry season"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        submitted = st.form_submit_button(
            "🌽  Optimize My Farm",
            use_container_width=True
        )

    if submitted:
        farm_params = {
            'farm_area_ha': farm_area,
            'topography': topography,
            'soil_type': soil_type,
            'soil_ph': soil_ph,
            'initial_n_kg_ha': initial_n,
            'initial_p_kg_ha': initial_p,
            'initial_k_kg_ha': initial_k,
            'planting_month': planting_month,
            'irrigation_available': irrigation == "Yes",
        }

        from algorithm.optimizer import Optimizer

        progress_bar = st.progress(0, text="Initializing optimizer…")

        def on_progress(gen, max_gen, best_fit):
            pct = gen / max_gen
            progress_bar.progress(pct, text=f"Generation {gen}/{max_gen} — Best profit so far: {_format_peso(best_fit)}")

        try:
            optimizer = Optimizer(farm_params, seed_variety)
            best = optimizer.run(progress_callback=on_progress)
        except Exception as e:
            progress_bar.empty()
            st.error(f"Optimization failed: {e}")
            return

        progress_bar.progress(1.0, text="Optimization complete!")

        if best is None:
            st.warning("The optimizer could not find a viable plan. Try adjusting your soil nutrients or farm parameters.")
            return

        from models.yield_model import YieldModel
        from models.cost_model import CostModel

        data_dir = str(Path(__file__).parent.parent / "data")

        yield_model = YieldModel(
            farm_area_ha=farm_area, seed_variety=seed_variety,
            planting_density=best['planting_density'],
            fertilizer_composition=best['fertilizer_composition'],
            topography=topography, soil_type=soil_type, soil_ph=soil_ph,
            initial_n_kg_ha=initial_n, initial_p_kg_ha=initial_p,
            initial_k_kg_ha=initial_k, planting_month=planting_month,
            irrigation_available=(irrigation == "Yes"), data_dir=data_dir
        )

        cost_model = CostModel(
            farm_area_ha=farm_area, seed_variety=seed_variety,
            planting_density=best['planting_density'],
            fertilizer_composition=best['fertilizer_composition'],
            topography=topography, data_dir=data_dir
        )

        total_yield  = yield_model.calculate_yield()
        revenue      = total_yield * farm_area * CORN_MARKET_PRICE
        seed_cost    = cost_model.calculate_seed_cost()
        fert_cost    = cost_model.calculate_fertilizer_cost()
        ops_cost     = cost_model.calculate_operational_costs()
        herb_cost    = cost_model.calculate_herbicide_cost()
        total_cost   = cost_model.calculate_total_cost()
        profit       = revenue - total_cost

        fert_data = _load_fertilizer_data().set_index("id").to_dict(orient="index")
        n_from_fert = sum(sacks * 50 * (fert_data[fid].get("nitrogen",    0) / 100) for fid, sacks in best['fertilizer_composition'].items() if fid in fert_data)
        p_from_fert = sum(sacks * 50 * (fert_data[fid].get("phosphorus",  0) / 100) for fid, sacks in best['fertilizer_composition'].items() if fid in fert_data)
        k_from_fert = sum(sacks * 50 * (fert_data[fid].get("potassium",   0) / 100) for fid, sacks in best['fertilizer_composition'].items() if fid in fert_data)
        total_n = initial_n + n_from_fert
        total_p = initial_p + p_from_fert
        total_k = initial_k + k_from_fert

        st.markdown('<p class="res-header">✅ Your Optimized Farming Plan</p>', unsafe_allow_html=True)

        profit_color = "mval-profit" if profit >= 0 else "mval-red"
        st.markdown(f"""
        <div class="metric-row">
            <div class="mcard mcard-green">
                <label>Expected Yield</label>
                <p class="mval-green">{total_yield * farm_area:,.0f} kg</p>
            </div>
            <div class="mcard mcard-green">
                <label>Expected Revenue</label>
                <p class="mval-green">{_format_peso(revenue)}</p>
            </div>
            <div class="mcard mcard-red">
                <label>Total Cost</label>
                <p class="mval-red">{_format_peso(total_cost)}</p>
            </div>
            <div class="mcard mcard-profit">
                <label>Net Profit</label>
                <p class="{profit_color}">{_format_peso(profit)}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        _seed_csv = _load_seed_data()  # Load once for both columns
        left_col, right_col = st.columns([3, 2])

        with left_col:
            st.markdown('<p class="res-header">🧪 Fertilizer Recommendation</p>', unsafe_allow_html=True)
            fert_df_data = _load_fertilizer_data().set_index("id")
            table_rows = ""
            total_sacks = 0
            for fid, sacks in sorted(best['fertilizer_composition'].items()):
                if fid not in fert_df_data.index:
                    continue
                info = fert_df_data.loc[fid]
                total_sacks_item = sacks * farm_area
                total_sacks += total_sacks_item
                kg_per_ha   = sacks * 50
                item_cost   = total_sacks_item * info["price"]
                table_rows += (f'<tr>'
                    f'<td><strong>{info["name"]}</strong></td>'
                    f'<td style="text-align:center;">{sacks:.2f}</td>'
                    f'<td style="text-align:center;">{kg_per_ha:.0f} kg</td>'
                    f'<td style="text-align:center;">{total_sacks_item:.2f}</td>'
                    f'<td style="text-align:right;">{_format_peso(item_cost)}</td>'
                    f'</tr>')

            total_label = f"(×{farm_area:.0f} ha)" if farm_area > 1 else ""
            st.markdown(
            f'<table class="clean-table">'
            f'<tr><th>Fertilizer</th><th style="text-align:center;">Sacks/ha</th>'
            f'<th style="text-align:center;">kg/ha</th>'
            f'<th style="text-align:center;">Total Sacks {total_label}</th><th style="text-align:right;">Cost</th></tr>'
            f'{table_rows}'
            f'<tr><td colspan="3" style="text-align:right;"><strong>Total:</strong></td><td style="text-align:center;"><strong>{total_sacks:.2f}</strong></td><td style="text-align:right;">{_format_peso(fert_cost)}</td></tr>'
            f'</table>',
            unsafe_allow_html=True)

            st.markdown('<p class="res-header">🧬 Nutrient Summary (NPK)</p>', unsafe_allow_html=True)

            n_pct = (total_n / RECOMMENDED_N * 100) if RECOMMENDED_N else 0
            p_pct = (total_p / RECOMMENDED_P * 100) if RECOMMENDED_P else 0
            k_pct = (total_k / RECOMMENDED_K * 100) if RECOMMENDED_K else 0

            def _npk_bar(label, delivered, recommended, pct):
                color = "#2d6a4f" if 85 <= pct <= 115 else "#e67e22" if 70 <= pct <= 130 else "#c0392b"
                bar_w = min(pct, 100)
                return (
                    f'<div style="margin-bottom:0.65rem;">'
                    f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;color:#555;">'
                    f'<span><strong>{label}</strong></span>'
                    f'<span>{delivered:.0f}/{recommended:.0f} kg ({pct:.0f}%)</span>'
                    f'</div>'
                    f'<div style="background:#e0ece4;border-radius:6px;height:9px;margin-top:4px;overflow:hidden;">'
                    f'<div style="background:{color};width:{bar_w}%;height:100%;border-radius:6px;"></div>'
                    f'</div>'
                    f'</div>'
                )

            st.markdown(
            f'<div class="icard" style="margin-top:1rem;">'
            f'{_npk_bar("Nitrogen (N)", total_n * farm_area, RECOMMENDED_N * farm_area, n_pct)}'
            f'{_npk_bar("Phosphorus (P)", total_p * farm_area, RECOMMENDED_P * farm_area, p_pct)}'
            f'{_npk_bar("Potassium (K)", total_k * farm_area, RECOMMENDED_K * farm_area, k_pct)}'
            f'<p style="color:#aaa;font-size:0.73rem;margin-top:0.4rem;">Total across {farm_area} hectare(s) • Target range: 85% – 115%</p>'
            f'</div>',
            unsafe_allow_html=True)

        with right_col:
            st.markdown('<p class="res-header">🌱 Planting Density</p>', unsafe_allow_html=True)
            optimal_density    = CHROMOSOME_CONSTRAINTS['planting_density'][seed_variety]['optimal']
            recommended_density = best['planting_density']
            st.markdown(
            f'<div class="icard" style="text-align:center;">'
            f'<label style="color:#888;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.8px;">Recommended</label>'
            f'<p style="color:#2d6a4f;font-size:2rem;font-weight:700;margin:0.2rem 0;">{recommended_density:,.0f}</p>'
            f'<p style="color:#888;font-size:0.82rem;margin:0;">plants per hectare</p>'
            f'</div>',
            unsafe_allow_html=True)

            # Seed sacks display — use same CSV-based calculation as cost model
            # 1 sack = 9 kg (DA standard: Hybrid/OPV ≈ 2 bags, Glutinous ≈ 1 bag per ha)
            _sv = _seed_csv.loc[seed_variety]
            _total_seeds = best['planting_density'] * _sv["seeds_per_hill"] * farm_area
            seed_kg       = _total_seeds / _sv["seeds_per_kg"]
            seed_sacks    = seed_kg / 9  # 9 kg per sack (DA standard bag size)
            st.markdown(
            f'<div class="icard" style="margin-top:1rem;">'
            f'<h4>🌱 Seed Requirement</h4>'
            f'<p style="color:#2d6a4f;font-size:1.5rem;font-weight:700;margin:0.3rem 0;">{seed_sacks:.2f} sacks ({seed_kg:.1f} kg)</p>'
            f'<p style="color:#888;font-size:0.82rem;margin:0;">{_sv["row_spacing_cm"]:.0f} cm rows · {_sv["hill_spacing_cm"]:.0f} cm hill spacing · {_sv["seeds_per_hill"]:.1f} seed/hill</p>'
            f'</div>',
            unsafe_allow_html=True)

        st.markdown('<p class="res-header">💰 Cost Breakdown</p>', unsafe_allow_html=True)
        cb1, cb2 = st.columns([3, 2])

        with cb1:
            cost_items = [
                ("🌱 Seed Cost",        seed_cost),
                ("🧪 Fertilizer Cost",  fert_cost),
                ("🔧 Operational Cost", ops_cost),
            ]
            if herb_cost > 0:
                cost_items.append(("🧴 Herbicide Cost", herb_cost))

            cost_rows = "".join(
                f'<tr><td>{label}</td><td style="text-align:right;">{_format_peso(amount)}</td></tr>'
                for label, amount in cost_items
            )

            st.markdown(
            f'<table class="clean-table">'
            f'<tr><th>Expense</th><th style="text-align:right;">Amount</th></tr>'
            f'{cost_rows}'
            f'<tr><td>Total Cost</td><td style="text-align:right;">{_format_peso(total_cost)}</td></tr>'
            f'</table>',
            unsafe_allow_html=True)

        with cb2:
            # Breakdown operational costs with specific ordering
            variety_name = seed_variety  # seed_variety is already the variety name
            ops_breakdown_html = '<div style="margin-bottom:0.6rem;"><strong style="color:#2d6a4f;font-size:0.82rem;">Operational</strong>'
            
            if topography == "Plain":
                # Plain layout: Land Prep, Planting, Fert App 1, Fert App 2, (Herbicide/Weeding Labor), Harvesting
                items_order = [
                    ("Land Prep", 6000),
                    ("Planting", 5000),
                    ("Fert Application 1", 3000),
                    ("Fert Application 2", 3000),
                    ("Herbicide Labor" if variety_name == "Hybrid" else "Weeding Labor", 2000),
                    ("Harvesting", 10000),
                ]
            else:
                # Elevated layout: Planting, Fert App Labor, Herbicide Labor 1, Herbicide Labor 2, Harvesting
                items_order = [
                    ("Planting", 5000),
                    ("Fert Application", 6000),
                    ("Herbicide Labor 1", 2000),
                    ("Herbicide Labor 2", 2000),
                    ("Harvesting", 10000),
                ]
            
            for label, cost_per_ha in items_order:
                total_cost_item = cost_per_ha * farm_area
                ops_breakdown_html += f'<div style="display:flex;justify-content:space-between;font-size:0.75rem;color:#666;margin-top:0.25rem;"><span>{label}</span><span>{_format_peso(total_cost_item)}</span></div>'
            
            ops_breakdown_html += f'<div style="display:flex;justify-content:space-between;font-size:0.77rem;font-weight:600;color:#2d6a4f;margin-top:0.35rem;border-top:1px solid #dde8e1;padding-top:0.35rem;"><span>Subtotal</span><span>{_format_peso(ops_cost)}</span></div></div>'
            
            # Herbicide breakdown
            herbicide_html = '<div><strong style="color:#2d6a4f;font-size:0.82rem;">Herbicide</strong>'
            if seed_variety == "Hybrid":
                gallon_req = cost_model.HERBICIDE_GALLONS_REQUIRED[topography]
                gallon_cost = cost_model.HERBICIDE_COST_PER_GALLON
                herbicide_html += f'<div style="display:flex;justify-content:space-between;font-size:0.75rem;color:#666;margin-top:0.25rem;"><span>{gallon_req} gal × ₱{gallon_cost:,.0f}/gal</span><span>{_format_peso(gallon_cost * gallon_req * farm_area)}</span></div>'
                herbicide_html += f'<div style="display:flex;justify-content:space-between;font-size:0.77rem;font-weight:600;color:#2d6a4f;margin-top:0.35rem;border-top:1px solid #dde8e1;padding-top:0.35rem;"><span>Subtotal</span><span>{_format_peso(herb_cost)}</span></div>'
            else:
                herbicide_html += f'<div style="font-size:0.75rem;color:#999;margin-top:0.25rem;font-style:italic;">N/A ({seed_variety} variety)</div>'
            herbicide_html += '</div>'
            
            st.markdown(
            f'<div class="icard">'
            f'{ops_breakdown_html}'
            f'<div style="border-top:1px solid #dde8e1;padding-top:0.75rem;margin-top:0.75rem;">'
            f'{herbicide_html}'
            f'</div></div>',
            unsafe_allow_html=True)

        st.markdown('<p class="res-header">📋 Your Farm Conditions</p>', unsafe_allow_html=True)
        season     = _season_label(planting_month)
        irrig_text = "Yes" if irrigation == "Yes" else "No"

        st.markdown(
        f'<div class="summary-grid">'
        f'<div class="icard"><h4>Farm Details</h4><p>'
        f'<strong>Area:</strong> {farm_area} hectare(s)<br>'
        f'<strong>Variety:</strong> {seed_variety}<br>'
        f'<strong>Land Type:</strong> {topography}</p></div>'
        f'<div class="icard"><h4>Soil Conditions</h4><p>'
        f'<strong>Type:</strong> {soil_type}<br>'
        f'<strong>pH:</strong> {soil_ph}<br>'
        f'<strong>NPK:</strong> {initial_n}–{initial_p}–{initial_k} kg/ha</p></div>'
        f'<div class="icard"><h4>Planting</h4><p>'
        f'<strong>Month:</strong> {MONTH_NAMES[planting_month]}<br>'
        f'<strong>Season:</strong> {season}<br>'
        f'<strong>Irrigation:</strong> {irrig_text}</p></div>'
        f'</div>',
        unsafe_allow_html=True)

        st.markdown(
        '<div class="disclaimer">Results are estimates based on DA Region 6 data (2026). '
        'Actual yields may vary depending on weather, pest outbreaks, and farming practices. '
        'Corn market price: ₱17/kg.</div>',
        unsafe_allow_html=True)

