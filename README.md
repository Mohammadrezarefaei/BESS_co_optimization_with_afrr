# ⚡ Utility-Scale BESS Co-Optimization & Revenue Stacking in German Markets

[![Streamlit App](https://img.shields.io/badge/Streamlit-App-red?style=for-the-badge&logo=streamlit)](https://besscooptimizationwithafrr-jkq92wbjpfnwquluemghnj.streamlit.app/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Tests Passed](https://img.shields.io/badge/pytest-passing-success.svg?style=for-the-badge&logo=pytest)](https://docs.pytest.org/)

An advanced **Mixed-Integer Linear Programming (MILP)** optimization engine designed for utility-scale Battery Energy Storage Systems (BESS) operating in the German energy market. The model optimizes **Revenue Stacking** across multiple revenue streams: **EPEX Spot Day-Ahead Market**, **aFRR (Automatic Frequency Restoration Reserve / Regelleistung)** capacity reservation, and **Industrial Peak Shaving (§ 19 StromNEV)**.

---

## 📊 Live Interactive Dashboard & Visualizations

Explore the live web application: [Streamlit Cloud App](https://besscooptimizationwithafrr-jkq92wbjpfnwquluemghnj.streamlit.app/)

### 📈 24-Hour Multi-Layer Dispatch Profile
<p align="center">
  <img src="https://raw.githubusercontent.com/Mohammadrezarefaei/BESS_co_optimization_with_afrr/main/assets/german_bess_co_optimization_dark.png" alt="German BESS Co-Optimization Dark Chart" width="100%">
</p>

### 🎬 Chronological Dispatch Animation
<p align="center">
  <img src="https://raw.githubusercontent.com/Mohammadrezarefaei/BESS_co_optimization_with_afrr/main/assets/bess_dispatch_animation.gif" alt="BESS Dispatch Animation GIF" width="100%">
</p>

---

## 📋 Optimization Results & CSV Data Table Preview

The following table represents the exact snapshot of `data/german_bess_co_optimization_results.csv`, containing optimized Day-Ahead prices, aFRR capacity reservations, power dispatches, and battery State of Charge (SoC):

| Timestamp | DA Price (€/MWh) | aFRR Cap Price (€/MW/h) | Discharge (MW) | aFRR Reserved (MW) | SoC (MWh) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **2026-06-01 00:00:00** | 84.97 | 33.37 | 0.00 | 5.00 | 5.00 |
| **2026-06-01 01:00:00** | 89.41 | 34.96 | 0.00 | 5.00 | 5.00 |
| **2026-06-01 02:00:00** | 107.26 | 30.09 | 0.00 | 5.00 | 5.00 |
| **2026-06-01 03:00:00** | 124.46 | 32.95 | 0.00 | 5.00 | 5.00 |
| **2026-06-01 04:00:00** | 113.17 | 27.80 | 0.00 | 5.00 | 5.00 |
| **2026-06-01 05:00:00** | 116.82 | 26.16 | 0.00 | 5.00 | 5.00 |
| **2026-06-01 06:00:00** | 135.70 | 23.88 | 3.61 | 1.39 | 5.00 |
| **2026-06-01 07:00:00** | 125.36 | 33.91 | 0.21 | 4.79 | 1.08 |
| **2026-06-01 08:00:00** | 107.98 | 30.73 | 0.00 | 5.00 | 0.84 |
| **2026-06-01 09:00:00** | 110.67 | 29.58 | 0.00 | 5.00 | 0.84 |

---

## 🗂️ Repository Architecture

```text
BESS_co_optimization_with_afrr/
│
├── .gitignore
├── BESS_co_optimization_with_afrr.ipynb
├── README.md                       # Comprehensive project documentation
├── requirements.txt                # Python dependencies
├── app.py                          # Streamlit interactive web dashboard
│
├── assets/
│   ├── bess_dispatch_animation.gif         # 24-hour animated dispatch sequence
│   └── german_bess_co_optimization_dark.png # High-resolution analytical chart
│
├── data/
│   ├── german_bess_co_optimization_results.csv # Optimized market dispatch results & prices (CSV)
│   └── industrial_load_profile.csv             # Industrial consumption load curves
│
├── src/
│   ├── __init__.py
│   ├── engine.py                               # Core MILP co-optimization engine (PuLP / CBC)
│   └── utils.py                                # Financial calculation & export helpers
│
└── tests/
    ├── __init__.py
    ├── test_market_data.py                     # Schema and data integrity tests
    └── test_optimization.py                    # SoC bounds, binary logic, and solver feasibility tests
