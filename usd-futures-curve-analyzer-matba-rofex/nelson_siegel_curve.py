from scipy.interpolate import UnivariateSpline
from scipy.optimize import minimize
from datetime import datetime, time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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
# ================== INPUT ==================
df["TTM (years)"] = ttm_list

df["TEA (%)"] = tea_list
df["TEM (%)"] = ((1 + df["TEA (%)"]/100) ** (1/12) - 1) * 100
df["ΔTEM"] = df["TEM (%)"].diff()

df["Vol."] = df["Vol."].astype(float)

x = df["TTM (years)"].values
y = np.log(df["Ajuste"].values / spot)
# ================== SPLINE (market curve) ==================
weights = np.sqrt(df["Vol."].values)
weights = weights / np.mean(weights)
weights = np.clip(weights, 0.6, 1.5)

spline = UnivariateSpline(x, y, w=weights, s=0.0001)

y_spline = spline(x)

df["Spline Price"] = spot * np.exp(y_spline)
# ================== NELSON-SIEGEL (structural curve) ==================
def ns_model(theta, x):
    beta0, beta1, beta2, lam = theta

    term1 = (1 - np.exp(-lam * x)) / (lam * x)
    term2 = term1 - np.exp(-lam * x)

    return beta0 + beta1 * term1 + beta2 * term2

def loss(theta):
    y_pred = ns_model(theta, x)
    return np.sum((y - y_pred) ** 2)

res = minimize(loss, x0=[0.02, -0.01, 0.01, 1.0])
theta = res.x

y_ns = ns_model(theta, x)
shift = np.mean(y - y_ns)
y_ns = y_ns + shift

# curva lisa
x_smooth = np.linspace(x.min(), x.max(), 100)
y_smooth = ns_model(theta, x_smooth)
# ================== BACK TO TEA ==================
y_smooth_tea = (np.exp(y_smooth) ** (1 / x_smooth) - 1) * 100
y_curve = ns_model(theta, x)
tea_curve = (np.exp(y_curve) ** (1 / x) - 1) * 100
df["TEA Curve (%)"] = tea_curve
# ================== EDGE ==================
df["Fair Price"] = spot * np.exp(y_curve)
df["Edge_pts"] = df["Spline Price"] - df["Fair Price"]
tick_size = 0.5
df["Desvio ticks"] = df["Edge_pts"] / tick_size
df["Mispricing"] = y - y_ns
signal = y_spline - y_ns
df["Direction"] = np.where(signal > 0, "LONG", "SHORT")
# ================== LIQUIDITY ==================
vol = df["Vol."].values
liq = np.log1p(vol)
liq = liq / liq.max()
df["Liquidity"] = liq
# ================== FILTER ==================
df_filtered = df.copy()
df_filtered = df_filtered[df_filtered["Liquidity"] > 0.2]
df_sorted = df_filtered.sort_values("Liquidity", ascending=False)
# ================== OUTPUT ==================
print("\n=== RESULTS ===\n")
print(df[["Posición", "Ajuste", "TTM (years)", "TEA (%)", "TEM (%)", "ΔTEM", "Mispricing"]])
print("\n=== FROM MORE LIQUIDS TO LESS LIQUIDS ===")
print(df_sorted[["Posición", "Ajuste", "Fair Price", "Direction", "Desvio ticks", "Edge_pts", "Liquidity"]])
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
    plt.text(x_i, y_i + 0.15, label, ha='center', fontsize=9, fontweight="bold", color="black")
    
    # abajo: TEA formateada
    plt.text(x_i, y_i - 0.30, f"{y_i:.2f}%", ha='center', fontsize=9, fontweight="bold", color="black")

plt.xlabel("Tiempo a vencimiento (años)")
plt.ylabel("TEA (%)")

plt.subplots_adjust(
    left=0.05,
    right=0.98,
    top=0.92,
    bottom=0.08
)

plt.show()
# =================================================