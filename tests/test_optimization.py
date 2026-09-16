import pytest
import pandas as pd
from src.engine import run_co_optimization_with_afrr

def test_optimization_execution():
    # Generate dummy test data
    df = pd.DataFrame({
        "Timestamp": pd.date_range("2026-06-01", periods=24, freq="h"),
        "DA_Price_EUR_MWh": [100.0] * 24,
        "aFRR_Cap_Price_EUR_MW": [30.0] * 24,
        "Industrial_Load_MW": [5.0] * 24
    })
    
    results = run_co_optimization_with_afrr(df, capacity_mwh=10.0, max_power_mw=5.0)
    
    # Assertions to ensure valid output structure
    assert "Optimized_Discharge_MW" in results.columns
    assert "aFRR_Reserved_MW" in results.columns
    assert len(results) == 24

def test_soc_and_power_boundaries():
    df = pd.DataFrame({
        "Timestamp": pd.date_range("2026-06-01", periods=10, freq="h"),
        "DA_Price_EUR_MWh": [80.0] * 10,
        "aFRR_Cap_Price_EUR_MW": [25.0] * 10,
        "Industrial_Load_MW": [4.0] * 10
    })
    
    capacity = 10.0
    max_power = 5.0
    results = run_co_optimization_with_afrr(df, capacity_mwh=capacity, max_power_mw=max_power)
    
    # Check if SoC respects battery limits
    assert results["SoC_MWh"].min() >= 0.0
    assert results["SoC_MWh"].max() <= capacity
    
    # Check if power limits are respected
    assert results["Optimized_Discharge_MW"].max() <= max_power
    assert results["aFRR_Reserved_MW"].max() <= max_power
