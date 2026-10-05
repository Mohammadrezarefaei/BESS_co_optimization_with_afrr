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
    
    # FIX: Wrapped in parentheses instead of backslash (\) to prevent copy-paste SyntaxErrors
    da_prices = (
        40 
        + 20 * np.sin(np.pi * np.array(time_index) / 12) 
        + 30 * np.exp(-0.5 * ((np.array(time_index) - 19) / 2)**2) 
        - 40 * np.exp(-0.5 * ((np.array(time_index) - 13) / 2)**2)
    )
    
    # Synthetic aFRR Capacity Prices (relatively stable with slight variations)
    afrr_prices = 15 + 5 * np.random.rand(time_steps)
    
    # Industrial Base Load Profile (MW) - consistent baseload with shift peaks
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
    aFRR capacity provision, and peak shaving (§ 19 StromNEV).
    """
    time_steps = int(len(market_df))
    time_index = list(range(time_steps))
    
    # Initialize the LP Problem
    model = pulp.LpProblem("German_BESS_Co_Optimization", pulp.LpMaximize)
    
    max_p = float(max_power_mw)
    cap_e = float(capacity_mwh)
    
    # Decision Variables
    P_ch = pulp.LpVariable.dicts("P_ch", time_index, lowBound=0, upBound=max_p, cat="Continuous")
    P_dis = pulp.LpVariable.dicts("P_dis", time_index, lowBound=0, upBound=max_p, cat="Continuous")
    aFRR_cap = pulp.LpVariable.dicts("aFRR_cap", time_index, lowBound=0, upBound=max_p, cat="Continuous")
    SoC = pulp.LpVariable.dicts("SoC", time_index, lowBound=0, upBound=cap_e, cat="Continuous")
    Net_Peak = pulp.LpVariable("Net_Peak", lowBound=0, cat="Continuous")
    
    # Constants
    efficiency = 0.88
    eta = float(np.sqrt(efficiency))
    
    # Objective Function
    da_revenue = pulp.lpSum([(P_dis[t] - P_ch[t]) * market_df.loc[t, "DA_Price_EUR_MWh"] for t in time_index])
    afrr_revenue = pulp.lpSum([aFRR_cap[t] * market_df.loc[t, "aFRR_Price_EUR_MW"] for t in time_index])
    penalty_cost = Net_Peak * float(grid_fee_penalty_rate)
    
    model += (da_revenue + afrr_revenue - penalty_cost)
    
    # Constraints
    for t in time_index:
        # Power & Reservation Constraints
        model += P_ch[t] + aFRR_cap[t] <= max_p
        model += P_dis[t] + aFRR_cap[t] <= max_p
        
        # Net Load and Peak Shaving Constraint
        net_load_t = market_df.loc[t, "Industrial_Load_MW"] + P_ch[t] - P_dis[t]
        model += Net_Peak >= net_load_t
        
        # State of Charge (SoC) Balance
        if t == 0:
            model += SoC[t] == (0.5 * cap_e) + (P_ch[t] * eta) - (P_dis[t] / eta)
        else:
            model += SoC[t] == SoC[t-1] + (P_ch[t] * eta) - (P_dis[t] / eta)
            
        # aFRR Energy Constraints
        model += SoC[t] >= aFRR_cap[t] / eta
        model += SoC[t] <= cap_e - (aFRR_cap[t] * eta)
    
    # Solve the model
    model.solve(pulp.PULP_CBC_CMD(msg=False))
    
    # Extract Results
    results_df = market_df.copy()
    results_df["Optimized_Charge_MW"] = [P_ch[t].varValue for t in time_index]
    results_df["Optimized_Discharge_MW"] = [P_dis[t].varValue for t in time_index]
    results_df["aFRR_Reserved_MW"] = [aFRR_cap[t].varValue for t in time_index]
    results_df["SoC_MWh"] = [SoC[t].varValue for t in time_index]
    results_df["Net_Grid_Load_MW"] = results_df["Industrial_Load_MW"] + results_df["Optimized_Charge_MW"] - results_df["Optimized_Discharge_MW"]
    
    return results_df
