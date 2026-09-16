import plotly.express as px
import streamlit as st
from src.engine import generate_german_market_data, run_co_optimization_with_afrr
from src.utils import calculate_financial_summary

# Streamlit configuration
st.set_page_config(
    page_title="German BESS Co-Optimization & aFRR",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚡ German BESS Co-Optimization: Day-Ahead, aFRR & Peak Shaving")
st.markdown(
    "Advanced MILP optimization engine for utility-scale BESS operating in"
    " European energy markets (§ 19 StromNEV & Regelleistung)."
)

# Sidebar controls
st.sidebar.header("Configuration")
bess_capacity = st.sidebar.slider("BESS Capacity (MWh)", 2.0, 50.0, 10.0)
bess_power = st.sidebar.slider("Max Power (MW)", 1.0, 25.0, 5.0)
penalty_rate = st.sidebar.number_input("Grid Fee Penalty Rate (€/MW)", value=150.0)

# Run optimization engine
market_df = generate_german_market_data()
results = run_co_optimization_with_afrr(
    market_df,
    capacity_mwh=bess_capacity,
    max_power_mw=bess_power,
    grid_fee_penalty_rate=penalty_rate,
)

# Financial summary metrics
fin_summary = calculate_financial_summary(results)

col1, col2, col3, col4 = st.columns(4)
col1.metric("DA Market Revenue", f"€{fin_summary['DA_Revenue_EUR']:,.2f}")
col2.metric("aFRR Capacity Revenue", f"€{fin_summary['aFRR_Revenue_EUR']:,.2f}")
col3.metric("Combined Daily Revenue", f"€{fin_summary['Total_Revenue_EUR']:,.2f}")
col4.metric("Optimized Net Peak", f"{results['Net_Grid_Load_MW'].max():.2f} MW")

st.markdown("---")

# Plotly interactive chart with dark theme legend fix
st.subheader("📊 24-Hour Multi-Layer Dispatch Profile")

fig = px.line(
    results,
    y=[
        "Industrial_Load_MW",
        "Net_Grid_Load_MW",
        "Optimized_Discharge_MW",
        "aFRR_Reserved_MW",
    ],
    labels={"value": "Power / Capacity (MW)", "Timestamp": "Time"},
    title="Power Dispatch & aFRR Capacity Reservation",
)

fig.update_layout(
    legend=dict(
        font=dict(color="black", size=12),
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="black",
        borderwidth=1,
    ),
    template="plotly_dark",
    hovermode="x unified",
)

st.plotly_chart(fig, use_container_width=True)

st.success(
    "Optimization pipeline executed successfully with revenue stacking!"
)
