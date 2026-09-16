import pandas as pd
import pulp
import numpy as np


def generate_german_market_data(num_hours=24):
  """Generates synthetic German market data including DA prices,

  aFRR capacity prices, and industrial load profiles.
  """
  timestamps = pd.date_range(start="2026-06-01 00:00:00", periods=num_hours, freq="h")
  da_prices = 80 + 40 * np.sin(np.linspace(0, 2 * np.pi, num_hours)) + np.random.normal(0, 10, num_hours)
  afrr_prices = 25 + 10 * np.abs(np.cos(np.linspace(0, 2 * np.pi, num_hours))) + np.random.normal(0, 3, num_hours)
  industrial_load = 5 + 2 * np.sin(np.linspace(0, 2 * np.pi, num_hours) - 1) + np.random.normal(0, 0.5, num_hours)

  df = pd.DataFrame({
      "Timestamp": timestamps,
      "DA_Price_EUR_MWh": da_prices,
      "aFRR_Cap_Price_EUR_MW": afrr_prices,
      "Industrial_Load_MW": industrial_load
  })
  return df


def run_co_optimization_with_afrr(
    df: pd.DataFrame,
    capacity_mwh: float = 10.0,
    max_power_mw: float = 5.0,
    grid_fee_penalty_rate: float = 150.0,
):
  """Runs MILP co-optimization for EPEX Day-Ahead, aFRR capacity,

  and Industrial Peak Shaving (§ 19 StromNEV).
  """
  model = pulp.LpProblem("BESS_DA_aFRR_CoOptimization", pulp.LpMaximize)
  time_steps = len(df)

  # Decision Variables
  P_ch = {t: pulp.LpVariable(f"P_ch_{t}", lowBound=0, upBound=max_power_mw) for t in range(time_steps)}
  P_dis = {t: pulp.LpVariable(f"P_dis_{t}", lowBound=0, upBound=max_power_mw) for t in range(time_steps)}
  P_afrr = {t: pulp.LpVariable(f"P_afrr_{t}", lowBound=0, upBound=max_power_mw) for t in range(time_steps)}
  
  u_dis = {t: pulp.LpVariable(f"u_dis_{t}", cat="Binary") for t in range(time_steps)}
  
  SoC = {t: pulp.LpVariable(f"SoC_{t}", lowBound=0, upBound=capacity_mwh) for t in range(time_steps + 1)}
  P_peak_grid = pulp.LpVariable("P_peak_grid", lowBound=0, upBound=max_power_mw * 3)

  # Initial State of Charge
  model += SoC[0] == capacity_mwh * 0.5

  # Objective Function: Revenue Stacking (DA + aFRR - Grid Peak Penalty)
  revenue_da = pulp.lpSum((P_dis[t] - P_ch[t]) * df.loc[t, "DA_Price_EUR_MWh"] for t in range(time_steps))
  revenue_afrr = pulp.lpSum(P_afrr[t] * df.loc[t, "aFRR_Cap_Price_EUR_MW"] for t in range(time_steps))
  penalty_grid = P_peak_grid * grid_fee_penalty_rate

  model += revenue_da + revenue_afrr - penalty_grid

  eff = 0.92  # Round-trip efficiency

  for t in range(time_steps):
    # Mutual exclusivity of charging and discharging
    model += P_dis[t] <= max_power_mw * u_dis[t]
    model += P_ch[t] <= max_power_mw * (1 - u_dis[t])

    # Power headroom constraints for aFRR reservation
    model += P_dis[t] + P_afrr[t] <= max_power_mw
    model += P_ch[t] + P_afrr[t] <= max_power_mw

    # State of Charge dynamics
    if t < time_steps - 1:
      model += SoC[t + 1] == SoC[t] + (P_ch[t] * eff - P_dis[t] / eff) * 1.0

    # Grid peak tracking for § 19 StromNEV
    industrial_load = df.loc[t, "Industrial_Load_MW"]
    net_grid_load = industrial_load + P_ch[t] - P_dis[t]
    model += P_peak_grid >= net_grid_load

  # Solve model using CBC solver
  model.solve(pulp.PULP_CBC_CMD(msg=0))

  # Extract results into DataFrame
  results_df = df.copy()
  results_df["Optimized_Discharge_MW"] = [pulp.value(P_dis[t]) for t in range(time_steps)]
  results_df["Optimized_Charge_MW"] = [pulp.value(P_ch[t]) for t in range(time_steps)]
  results_df["aFRR_Reserved_MW"] = [pulp.value(P_afrr[t]) for t in range(time_steps)]
  results_df["SoC_MWh"] = [pulp.value(SoC[t]) for t in range(time_steps)]
  results_df["Net_Grid_Load_MW"] = (
      results_df["Industrial_Load_MW"]
      + results_df["Optimized_Charge_MW"]
      - results_df["Optimized_Discharge_MW"]
  )

  return results_df
