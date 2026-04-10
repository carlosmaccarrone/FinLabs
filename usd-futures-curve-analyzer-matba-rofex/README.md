# USD Futures Curve Analyzer (MATBA-ROFEX)

This Python script builds and analyzes the USD futures curve using contracts data (e.g. DLR) and spot FX.

---

## Features

- Extracts and cleans futures data directly from Matba-Rofex Excel files.  
- Automatically detects spot FX (Dólar UST ART 000).  
- Calculates:  
  - TTM (Time to Maturity) in years.  
  - TEA (Tasa Efectiva Anual).  
  - TEM (Tasa Efectiva Mensual).  
  - ΔTEM (slope between contracts).  
- Fits a smooth futures curve using weighted splines:  
  - Weights based on traded volume.  
- Computes:
  - Theoretical curve (fair value).  
  - Mispricing (%) vs curve.
  - Mispricing in ARS.
- Visualization:  
  - TEA vs TTM scatter plot.  
  - Smoothed curve (yellow line).  
  - Contracts labeled with ticker + TEA.  
- Uses:
  - `pandas` & `openpyxl` for data processing.  
  - `scipy` to calculate spline curve.  
  - `matplotlib` for visualization.  
- Built as an **educational, clean example** of financial data analysis and plotting in Python.

---

## Requirements

```bash
pip install pandas numpy matplotlib scipy openpyxl
```

## Usage

Run the script and provide the Excel file exported from Matba-Rofex:  
E.G.: https://www.rofex.com.ar/Herramientas/Descargas/New/CierreParcialA3Mercados%E2%80%93Monedas09042026.xlsx

Then input:

```bash
Ingrese nombre archivo con extension: cierre.xlsx
```

## Analysis Details

1. Time to Maturity (TTM)  
Computed as the fraction of time between current market time and contract maturity:  
```bash
TTM = (maturity - now) / 365
```

2. TEA Calculation  
```bash
TEA = (Future Price / Spot)^(1 / TTM) - 1
```
Represents the implied annualized rate of the futures contract.  

3. Curve Construction  
- Uses log transformation:  
```bash
y = log(Future / Spot)
```
- Fits a Univariate Spline:  
  - Weighted by √volume (more liquidity → more influence).  
  - Smoothness controlled via parameter s.  

4. Fair Value  
The theoretical price is reconstructed from the curve:  
```bash
Fair Price = Spot * exp(curve_value)
```

5. Mispricing  
```bash
Mispricing (%) = TEA_real - TEA_curve
Mispricing ($) = Market Price - Fair Price
```
Used to detect relative value opportunities across contracts.  

6. Filtering by Liquidity  
Contracts with low volume are filtered out (e.g. Vol > 9000) for ranking:  
```bash
Top: most expensive vs curve  
Bottom: cheapest vs curve
```

---

## Author

Carlos Maccarrone  
Date: 2026-04-08

---

## Notes
- Designed for futures curve analysis in ARS/USD markets.  
-  Useful for:  
  - Relative value trading.  
  - Detecting distortions in the curve.  
  - Understanding term structure dynamics.  
- Educational example of:  
  - Financial modeling  
  - Curve fitting  
  - Data visualization in Python  