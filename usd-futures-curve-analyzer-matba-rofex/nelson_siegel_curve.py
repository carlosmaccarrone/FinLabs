from scipy.interpolate import UnivariateSpline
from scipy.optimize import minimize
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
# ================= FORMAT FUNCTIONS =================
def format_matba_contract(pos):
    if not isinstance(pos, str) or len(pos) != 9:
        return pos  # first guardrail

    asset = pos[:3]
    month = pos[3:5]
    year = pos[-2:]

    month_map = {
        "01": "ENE", "02": "FEB", "03": "MAR",
        "04": "ABR", "05": "MAY", "06": "JUN",
        "07": "JUL", "08": "AGO", "09": "SEP",
        "10": "OCT", "11": "NOV", "12": "DIC",
    }

    if month not in month_map:
        return pos # second guardrail

    return f"{asset}/{month_map[month]}{year}"    
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
        prev_spot = parse_number(df_raw.iloc[i, 4])
        close_date = pd.to_datetime(df_raw.iloc[i, 1], dayfirst=True)
        break

if spot is None:
    raise ValueError("No se encontró el spot 'Dólar UST ART 000' en las filas esperadas")

holidays_df = pd.read_excel("holidays.xlsx")
holidays_df["Fecha"] = pd.to_datetime(holidays_df["Fecha"], dayfirst=True)
holiday_dates = sorted(set(holidays_df["Fecha"].dt.date))
df = df[df["Último Día Neg."] > close_date].copy()
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
    w_base = np.sqrt(np.clip(x_safe, 0.05, 0.6))
    w_mask = np.zeros(len(df))
    w_mask[2:7] = 1
    w = 0.7 * w_base + 0.3 * w_mask
    return np.sum(w * (y - y_pred) ** 2)

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
df["Mispricing"] = y - y_ns
df["Status"] = np.where(df["Mispricing"] > 0, "CARO", "BARATO")
df["Twist"] = np.where(np.sign(y_spline - y_ns) > 0, "STEEPENING", "FLATTENING")
df["Simple Return"] = (df["Ajuste"] / spot - 1)
df["TNA (%)"] = (df["Simple Return"] / x_safe) * 100
adj = pd.to_numeric(df["Ajuste"], errors="coerce")
spreads = adj.diff().fillna(0)
spreads.iloc[0] = adj.iloc[0] - spot
df["Spread"] = spreads
prev_adj  = pd.to_numeric(df["Aj. Ant."], errors="coerce")
prev_spreads = prev_adj.diff().fillna(0)
prev_spreads.iloc[0] = prev_adj.iloc[0] - prev_spot
df["PvSpd"] = prev_spreads
total_vol = df["Vol."].sum()
df["Vol_Share"] = df["Vol."] / total_vol
df["Vol.%"] = (df["Vol_Share"] * 100).round(2)
df["TTM (days)"] = (df["TTM (years)"] * 252).round()
df["TTM"] = df["TTM (days)"].astype("Int64")
df["Var.%"] = df.filter(like="Var.%").iloc[:, 0]
# ================== LIQUIDITY ==================
vol = df["Vol."].values
liq = np.log1p(vol)
liq = liq / liq.max()
df["Liquidity"] = liq
# ================== FILTER ==================
df["Posición"] = df["Posición"].apply(format_matba_contract)
df_calculations = df.copy()
df_calculations["O.I."] = df_calculations["I. A.*"]
df_calculations["Rank"] = df_calculations["Liquidity"].rank(ascending=False).astype(int)
# df_sorted = df_calculations.sort_values("Liquidity", ascending=False)
# ================== OUTPUT ==================
print("\n=== RESULTS ===")
print(df.assign(**{
        "Aj": df["Ajuste"],
        "SpdDff": pd.to_numeric(df["Spread"].diff(), errors="coerce"),
        "PvAj": pd.to_numeric(df["Aj. Ant."], errors="coerce"),
        "PvSpdDff": pd.to_numeric(df["PvSpd"].diff(), errors="coerce"),
        "TEM %": df["TEM (%)"].round(3),
        "TEA %": df["TEA (%)"].round(2),
        "TNA %": df["TNA (%)"].round(2)        
    })[["Posición", "Var.%", "Aj", "Spread", "SpdDff", "PvAj", "PvSpd", "PvSpdDff", "TTM", "TEM %", "TEA %","TNA %"]])
print("\n")
print(df_calculations.assign(**{
        "Misprice": (df_calculations["Mispricing"] * 10000).round(2),
    })[["Posición", "Misprice", "Status", "Twist", "O.I.", "Vol.", "Vol.%", "Rank"]])
print("\nSPOT: AR$ {}".format(spot))
print("Timestamp: {}".format(close_date.date().strftime("%d/%m/%Y")))
# ================== PLOT ==================
plt.figure()

# puntos reales
colors = ["red" if m > 0 else "green" for m in df["Mispricing"]]
plt.scatter(df["TTM (years)"], df["TEA (%)"], color=colors, zorder=3)

# curva suavizada
plt.plot(x_smooth, y_smooth_tea, color="tab:orange", zorder=2)

y_min = df["TEA (%)"].min()
y_max = df["TEA (%)"].max()
padding = (y_max - y_min) * 0.15
plt.ylim(y_min - padding, y_max + padding)

y_band = y_max + padding * 0.9

# etiquetas
for _, row in df.iterrows():
    x_i = row["TTM (years)"]
    y_i = row["TEA (%)"]
    label = row["Posición"]

    y_model = np.interp(x_i, x_smooth, y_smooth_tea)

    # línea gris de mispricing
    plt.plot(
        [x_i, x_i],
        [y_i, y_model],
        color="gray",
        linewidth=1,
        alpha=0.5
    )

    # valor del mispricing
    mis = row["Mispricing"] * 10000
    plt.annotate(
        f"{mis:.2f}",
        (x_i, y_band),
        textcoords="offset points",
        xytext=(0, 0),
        ha="center",
        fontsize=8,
        color="gray",
        alpha=0.9
    )

    # arriba: contrato
    plt.annotate(
        label,
        (x_i, y_i),
        textcoords="offset points",
        xytext=(0, 7),
        ha='center',
        fontsize=9,
        fontweight="bold",
        color="black"
    )

    # abajo: TEA
    plt.annotate(
        f"{y_i:.2f}%",
        (x_i, y_i),
        textcoords="offset points",
        xytext=(3, -14),
        ha='center',
        fontsize=9,
        fontweight="bold",
        color="black"
    )

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