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
  - TTM (Time to Maturity, business days adjusted).  
  - TEA (Tasa Efectiva Anual).  
  - TEM (Tasa Efectiva Mensual).  
  - ΔTEM (curve slope dynamics).  
  - TNA (Nominal Annual Rate approximation).  
- Builds two independent curve models:  
  - **Weighted Univariate Spline (market curve)**  
  - **Nelson–Siegel model (structural term structure)**  
- Computes:  
  - Fair value curve (Nelson–Siegel)  
  - Mispricing (log-space)  
  - Price Deviation (price-space)  
  - LONG / SHORT signal  
- Spread analysis:  
  - Current spread between contracts  
  - Previous spread comparison  
- Liquidity modeling:  
  - Log-scaled volume  
  - Normalized liquidity score  
  - Ranking by liquidity (most tradable first)  
- Visualization:  
  - TEA vs TTM scatter plot  
  - Nelson–Siegel curve (converted to TEA space)  
  - Contract labeling with ticker and rates  

---

## Requirements

```bash
pip install pandas numpy matplotlib scipy openpyxl
```

---

## Usage

Provide the required input files:  
  - close.xlsx → market data from Matba-Rofex  
  - holidays.xlsx → trading calendar (holidays)  

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
  - Adjusted with external holiday calendar (holidays.xlsx)  
  - Critical for short-term contract accuracy  

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
  - Price Deviation (price-space)  
```
Price Deviation = Spline Price - Fair Price
```
Used to detect **relative value opportunities**.  

7\. Liquidity Filter  

Liquidity is defined as:  
```
Liquidity = log(1 + Volume) normalized
```

Then:  
  - Used to rank contracts  
  - Output sorted from most to least liquid  

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
  - TEA, TEM, ΔTEM, TNA  
  - Spread, Previous Spread  
- Ranked liquidity view:  
  - Mispricing  
  - Price Deviation  
  - Trend (LONG / SHORT)  
  - Liquidity ranking  

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