import pandas as pd
import numpy as np
import pulp

def generate_german_market_data(time_steps: int = 24) -> pd.DataFrame:
    """
    Generates synthetic but realistic German market data for 24 hours.
    Includes Day-Ahead prices, aFRR capacity prices, and an industrial load profile.
    """
    np.random.seed(42)
    time_index = range(time_steps)
    
    da_prices = (
        40 
        + 20 * np.sin(np.pi * np.array(time_index) / 12) 
        + 30 * np.exp(-0.5 * ((np.array(time_index) - 19) / 2)**2) 
        - 40 * np.exp(-0.5 * ((np.array(time_index) - 13) / 2)**2)
    )
    
    afrr_prices = 15 + 5 * np.random.rand(time_steps)
    industrial_load = 10 + 5 * np.sin(np.pi * np.array(time_index) / 8) + np.random.rand(time_steps) * 2
    
    df = pd.DataFrame({
        "Timestamp": pd.date_range(start="2026-10-06", periods=time_steps, freq="h"),
        "DA_Price_EUR_MWh": da_prices,
        "aFRR_Price_EUR_MW": afrr_prices,
        "Industrial_Load_MW": np.maximum(industrial_load, 0)
    })
    
    return df

def run_co_optimization_with_afrr(market_df: pd.DataFrame, capacity_mwh: float, max_power_mw: float, grid_fee_penalty_rate: float) -> pd.DataFrame:
    """
    MILP Optimization Engine using PuLP for co-optimizing Day-Ahead arbitrage,
    aFRR capacity provision, and peak shaving.
    """
    time_steps = int(len(market_df))
    time_index = list(range(time_steps))
    
    model = pulp.LpProblem("German_BESS_Co_Optimization", pulp.LpMaximize)
    
    max_p = float(max_power_mw)
    cap_e = float(capacity_mwh)
    
    P_ch = {}
    P_dis = {}
    aFRR_cap = {}
    SoC = {}
    
    # 100% Bulletproof: Using strict positional arguments to prevent TypeError on Streamlit Cloud
    # Arguments order: name, lowBound, upBound, cat
    for t in time_index:
        P_ch[t] = pulp.LpVariable(f"P_ch_{t}", 0.0, max_p, "Continuous")
        P_dis[t] = pulp.LpVariable(f"P_dis_{t}", 0.0, max_p, "Continuous")
        aFRR_cap[t] = pulp.LpVariable(f"aFRR_cap_{t}", 0.0, max_p, "Continuous")
        SoC[t] = pulp.LpVariable(f"SoC_{t}", 0.0, cap_e, "Continuous")
        
    # Net_Peak is unconstrained on the upper bound, so upBound is passed as None
    Net_Peak = pulp.LpVariable("Net_Peak", 0.0, None, "Continuous")
    
    efficiency = 0.88
    eta = float(np.sqrt(efficiency))
    
    # Objective Function
    da_revenue = pulp.lpSum([(P_dis[t] - P_ch[t]) * float(market_df.loc[t, "DA_Price_EUR_MWh"]) for t in time_index])
    afrr_revenue = pulp.lpSum([aFRR_cap[t] * float(market_df.loc[t, "aFRR_Price_EUR_MW"]) for t in time_index])
    penalty_cost = Net_Peak * float(grid_fee_penalty_rate)
    
    model += (da_revenue + afrr_revenue - penalty_cost)
    
    # Constraints
    for t in time_index:
        model += P_ch[t] + aFRR_cap[t] <= max_p
        model += P_dis[t] + aFRR_cap[t] <= max_p
        
        net_load_t = float(market_df.loc[t, "Industrial_Load_MW"]) + P_ch[t] - P_dis[t]
        model += Net_Peak >= net_load_t
        
        if t == 0:
            model += SoC[t] == (0.5 * cap_e) + (P_ch[t] * eta) - (P_dis[t] / eta)
        else:
            model += SoC[t] == SoC[t-1] + (P_ch[t] * eta) - (P_dis[t] / eta)
            
        model += SoC[t] >= aFRR_cap[t] / eta
        model += SoC[t] <= cap_e - (aFRR_cap[t] * eta)
    
    # Solve the model silently
    model.solve(pulp.PULP_CBC_CMD(msg=False))
    
    results_df = market_df.copy()
    
    # Helper to safely extract float values
    def get_val(var):
        val = var.varValue
        return float(val) if val is not None else 0.0
        
    results_df["Optimized_Charge_MW"] = [get_val(P_ch[t]) for t in time_index]
    results_df["Optimized_Discharge_MW"] = [get_val(P_dis[t]) for t in time_index]
    results_df["aFRR_Reserved_MW"] = [get_val(aFRR_cap[t]) for t in time_index]
    results_df["SoC_MWh"] = [get_val(SoC[t]) for t in time_index]
    results_df["Net_Grid_Load_MW"] = results_df["Industrial_Load_MW"] + results_df["Optimized_Charge_MW"] - results_df["Optimized_Discharge_MW"]
    
    return results_df
