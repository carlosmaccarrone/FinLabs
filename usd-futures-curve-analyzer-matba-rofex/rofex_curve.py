from scipy.interpolate import UnivariateSpline
from datetime import datetime, time
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# ================== TIME FUNCTIONS ==================
def market_now():
    now = datetime.now()
    return datetime.combine(now.date(), time(15, 0))

def market_maturity(maturity_date):
    return datetime.combine(maturity_date, time(15, 0))

def year_fraction(now, maturity):
    delta = maturity - now
    return delta.total_seconds() / (365 * 24 * 60 * 60)

def tea(price, spot, maturity_date):
    now_mkt = market_now()
    maturity = market_maturity(maturity_date)
    ttm_years = year_fraction(now_mkt, maturity)
    return (price / spot) ** (1 / ttm_years) - 1, ttm_years

# ================== READ EXCEL ==================

file_path = input("Ingrese nombre archivo con extension: ")

# file_path = "CierreParcialA3Mercados–Monedas08042026.xlsx"

df = pd.read_excel(file_path, header=9)

# Tomamos solo las 10 filas de contratos
df = df.iloc[0:11].copy()

# ================== CLEAN DATA ==================

def parse_number(x):
    if isinstance(x, str):
        x = x.replace('.', '').replace(',', '.')
    return float(x)

# Precio (Ajuste)
df["Ajuste"] = df["Ajuste"].apply(parse_number)

# Fecha
df["Último Día Neg."] = pd.to_datetime(df["Último Día Neg."], dayfirst=True)

# ================== SPOT ==================

df_raw = pd.read_excel(file_path, header=None)

spot = None

for i in range(31, 37):  # filas 32 a 36 inclusive
    if str(df_raw.iloc[i, 0]).strip() == "Dólar UST ART 000":
        spot = parse_number(df_raw.iloc[i, 2])
        break

if spot is None:
    raise ValueError("No se encontró el spot 'Dólar UST ART 000' en las filas esperadas")

print("\nSPOT: AR$ {}\n".format(spot))
# ================== CALCULATE CURVE ==================

ttm_list = []
tea_list = []

for _, row in df.iterrows():
    price = row["Ajuste"]
    maturity_date = row["Último Día Neg."]
    
    ttm, ttm_years = None, None
    tea_value, ttm_years = tea(price, spot, maturity_date)
    
    ttm_list.append(ttm_years)
    tea_list.append(tea_value * 100)

df["TTM (years)"] = ttm_list
df["TEA (%)"] = tea_list
df["TEM (%)"] = ((1 + df["TEA (%)"]/100) ** (1/12) - 1) * 100
df["ΔTEM"] = df["TEM (%)"].diff()

x = df["TTM (years)"].values
y = np.log(df["Ajuste"] / spot)

df["Vol."] = df["Vol."].apply(parse_number)
weights = np.sqrt(df["Vol."].values)
weights = weights / weights.max()

# spline con suavizado
spline = UnivariateSpline(x, y, w=weights, s=0.0001)  # parámetro clave

x_smooth = np.linspace(min(x), max(x), 100)
y_smooth = spline(x_smooth)

# volver a TEA
y_smooth_tea = (np.exp(y_smooth) ** (1 / x_smooth) - 1) * 100

# curva en los puntos reales
y_curve = spline(x)

# convertir a TEA
tea_curve = (np.exp(y_curve) ** (1 / x) - 1) * 100

df["TEA Curve (%)"] = tea_curve

# desvío
df["Mispricing"] = df["TEA (%)"] - df["TEA Curve (%)"]

# precio teórico desde la curva
df["Fair Price"] = spot * np.exp(y_curve)

# mispricing en pesos
df["Mispricing $"] = df["Ajuste"] - df["Fair Price"]

print(df[["Posición", "Ajuste", "TTM (years)", "TEA (%)", "TEM (%)", "ΔTEM", "Mispricing"]])

df_sorted = df[df["Vol."] > 9000]

df_sorted = df_sorted.sort_values("Mispricing", ascending=False)
print("\n=== MÁS CAROS → MÁS BARATOS ===\n")
print(df_sorted[["Posición", "Ajuste", "Mispricing", "Mispricing $", "I. A.*", "Fair Price"]])
# ================== PLOT ==================
plt.figure()

# puntos reales
colors = ["red" if m > 0 else "green" for m in df["Mispricing"]]
plt.scatter(df["TTM (years)"], df["TEA (%)"], color=colors, zorder=3)

# curva suavizada
plt.plot(x_smooth, y_smooth_tea, color="yellow", zorder=2)

# etiquetas
for _, row in df.iterrows():
    x_i = row["TTM (years)"]
    y_i = row["TEA (%)"]
    label = row["Posición"]
    
    # arriba: contrato
    plt.text(x_i, y_i + 0.25, label, ha='center', fontsize=9, fontweight="bold", color="black")
    
    # abajo: TEA formateada
    plt.text(x_i, y_i - 0.4, f"{y_i:.2f}%", ha='center', fontsize=9, fontweight="bold", color="black")

plt.xlabel("Tiempo a vencimiento (años)")
plt.ylabel("TEA (%)")
plt.title("Curva futuros dólar (suavizada)")

plt.grid()
plt.show()
# =================================================