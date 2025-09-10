"""
MEP Analyzer for AL30/AL30D Bonds
---------------------------------
This script calculates and visualizes the MEP (Mercado Electrónico de Pagos)
exchange rate using AL30 (ARS) and AL30D (USD) bond price data.

Features:
- Calculates MEP from AL30 and AL30D prices.
- Plots:
	* Historical MEP value.
	* Daily traded volume.
	* Market pressure (buy(c)/sell(v) dominance).
	* "Sweet spot" zones for optimal buy/sell opportunities.
- RSI-style visualization for intuitive market timing.
- Uses pandas for data processing, scipy to detect sweet spots 
  and matplotlib for visualization.
- Built as an educational, clean example of financial data analysis
  and plotting with Python.

Requirements:
	pandas, scipy, matplotlib

Usage:
	• In Windows: run from desktop the `analisisMep.bat` file.
	• In Linux/macOS: run from terminal `python analisisMep.py`.

Author: Carlos Maccarrone
Date: 2025-08-15
"""

import matplotlib.pyplot as plt
from scipy.stats import zscore
import pandas as pd

df = pd.read_excel("dolarMep.xlsx")
# print(df.head())

################################
al30 = df[df["SIMBOLO"] == "AL30"].copy()
al30d = df[df["SIMBOLO"] == "AL30D"].copy()

al30.rename(columns={"PRECIO PROMEDIO":"PRECIO AL30", "VOLUMEN NOMINAL": "VOLUMEN AL30", "MONTO NEGOCIADO": "MONTO AL30"}, inplace=True)
al30d.rename(columns={"PRECIO PROMEDIO":"PRECIO AL30D", "VOLUMEN NOMINAL": "VOLUMEN AL30D", "MONTO NEGOCIADO": "MONTO AL30D"}, inplace=True)

merged = pd.merge(al30[["FECHA", "PRECIO AL30", "VOLUMEN AL30", "MONTO AL30"]], al30d[["FECHA", "PRECIO AL30D", "VOLUMEN AL30D", "MONTO AL30D"]], on="FECHA")

merged["DOLAR MEP"] = merged["PRECIO AL30"] / merged["PRECIO AL30D"]

merged["FECHA"] = pd.to_datetime(merged["FECHA"])
merged.sort_values("FECHA", inplace=True)
################################

## Un ZCORE MEP < -1 podría ndicar un MEP bajo respecto al promedio, con posibilidad de compra.
## Si el volumen > promedio es una oportunidad de comra.
merged["ZSCORE MEP"] = zscore(merged["DOLAR MEP"])

sweet_spots_compra = merged[merged["ZSCORE MEP"] < -1.0]
sweet_spots_venta = merged[merged["ZSCORE MEP"] > 1.0]

# print("Posibles oportunidades de COMPRA (MEP muy bajo):")
# print(sweet_spots_compra[["FECHA", "DOLAR MEP", "ZSCORE MEP"]])

# print("Posibles oportunidades de VENTA (MEP muy alto):")
# print(sweet_spots_venta[["FECHA", "DOLAR MEP", "ZSCORE MEP"]])

################################

def clasificar_flujo(row):
	mean = merged["VOLUMEN AL30D"].mean()
	if row["ZSCORE MEP"] > 1 and row["VOLUMEN AL30D"] > mean:
		return "Venta"
	elif row["ZSCORE MEP"] < -1 and row["VOLUMEN AL30D"] > mean:
		return "Compra"
	else:
		return None

merged["FLUJO INFERIDO"] = merged.apply(clasificar_flujo, axis=1)

################################

# 1 precio implícito calculado
merged["PRECIO CALC AL30"] = merged["MONTO AL30"] / merged["VOLUMEN AL30"]
merged["PRECIO CALC AL30D"] = merged["MONTO AL30D"] / merged["VOLUMEN AL30D"]

# 2 zcore del volumen en al30
merged["ZVOL AL30"] = (merged["VOLUMEN AL30"] - merged["VOLUMEN AL30"].mean()) / merged["VOLUMEN AL30"].std()

# 3 diferencia entre precios teóricos vs reales
merged["DELTA PRECIO AL30"] = abs(merged["PRECIO CALC AL30"] - merged["PRECIO AL30"])

# 4 dias con posible intervención (marcamos como True si se cumple alguna combinación)
merged["INTERVENIDO"] = ((merged["ZVOL AL30"] > 1.0) & (merged["DELTA PRECIO AL30"] < 0.5)) # tolerancia de precios

################################

window = 50
subset = merged.tail(window)

fig, ax1 = plt.subplots(figsize=(12, 6))

# Eje principal: MEP y sus zcores
ax1.plot(subset["FECHA"], subset["DOLAR MEP"], label="MEP", color="blue", marker="o")
media = subset["DOLAR MEP"].mean()
std = subset["DOLAR MEP"].std()

# Líneas de +-1o
ax1.axhline(media + std, color="red", linestyle="--", label="+1o")
ax1.axhline(media - std, color="red", linestyle="--", label="-1o")
ax1.axhline(media, color="gray", linestyle="--", label="Media")

# Puntos de sweet spots
ax1.scatter(sweet_spots_compra["FECHA"], sweet_spots_compra["DOLAR MEP"], color="red", label="Sweet Spot Compra", zorder=5)
ax1.scatter(sweet_spots_venta["FECHA"], sweet_spots_venta["DOLAR MEP"], color="red", label="Sweet Spot Venta", zorder=5)

ax1.set_ylabel("Dólar MEP")
ax1.set_xlabel("Fecha")
ax1.tick_params(axis="y", labelcolor="blue")
ax1.grid(True)

# Eje secundario: Volumen AL30D fondo gris
ax2 = ax1.twinx()
ax2.bar(subset["FECHA"], subset["VOLUMEN AL30D"], alpha=0.2, color="gray", label="Volumen AL30D")
ax2.set_ylabel("Volumen AL30D")
ax2.tick_params(axis="y", labelcolor="gray")

for _, row in subset.iterrows():
	if row["FLUJO INFERIDO"] == "Venta":
		ax2.annotate("v", xy=(row["FECHA"], row["VOLUMEN AL30D"]), color="black", ha="center")
	elif row["FLUJO INFERIDO"] == "Compra":
		ax2.annotate("c", xy=(row["FECHA"], row["VOLUMEN AL30D"]), color="black", ha="center")

for fecha in subset[subset["INTERVENIDO"] == True]["FECHA"]:
	ax1.axvspan(fecha - pd.Timedelta(days=0.5), fecha + pd.Timedelta(days=0.5), color='yellow', alpha=0.3)

# Título y leyenda
fig.suptitle("Análisis del Dólar MEP con Sweet Spots y Volumen", fontsize=14)
fig.tight_layout()
fig.legend(loc="upper left", bbox_to_anchor=(0.12, 0.88))
plt.show()

################################







