# MEP Analyzer for AL30/AL30D Bonds

This Python script analyzes and visualizes the **MEP (Mercado Electrónico de Pagos) exchange rate** using AL30 (ARS) and AL30D (USD) bond prices.

---

## Features

- Calculates **MEP** from AL30 and AL30D prices.
- Uses **EWMA (Exponentially Weighted Moving Average)** to model dynamic mean and volatility.
- Plots:
  - Historical MEP values.
  - EWMA mean and deviation bands (±1σ).
  - Daily traded volume (AL30D).
  - Market flow dominance (buy/sell signals).
  - "Sweet spot" zones for potential buying/selling opportunities.
  - Highlighted periods of possible market intervention.
- Uses:
  - `pandas` for data processing.
  - `numpy` for numerical operations.
  - `matplotlib` for visualization.
- Designed as a **lightweight analytical tool** to quickly review market behavior over time.

---

## Requirements

```bash
pip install pandas matplotlib numpy

```

---

## Usage

Windows: run the analisisMep.bat file from your desktop.

Linux/macOS: run in terminal:

```bash
python analisisMep.py
```

---

## Analysis Details

1. MEP Calculation:
```bash
MEP = PRICE_AL30 / PRICE_AL30D
```
2. EWMA-Based Z-score  
  - Measures deviation from a dynamic mean.  
  - Adapts to recent market conditions.  
3. Sweet Spots  
  - Z-score < -1 → potential buy zone  
  - Z-score > 1 → potential sell zone  
4. Inferred Flow  
  - Combines Z-score and volume (EWMA-based) to identify dominant market pressure.  
5. Interventions  
  - Days with high volume and low price deviation are flagged as potential interventions.  
6. Visualization:
	- MEP time series.  
	- EWMA mean and ±1σ bands.  
	- AL30D volume bars.  
	- Flow annotations:  
    - ```c``` → buy  
    - ```v``` → sell  
  - Highlighted zones for potential interventions.  

---

## Author

Carlos Maccarrone  
Date: 2025-08-15

---

## Note

This script is intended for **exploratory and educational analysis**.  
It provides a high-level view of market dynamics rather than a trading system.  