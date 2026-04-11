# USD Futures Curve Percentile Analyzer (MATBA-ROFEX)

This project builds a clean historical dataset of USD futures (DLR) and analyzes curve mispricing dynamics over time, using percentiles and z-scores across different maturity buckets.

---

## Features

- Builds a **clean dataset** from raw market data:   
  - Spot FX (USD/ARS).  
  - TEA (Tasa Efectiva Anual).  
  - Futures contracts (DLR).  
- Filters contracts by **liquidity (volume threshold)**.  
- Calculates:
  - TTM (Time to Maturity).  
  - Log returns: `log(Future / Spot)`.  
- Fits a **smoothed futures curve** per day:  
  - Uses weighted splines.  
  - Weights based on volume.  
- Computes:  
  - Mispricing (%) vs theoretical curve.  
- Aggregates mispricing into **curve segments (buckets)**:  
  - Short (0–3 months).  
  - Mid (3–7 months).  
  - Long (7+ months).  
- Performs **historical analysis**:  
  - Percentiles per bucket.  
  - Mean and standard deviation.  
  - Z-score.  
- Generates **trading signals**:  
  - EXTREMO CARO / BARATO.  
  - CARO / BARATO.  
  - NEUTRO.  
- Built as an **educational, clean example** of financial data analysis and plotting in Python.

---

## Project Structure

.  
├── build_dataset.py&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Creates clean dataset from raw files  
├── analyze_curve.py&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Computes curve + percentiles + signals  
├── DollarSpot.xlsx&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Historical spot FX  
├── closing_prices_contratos.csv&nbsp;&nbsp;&nbsp;# Futures data  
├── clean_dataset.csv&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Generated dataset  

---

## Requirements  
```bash
pip install pandas numpy scipy openpyxl
```

## Usage

### Build Dataset

Run:  
```bash
python build_dataset.py
```

Output:  
```bash
clean_dataset.csv
```

- Dataset includes:  
  - Date  
  - Spot  
  - Contract  
  - Maturity  
  - Price  
  - Volume  

### Analyze Curve & Percentiles

Run:  
```bash
python analyze_curve.py
```

Output example:

```bash
=== SHORT ===  
Mispricing: 0.1234  
Percentil: 92.15%  
Media: 0.0456  
Std: 0.0301  
Z-score: 2.12  
Señal: 🔴 EXTREMO CARO  
```

## Analysis Details

1. Time to Maturity (TTM)  
```bash
TTM = (maturity - now) / 365
```

Computed using market close time (15:00).  

2. Curve Construction  

- Transform:
```bash
y = log(Future / Spot)
```

- Fit spline:  
```bash
UnivariateSpline(x, y, w=weights, s=0.0001)
```

Where:  

- `weights = sqrt(volume)`  
- Normalized to avoid dominance  

3. Mispricing Calculation   
```bash
TEA_real  = exp(y)^(1 / TTM) - 1  
TEA_curve = exp(y_curve)^(1 / TTM) - 1  
Mispricing (%) = (TEA_real - TEA_curve) * 100  
```
- Fits a Univariate Spline:  
  - Weighted by √volume (more liquidity → more influence).  
  - Smoothness controlled via parameter s.  

4. Bucket Aggregation  
- Buckets:
  - Short: 0 – 0.25 years  
  - Mid: 0.25 – 0.6 years  
  - Long: 0.6 – 1.5 years  

Volume-weighted average:  
```bash
mispricing_bucket = Σ(mispricing_i * weight_i)
```

5. Percentile & Z-score  

For each bucket:  
```bash
percentile = (historical < current).mean()  
zscore = (current - mean) / std  
```
Used to contextualize current mispricing vs history.  

---

## Notes
- Designed for **ARS/USD futures curve analysis (DLR)**.  
- Focuses on **relative value, not outright direction**.  
- Key idea:  
  - The curve is dynamic.  
  - Percentiles capture **how stretched each segment is vs history**.  

---

## Author

Carlos Maccarrone  
Date: 2026-04-08

---

## Use Cases
- Relative value trading (curve arbitrage).  
- Detecting distortions between short/mid/long segments.  
- Monitoring term structure regimes.  
- Building signals for systematic strategies.  