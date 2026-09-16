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

## 🗂️ Repository Architecture

```text
BESS_co_optimization_with_afrr/
│
├── .gitignore
├── README.md                       # Comprehensive project documentation
├── requirements.txt                # Python dependencies
├── app.py                          # Streamlit interactive web dashboard
│
├── data/
│   ├── german_market_sample.csv    # Optimized market dispatch results & prices (CSV)
│   └── industrial_load_profile.csv # Industrial consumption load curves
│
├── src/
│   ├── __init__.py
│   ├── engine.py                   # Core MILP co-optimization engine (PuLP / CBC)
│   └── utils.py                    # Financial calculation & export helpers
│
├── tests/
│   ├── __init__.py
│   ├── test_market_data.py         # Schema and data integrity tests
│   └── test_optimization.py        # SoC bounds, binary logic, and solver feasibility tests
│
└── assets/
    ├── german_bess_co_optimization_dark.png # High-resolution analytical chart
    └── bess_dispatch_animation.gif          # 24-hour animated dispatch sequence
