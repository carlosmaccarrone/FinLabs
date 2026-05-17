# USD Futures Curve Analyzer (Nelson–Siegel with Front-End Stabilization)

This project builds and analyzes the USD futures curve using market data from MATBA-ROFEX, using a single structural framework based on a calibrated Nelson–Siegel model with front-end stabilization.  

- The model focuses on:  
  - Term structure estimation  
  - Relative-value mispricing  
  - Liquidity-aware weighting  
  - Curve shape diagnostics   

---

## Features

- Extracts and cleans futures data directly from MATBA-ROFEX Excel files.  
- Automatically detects spot FX (`Dólar UST ART 000`).  
- Business-day adjusted time modeling using an external holiday calendar.  
- Calculates:  
  - TTM (Time to Maturity, business days adjusted).  
  - TEA (Tasa Efectiva Anual).  
  - TEM (Tasa Efectiva Mensual).   
  - TNA (Nominal Annual Rate approximation).  
  - Contract spread structure.  
  - Spread acceleration / deceleration (`SpdDff`).  
  - Previous session spread comparison (`PvSpd`).  
- Curve modeling:    
  - **Nelson–Siegel model (structural model)**  
- Relative value analytics:   
  - Fair value estimation.  
  - Log-space mispricing detection.  
- Liquidity analytics:    
  - Log-normalized liquidity score.  
  - Volume participation (Vol.%).  
  - Liquidity ranking.  
- Visualization:  
  - TEA vs TTM term structure plot.  
  - Nelson–Siegel smoothed curve.  
  - Contract annotations.    

---

## Requirements

```bash
pip install pandas numpy matplotlib scipy openpyxl
```

---

## Usage

Provide the required input files:  
  - close.xlsx → MATBA-ROFEX market data  
  - holidays.xlsx → MATBA-ROFEX trading calendar (holidays)  

Run the script:
```bash
python nelson_siegel_curve.py
```

Example market data file: https://www.rofex.com.ar/Herramientas/Descargas/New/CierreParcialA3Mercados%E2%80%93Monedas17042026.xlsx

(Rename: CierreParcialA3Mercados%E2%80%93Monedas17042026.xlsx to close.xlsx)  

---

## Methodology

1\. Time to Maturity (TTM)  
```
TTM = Business Days (excluding weekends + holidays) / 252
```
Where:  
  - Uses numpy.busday_count  
  - Excludes weekends and holidays, adjusted through `holidays.xlsx`  
  - Critical for short-term contract accuracy  

2\. TEA Calculation  
```
TEA = (Future Price / Spot)^(1 / TTM) - 1
```
Represents the implied annualized rate embedded in each futures contract.  

3\. Nelson–Siegel Curve (Structural Model)  
The model is calibrated on log-price space:  
```
y = log(F / Spot)
```

The structural term structure is modeled as:  

```
y(x) = β₀ + β₁ * ((1 - e^{-λx}) / λx) + β₂ * (((1 - e^{-λx}) / λx) - e^{-λx})
```

Optimization is performed on a weighted least-squares objective over log-price space, including a synthetic front-end anchor.  

This provides a **smooth structural benchmark curve**.  

4\. Front-end stabilization (phantom node)  

A synthetic observation is injected at the front end of the curve:  
  - Improves calibration stability for short maturities  
  - Reduces sensitivity to sparse front contracts  
  - Acts as a numerical anchor for the Nelson–Siegel fit  

5\. Fair Value Construction  
```
Fair Price = Spot * exp(curve_value)
```

Computed by transforming the fitted Nelson–Siegel log-curve back into price space.  

6\. Mispricing (log-space)  

```
Mispricing = log(F/S) - NS_curve
```
- Interpretation:  
  - Positive → richer-than-structural pricing  
  - Negative → cheaper-than-structural pricing  

This allows detection of **relative-value distortions** across the curve.  
 
7\. Spread Structure Analysis  

The model computes:  
  - Incremental contract spreads  
  - Previous session spreads  
  - Spread differentials (`SpdDff`)  
  - Previous spread differentials (`PvSpdDff`)  

This helps visualize local steepening/flattening pressure along the futures strip.  

8\. Liquidity Modeling  

Liquidity is modeled as: 
```
Liquidity = log(1 + Volume)
```
Then normalized across the curve.  

Used for:  
  - Liquidity ranking  
  - Relative tradability analysis  
  - Weight stabilization in curve fitting  

---

## Outputs

**Console Output**  
- Market Structure Table  
  - TEA, TEM, TNA  
  - Current spreads  
  - Previous spreads  
  - Spread differentials  
  - Time-to-maturity  
- Relative Value Table:  
  - Mispricing (basis points equivalent aka bps)   
  - Open interest  
  - Volume participation  
  - Liquidity rank  

## Visualization

The generated chart includes:  
  - TEA (%) vs TTM (years)  
  - Market observations  
  - Nelson–Siegel structural curve  
  - Contract annotations  

---

## Notes

- Designed for **USD futures curve analysis in Argentina (MATBA-ROFEX)**.  
- Emphasizes relative-value structure rather than outright directional forecasting.  
- Incorporates liquidity-sensitive weighting and curve shape diagnostics.  
- Especially useful for:  
  - Relative value trading  
  - FX futures curve analysis  
  - Term structure diagnostics  
  - Short-end futures microstructure analysis  
- Built as a **hybrid quantitative research tool** for FX futures pricing.

---

## Author

Carlos Maccarrone  
Date: 2026-04-08

---