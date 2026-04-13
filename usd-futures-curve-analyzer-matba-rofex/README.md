# USD Futures Curve Analyzer (Spline + Nelson-Siegel Hybrid Model)

This Python script builds and analyzes the USD futures curve using MATBA-ROFEX contract data and spot FX, combining two curve-fitting approaches:

A weighted spline (market-driven curve)
A Nelson–Siegel model (structural curve)

It then compares both to detect mispricing, relative value opportunities, and liquidity-adjusted signals.

---

## Features

- Extracts and cleans futures data directly from Matba-Rofex Excel files.  
- Automatically detects spot FX (Dólar UST ART 000).  
- Calculates:  
  - TTM (Time to Maturity) in years.  
  - TEA (Tasa Efectiva Anual).  
  - TEM (Tasa Efectiva Mensual).  
  - ΔTEM (curve slope dynamics).  
- Builds two independent curve models:  
  - **Weighted Univariate Spline (market curve)**  
  - **Nelson–Siegel model (structural term structure)**  
- Computes:
  - Fair value curve  
  - Mispricing (NS)  
  - LONG / SHORT based on relative mispricing  
  - Ranking of candidates which could reverse direction  
- Liquidity modeling:  
  - Log-scaled volume  
  - Normalized liquidity score  
  - Filtering of illiquid contracts  
- Visualization:  
  - TEA vs TTM scatter plot.  
  - Smoothed curve overlay.  
  - Contract labeling with ticker and rates.  

---

## Requirements

```bash
pip install pandas numpy matplotlib scipy openpyxl
```

---

## Usage

Run the script and provide a Matba-Rofex Excel file: 
```bash
Ingrese nombre archivo con extension: close.xlsx
```

Example file: https://www.rofex.com.ar/Herramientas/Descargas/New/CierreParcialA3Mercados%E2%80%93Monedas10042026.xlsx

(Rename: CierreParcialA3Mercados%E2%80%93Monedas10042026.xlsx to close.xlsx)  

---

## Methodology

1\. Time to Maturity (TTM)  

All contracts are aligned to market close (15:00):  
```
TTM = Effective Trading Days / 252
```
Where:  
  - Calendar time is adjusted by removing weekends  
  - Both report timestamps (close_date and maturity_date) are aligned to market close (15:00)  

2\. TEA Calculation  
```
TEA = (Future Price / Spot)^(1 / TTM) - 1
```
Represents the implied annualized rate embedded in each futures contract.  

3\. Weighted Spline Curve (Market Curve)  
- The market curve is constructed using:  
```
y = log(Future / Spot)
```
- Weighted smoothing spline:  
  - Weights = √(Volume)  
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

This provides a **smooth macro-consistent curve**.  

5\. Fair Value Construction  
```
Fair Price = Spot * exp(curve_value)
```

Computed from Nelson–Siegel fitted curve.  

6\. Mispricing & Difference  
- Two sources of deviation:  
  - Spline vs Nelson-Siegel  
  - Market price vs theoretical curve  

- Key metrics:  
  - `Mispricing = log(F/S) - NS_curve`  
  - `Difference = Spline Price - Fair Price`  

- Used to detect **relative value opportunities**.

7\. Liquidity Filter  

Liquidity is defined as:  
```
Liquidity = log(1 + Volume) normalized
```

Then:  
  - Contracts with low liquidity are filtered out  
  - Ranking is done by liquidity strength  

8\. Trading Signal  
  
Directional signal:  
```
signal = spline_curve - nelson_siegel_curve
```
  
Signal is derived from the relative position between the market curve 
(spline) and the structural curve (Nelson–Siegel).  
  
It reflects momentum or deviation from structural equilibrium, 
not absolute mispricing.  

---

## Outputs

**Console Output**  
- Full contract table:  
  - TEA, TEM, ΔTEM, Mispricing  
- Ranked liquidity view:  
  - Fair Price  
  - Direction (LONG / SHORT)  
  - Candidates ranking which could reverse direction.  

## Visualization

- TEA (%) vs TTM (years)  
- Market scatter points (red/green by mispricing)  
- Smoothed Nelson–Siegel curve (orange)  
- Contract annotations  

---

## Methodoly  
  
The Nelson–Siegel curve is not intended to replicate market prices, 
but to provide a stable structural benchmark.  
  
Mispricing is defined as the deviation between market-implied pricing 
and this structural curve.  
  
Short-term contracts are highly sensitive to time-to-maturity estimation,
making accurate time modeling critical for stable curve construction.  
  
---

## Notes

- Designed for **USD futures curve analysis in Argentina (MATBA-ROFEX)**.  
- Combines:  
  - Market-driven interpolation (spline)  
  - Structural macro model (Nelson–Siegel)   
- Useful for:  
  - Relative value trading  
  - Curve arbitrage  
  - Term structure analysis  
- Built as a **hybrid quantitative research tool** for FX futures pricing.

---

## Author

Carlos Maccarrone  
Date: 2026-04-08

---