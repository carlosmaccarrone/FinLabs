from scipy.interpolate import UnivariateSpline
from scipy.optimize import minimize
from datetime import datetime, time
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# ================== TIME FUNCTIONS ==================
def ttm_years(close, maturity, holiday_dates):
    business_days = np.busday_count(
        close.date(),
        maturity.date(),
        holidays=holiday_dates
    )
    if business_days <= 0:
        return np.nan
    return max(business_days / 252, 0.0001)

def tea(price, spot, maturity, close, holiday_dates):
    ttm_y = ttm_years(close, maturity, holiday_dates)
    return (price / spot) ** (1 / ttm_y) - 1, ttm_y
# ================== READ EXCEL ==================
file_path = "close.xlsx"
df = pd.read_excel(file_path, header=9)
# Tomamos solo las 10 filas de contratos
# df = df.iloc[0:11].copy()

# encontrar primer corte (fila vacía en Posición)
mask = df["Posición"].notna()
end_idx = mask.idxmin() if not mask.all() else len(df)
df = df.iloc[:end_idx].copy()
# ================== CLEAN DATA ==================
def parse_number(x):
    if isinstance(x, str):
        x = x.replace('.', '').replace(',', '.')
    return float(x)

# Precio (Ajuste)
df["Ajuste"] = df["Ajuste"].apply(parse_number)
# Maturity
df["Último Día Neg."] = pd.to_datetime(df["Último Día Neg."], dayfirst=True)
# ================== SPOT ==================
df_raw = pd.read_excel(file_path, header=None)
spot = None

for i in range(27, 47):
    if str(df_raw.iloc[i, 0]).strip() == "Dólar UST ART 000":
        spot = parse_number(df_raw.iloc[i, 2])
        close_date = pd.to_datetime(df_raw.iloc[i, 1], dayfirst=True)
        break

if spot is None:
    raise ValueError("No se encontró el spot 'Dólar UST ART 000' en las filas esperadas")

holidays_df = pd.read_excel("holidays.xlsx")
holidays_df["Fecha"] = pd.to_datetime(holidays_df["Fecha"], dayfirst=True)
holiday_dates = sorted(set(holidays_df["Fecha"].dt.date))
# ================== CALCULATE CURVE ==================
ttm_list = []
tea_list = []

for _, row in df.iterrows():
    price = row["Ajuste"]
    maturity_date = row["Último Día Neg."]
    
    tea_value, ttm_y = tea(price, spot, maturity_date, close_date, holiday_dates)
    
    ttm_list.append(ttm_y)
    tea_list.append(tea_value * 100)
# ================== INPUT ==================
df["TTM (years)"] = ttm_list
df["TEA (%)"] = tea_list
df["TEM (%)"] = ((1 + df["TEA (%)"]/100) ** (1/12) - 1) * 100
df["ΔTEM"] = df["TEM (%)"].diff()
df["Vol."] = pd.to_numeric(df["Vol."], errors="coerce").fillna(0)
x = df["TTM (years)"].values
x_safe = np.where(x == 0, 1e-6, x) # guardrail
y = np.log(df["Ajuste"].values / spot)
# ================== SPLINE (market curve) ==================
weights = np.sqrt(df["Vol."].values)
weights = weights / np.mean(weights)
weights = np.clip(weights, 0.6, 1.5)
spline = UnivariateSpline(x_safe, y, w=weights, s=0.0001)
y_spline = spline(x_safe)
df["Spline Price"] = spot * np.exp(y_spline)
# ================== NELSON-SIEGEL (structural curve) ==================
def ns_model(theta, x):
    beta0, beta1, beta2, lam = theta

    term1 = (1 - np.exp(-lam * x)) / (lam * x)
    term2 = term1 - np.exp(-lam * x)

    return beta0 + beta1 * term1 + beta2 * term2

def loss(theta):
    y_pred = ns_model(theta, x_safe)
    return np.sum((y - y_pred) ** 2)

res = minimize(loss, x0=[0.02, -0.01, 0.01, 1.0])
theta = res.x
y_ns = ns_model(theta, x_safe)
# curva lisa
x_smooth = np.linspace(x_safe.min(), x_safe.max(), 100)
y_smooth = ns_model(theta, x_smooth)
# ================== BACK TO TEA ==================
y_smooth_tea = (np.exp(y_smooth) ** (1 / x_smooth) - 1) * 100
# ================== EDGE ==================
df["Fair Price (NS)"] = spot * np.exp(y_ns)
df["Price Deviation"] = df["Spline Price"] - df["Fair Price (NS)"]
df["Mispricing"] = y - y_ns
df["Status"] = np.where(df["Mispricing"] > 0, "CARO", "BARATO")
signal = y_spline - y_ns
df["Trend"] = np.where(signal > 0, "LONG", "SHORT")
df["Simple Return"] = (df["Ajuste"] / spot - 1)
df["TNA (%)"] = (df["Simple Return"] / x_safe) * 100
df["Spread"] = pd.to_numeric(df["Ajuste"].diff(), errors="coerce").fillna(0)
df["PrevSpread"] = pd.to_numeric(df["Aj. Ant."].diff(), errors="coerce").fillna(0)
# ================== LIQUIDITY ==================
vol = df["Vol."].values
liq = np.log1p(vol)
liq = liq / liq.max()
df["Liquidity"] = liq
# ================== FILTER ==================
df_filtered = df.copy()
# df_filtered = df_filtered[df_filtered["Liquidity"] > 0.2]
df_filtered["O.I."] = df_filtered["I. A.*"]
df_filtered["Var.%"] = df.filter(like="Var.%")
df_sorted = df_filtered.sort_values("Liquidity", ascending=False)
# ================== OUTPUT ==================
print("\n=== RESULTS ===\n")
print(df[["Posición", "Ajuste", "Spread", "PrevSpread", "TTM (years)", "TEA (%)", "TEM (%)", "ΔTEM", "TNA (%)"]])
print("\n=== FROM MORE LIQUIDS TO LESS LIQUIDS ===")
print(df_sorted[["Posición", "Var.%", "Mispricing", "Price Deviation", "Trend", "Status", "O.I.", "Liquidity"]])
print("\nSPOT: AR$ {}".format(spot))
print("Timestamp: {}".format(close_date.date().strftime("%d/%m/%Y")))
# ================== PLOT ==================
plt.figure()

# puntos reales
colors = ["red" if m > 0 else "green" for m in df["Mispricing"]]
plt.scatter(df["TTM (years)"], df["TEA (%)"], color=colors, zorder=3)

# curva suavizada
plt.plot(x_smooth, y_smooth_tea, color="tab:orange", zorder=2)

# etiquetas
for _, row in df.iterrows():
    x_i = row["TTM (years)"]
    y_i = row["TEA (%)"]
    label = row["Posición"]
    
    # arriba: contrato
    plt.text(x_i, y_i + 0.2, label, ha='center', fontsize=9, fontweight="bold", color="black")
    
    # abajo: TEA formateada
    plt.text(x_i + 0.004, y_i - 0.5, f"{y_i:.2f}%", ha='center', fontsize=9, fontweight="bold", color="black")

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