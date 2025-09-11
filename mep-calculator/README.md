# MEP Analyzer for AL30/AL30D Bonds

This Python script analyzes and visualizes the **MEP (Mercado Electrónico de Pagos) exchange rate** using AL30 (ARS) and AL30D (USD) bond prices.

---

## Features

- Calculates **MEP** from AL30 and AL30D prices.
- Plots:
  - Historical MEP values.
  - Daily traded volume.
  - Market flow dominance (buy/sell signals).
  - "Sweet spot" zones for optimal buying/selling opportunities.
  - RSI-style visualization for intuitive market timing.
- Uses:
  - `pandas` for data processing.
  - `scipy` to detect sweet spots.
  - `matplotlib` for visualization.
- Built as an **educational, clean example** of financial data analysis and plotting in Python.

---

## Requirements

```bash
pip install pandas scipy matplotlib
```

## Usage

Windows: run the analisisMep.bat file from your desktop.

Linux/macOS: run in terminal:

```bash
python analisisMep.py
```

## Analysis Details

1. MEP Calculation:
```bash
MEP = PRICE_AL30 / PRICE_AL30D
```
2. MEP Z-score: detects extreme values and possible buy/sell opportunities.
3. Sweet Spots: points where MEP is significantly low (buy) or high (sell).
4. Inferred Flow: combines Z-score and volume to mark potential buy/sell events.
5. Interventions: days with unusual volume and minimal price deviation are flagged as possible market interventions
6. Visualization:
	- MEP line and standard deviation bands.
	- AL30D volume bars.
	- Flow annotations (“c” for buy, “v” for sell).
	- Yellow areas for potential interventions.

## Author

Carlos Maccarrone  
Date: 2025-08-15

---

## Note

This script is educational and for financial analysis purposes, ideal as an example of Python data processing and plotting.