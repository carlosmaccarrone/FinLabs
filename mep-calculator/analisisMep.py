import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_excel("analisisMep.xlsx")

################################
al30 = df[df["SIMBOLO"] == "AL30"].copy()
al30d = df[df["SIMBOLO"] == "AL30D"].copy()

al30.rename(columns={"PRECIO PROMEDIO":"PRECIO AL30", "VOLUMEN NOMINAL": "VOLUMEN AL30", "MONTO NEGOCIADO": "MONTO AL30"}, inplace=True)
al30d.rename(columns={"PRECIO PROMEDIO":"PRECIO AL30D", "VOLUMEN NOMINAL": "VOLUMEN AL30D", "MONTO NEGOCIADO": "MONTO AL30D"}, inplace=True)

merged = pd.merge(al30[["FECHA", "PRECIO AL30", "VOLUMEN AL30", "MONTO AL30"]], al30d[["FECHA", "PRECIO AL30D", "VOLUMEN AL30D", "MONTO AL30D"]], on="FECHA")
merged.columns = merged.columns.str.replace(" ", "_", regex=False)

merged["DOLAR_MEP"] = merged["PRECIO_AL30"] / merged["PRECIO_AL30D"]

merged["FECHA"] = pd.to_datetime(merged["FECHA"])
merged.sort_values("FECHA", inplace=True)
merged.reset_index(drop=True, inplace=True)
################################
## Un ZCORE_MEP < -1 podría indicar un MEP bajo respecto al promedio, con posibilidad de compra.
## Si el volumen > promedio es una oportunidad de compra.
span = 50
merged["EWMA_MEAN"] = merged["DOLAR_MEP"].ewm(span=span, adjust=False).mean()
merged["EWMA_STD"] = merged["DOLAR_MEP"].ewm(span=span, adjust=False).std()

merged["ZSCORE_MEP"] = (merged["DOLAR_MEP"] - merged["EWMA_MEAN"]) / merged["EWMA_STD"]

merged = merged.dropna(subset=["EWMA_MEAN", "EWMA_STD"]).copy()
################################
merged["EWMA_VOL_AL30D"] = merged["VOLUMEN_AL30D"].ewm(span=span, adjust=False).mean()

cond_venta = (merged["ZSCORE_MEP"] > 1) & (merged["VOLUMEN_AL30D"] > merged["EWMA_VOL_AL30D"])
cond_compra = (merged["ZSCORE_MEP"] < -1) & (merged["VOLUMEN_AL30D"] > merged["EWMA_VOL_AL30D"])

merged["FLUJO_INFERIDO"] = np.where(cond_venta, "Venta",
                           np.where(cond_compra, "Compra", None))
################################

# 1 precio implícito calculado
merged["PRECIO_CALC_AL30"] = merged["MONTO_AL30"] / merged["VOLUMEN_AL30"]
merged["PRECIO_CALC_AL30D"] = merged["MONTO_AL30D"] / merged["VOLUMEN_AL30D"]

# 2 zcore del volumen en al30
merged["EWMA_VOL_AL30"] = merged["VOLUMEN_AL30"].ewm(span=span, adjust=False).mean()
merged["EWMA_STD_VOL_AL30"] = merged["VOLUMEN_AL30"].ewm(span=span, adjust=False).std()

merged["ZVOL_AL30"] = (merged["VOLUMEN_AL30"] - merged["EWMA_VOL_AL30"]) / merged["EWMA_STD_VOL_AL30"]

# 3 diferencia entre precios teóricos vs reales
merged["DELTA_PRECIO_AL30"] = np.abs(merged["PRECIO_CALC_AL30"] - merged["PRECIO_AL30"])

# 4 dias con posible intervención (marcamos como True si se cumple alguna combinación)
merged["INTERVENIDO"] = ((merged["ZVOL_AL30"] > 1.0) & (merged["DELTA_PRECIO_AL30"] < 0.5)) # tolerancia de precios

################################
window = 50
subset = merged.tail(window)

subset_compra = subset[subset["ZSCORE_MEP"] < -1.0]
subset_venta = subset[subset["ZSCORE_MEP"] > 1.0]

fig, ax1 = plt.subplots(figsize=(12, 6))

# Eje principal: MEP y sus zcores
ax1.plot(subset["FECHA"], subset["DOLAR_MEP"], label="MEP", color="orange", marker="o")

# Líneas de +-1o
ax1.plot(subset["FECHA"], subset["EWMA_MEAN"], linestyle="--", color="gray", label="Media EWMA")
ax1.plot(subset["FECHA"], subset["EWMA_MEAN"] + subset["EWMA_STD"], linestyle="--", color="darkred", label="+1σ")
ax1.plot(subset["FECHA"], subset["EWMA_MEAN"] - subset["EWMA_STD"], linestyle="--", color="darkred", label="-1σ")

# Puntos de sweet spots
ax1.scatter(subset_compra["FECHA"], subset_compra["DOLAR_MEP"], color="green", label="Sweet Spot Compra", zorder=5)
ax1.scatter(subset_venta["FECHA"], subset_venta["DOLAR_MEP"], color="red", label="Sweet Spot Venta", zorder=5)

ax1.set_ylabel("Dólar MEP")
ax1.set_xlabel("Fecha")
ax1.tick_params(axis="y", labelcolor="orange")
ax1.grid(True)

# Eje secundario: Volumen AL30D fondo gris
ax2 = ax1.twinx()
ax2.bar(subset["FECHA"], subset["VOLUMEN_AL30D"], alpha=0.2, color="gray", label="Volumen AL30D")
ax2.set_ylabel("Volumen AL30D")
ax2.tick_params(axis="y", labelcolor="gray")

for row in subset.itertuples():
    if row.FLUJO_INFERIDO == "Venta":
        ax2.annotate("v", xy=(row.FECHA, row.VOLUMEN_AL30D), color="black", ha="center")
    elif row.FLUJO_INFERIDO == "Compra":
        ax2.annotate("c", xy=(row.FECHA, row.VOLUMEN_AL30D), color="black", ha="center")

for fecha in subset[subset["INTERVENIDO"]]["FECHA"]:
	ax1.axvspan(fecha - pd.Timedelta(days=0.5), fecha + pd.Timedelta(days=0.5), color='yellow', alpha=0.3)

# Título y leyenda
fig.suptitle("Análisis del Dólar MEP con Sweet Spots y Volumen", fontsize=14)
fig.tight_layout()
fig.legend(loc="upper left", bbox_to_anchor=(0.12, 0.88))
plt.show()

################################