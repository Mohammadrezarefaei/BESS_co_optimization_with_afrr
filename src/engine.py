import pandas as pd
import numpy as np
import pulp

def generate_german_market_data(time_steps: int = 24) -> pd.DataFrame:
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
    time_steps = int(len(market_df))
    time_index = list(range(time_steps))
    
    model = pulp.LpProblem("German_BESS_Co_Optimization", pulp.LpMaximize)
    
    max_p = float(max_power_mw)
    cap_e = float(capacity_mwh)
    
    # تعریف متغیرها به روش کلاسیک و امن برای جلوگیری از TypeError در سرورهای ابری
    P_ch = {}
    P_dis = {}
    aFRR_cap = {}
    SoC = {}
    
    for t in time_index:
        P_ch[t] = pulp.LpVariable(name="P_ch_" + str(t), lowBound=0.0, upBound=max_p, cat="Continuous")
        P_dis[t] = pulp.LpVariable(name="P_dis_" + str(t), lowBound=0.0, upBound=max_p, cat="Continuous")
        aFRR_cap[t] = pulp.LpVariable(name="aFRR_cap_" + str(t), lowBound=0.0, upBound=max_p, cat="Continuous")
        SoC[t] = pulp.LpVariable(name="SoC_" + str(t), lowBound=0.0, upBound=cap_e, cat="Continuous")
        
    Net_Peak = pulp.LpVariable(name="Net_Peak", lowBound=0.0, cat="Continuous")
    
    efficiency = 0.88
    eta = float(np.sqrt(efficiency))
    
    da_revenue = pulp.lpSum([(P_dis[t] - P_ch[t]) * float(market_df.loc[t, "DA_Price_EUR_MWh"]) for t in time_index])
    afrr_revenue = pulp.lpSum([aFRR_cap[t] * float(market_df.loc[t, "aFRR_Price_EUR_MW"]) for t in time_index])
    penalty_cost = Net_Peak * float(grid_fee_penalty_rate)
    
    model += (da_revenue + afrr_revenue - penalty_cost)
    
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
    
    model.solve(pulp.PULP_CBC_CMD(msg=False))
    
    results_df = market_df.copy()
    
    # استخراج امن مقادیر برای جلوگیری از خطای NoneType
    def get_val(var):
        val = var.varValue
        return float(val) if val is not None else 0.0
        
    results_df["Optimized_Charge_MW"] = [get_val(P_ch[t]) for t in time_index]
    results_df["Optimized_Discharge_MW"] = [get_val(P_dis[t]) for t in time_index]
    results_df["aFRR_Reserved_MW"] = [get_val(aFRR_cap[t]) for t in time_index]
    results_df["SoC_MWh"] = [get_val(SoC[t]) for t in time_index]
    results_df["Net_Grid_Load_MW"] = results_df["Industrial_Load_MW"] + results_df["Optimized_Charge_MW"] - results_df["Optimized_Discharge_MW"]
    
    return results_df
