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
  - Mispricing vs both curves  
  - Edge in ARS and ticks  
- Liquidity modeling:  
  - Log-scaled volume  
  - Normalized liquidity score  
  - Filtering of illiquid contracts  
- Generates trading signals:  
  - LONG / SHORT based on relative mispricing
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
```bash
TTM = (maturity - market_close) / 365
```

Where:  
  - Market close is fixed at 15:00  
  - Maturity is also normalized to 15:00  

2\. TEA Calculation  
```bash
TEA = (Future Price / Spot)^(1 / TTM) - 1
```
Represents the implied annualized rate embedded in each futures contract.  

3\. Weighted Spline Curve (Market Curve)  
- The market curve is constructed using:  
```bash
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
```bash
Fair Price = Spot * exp(curve_value)
```

Computed from Nelson–Siegel fitted curve.  

6\. Mispricing & Edge  
- Two sources of deviation:  
  - Spline vs Nelson-Siegel  
  - Market price vs theoretical curve  

- Key metrics:  
  - `Edge_pts = Spline Price - Fair Price`  
  - `Mispricing = log(F/S) - NS_curve`  
  - `Desvio ticks = Edge_pts / tick_size`  

- Used to detect **relative value opportunities**.

7\. Liquidity Filter  

Liquidity is defined as:  
```bash
Liquidity = log(1 + Volume) normalized
```

Then:  
  - Contracts with low liquidity are filtered out  
  - Ranking is done by liquidity strength  

8\. Trading Signal  
  
Directional signal:  
```bash
signal = spline_curve - nelson_siegel_curve
```

Interpretation:  
  - LONG → market above structural curve  
  - SHORT → market below structural curve  

---

## Outputs

**Console Output**  
- Full contract table:  
  - TEA, TEM, ΔTEM, Mispricing  
- Ranked liquidity view:  
  - Fair Price  
  - Direction (LONG / SHORT)  
  - Edge in ARS and ticks  

## Visualization

- TEA (%) vs TTM (years)  
- Market scatter points (red/green by mispricing)  
- Smoothed Nelson–Siegel curve (yellow)  
- Contract annotations  

---

## Author

Carlos Maccarrone  
Date: 2026-04-08

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