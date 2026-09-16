import pandas as pd


def export_results_to_csv(results_df: pd.DataFrame, filepath: str = "german_bess_optimization_results.csv"):
  """Exports optimization results dataframe to a CSV file."""
  results_df.to_csv(filepath, index=False)
  print(f"Results successfully exported to {filepath}")


def calculate_financial_summary(results_df: pd.DataFrame):
  """Calculates total revenues from Day-Ahead and aFRR markets."""
  da_revenue = ((results_df["Optimized_Discharge_MW"] - results_df["Optimized_Charge_MW"]) * results_df["DA_Price_EUR_MWh"]).sum()
  afrr_revenue = (results_df["aFRR_Reserved_MW"] * results_df["aFRR_Cap_Price_EUR_MW"]).sum()
  
  return {
      "DA_Revenue_EUR": da_revenue,
      "aFRR_Revenue_EUR": afrr_revenue,
      "Total_Revenue_EUR": da_revenue + afrr_revenue
  }
