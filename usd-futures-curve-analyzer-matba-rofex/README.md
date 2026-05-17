# USD Futures Curve Analyzer (Spline + Nelson-Siegel Hybrid Model)

This Python script builds and analyzes the USD futures curve using MATBA-ROFEX contract data and spot FX, combining two complementary curve-fitting approaches:

A weighted spline (market-driven curve)
A Nelson–Siegel model (structural curve)

The model compares both structures to detect relative value distortions, curve shape dynamics, and liquidity-sensitive anomalies in the FX futures term structure.  

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
  - **Weighted Univariate Spline (market curve)**  
  - **Nelson–Siegel model (structural model)**  
- Relative value analytics:   
  - Fair value estimation.  
  - Log-space mispricing detection.  
  - Curve twist classification `STEEPENING/FLATTENING`.  
- Liquidity analytics:    
  - Log-normalized liquidity score.  
  - Volume participation (Vol.%).  
  - Liquidity ranking.  
- Visualization:  
  - TEA vs TTM term structure plot.  
  - Nelson–Siegel smoothed curve.  
  - Relative-value deviation lines.  
  - Mispricing labels (basis points).
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

3\. Weighted Spline Curve (Market Curve)  
- Observed futures prices are transformed into log-space:  
```
y = log(Future / Spot)
```
- Weighted smoothing spline:  
  - Weights = sqrt(Volume)  
  - Clipped to reduce outliers impact  

This produces a **liquidity-adjusted market curve**.  

4\. Nelson–Siegel Curve (Structural Model)  
The structural term structure is modeled as:  
```
y(x) = β₀ + β₁ * ((1 - e^{-λx}) / λx) + β₂ * (((1 - e^{-λx}) / λx) - e^{-λx})
```

Optimized via nonlinear least squares:  
  - Minimizes squared error vs observed log-prices  
  - Includes level shift adjustment for calibration  

This provides a **smooth structural benchmark curve**.  

5\. Fair Value Construction  
```
Fair Price = Spot * exp(curve_value)
```

Computed from Nelson–Siegel fitted curve.  

6\. Mispricing & Difference  
Two complementary measures:  
  - Mispricing (log-space) 
```
Mispricing = log(F/S) - NS_curve
```
- Interpretation:  
  - Positive → richer-than-structural pricing  
  - Negative → cheaper-than-structural pricing  

This allows detection of **relative-value distortions** across the curve.  
  
7\. Curve Twist Classification  

The relative position between the market spline and the Nelson–Siegel curve is used to classify curve shape dynamics:  
  - `STEEPENING`  
  - `FLATTENING`  

This is not intended as a directional trading signal, but rather as a term-structure diagnostic.  

8\. Spread Structure Analysis  

The model computes:  
  - Incremental contract spreads  
  - Previous session spreads  
  - Spread differentials (`SpdDff`)  
  - Previous spread differentials (`PvSpdDff`)  

This helps visualize local steepening/flattening pressure along the futures strip.  

9\. Liquidity Modeling  

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
  - Mispricing (bps)  
  - Curve twist classification  
  - Open interest  
  - Volume participation  
  - Liquidity rank  

## Visualization

The generated chart includes:  
  - TEA (%) vs TTM (years)  
  - Market observations  
  - Nelson–Siegel structural curve  
  - Relative-value deviation lines  
  - Mispricing labels in basis points  
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