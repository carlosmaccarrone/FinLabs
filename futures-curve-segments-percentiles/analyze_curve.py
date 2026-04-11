from scipy.interpolate import UnivariateSpline
from datetime import datetime, time
import pandas as pd
import numpy as np

# ================== READ DATA ==================

df = pd.read_csv("clean_dataset.csv", sep=";")

df["date"] = pd.to_datetime(df["date"])
df["maturity"] = pd.to_datetime(df["maturity"])

# ================== BUCKETS ==================

buckets = {
	"short": (0, 0.25),    # 0–3 meses
	"mid": (0.25, 0.6),    # 3–7 meses
	"long": (0.6, 1.5)     # 7+ meses
}

# ================== CALCULATE CURVE ==================

results = []

for date, group in df.groupby("date"):
	
	if len(group) < 4:
		continue

	spot = group["spot"].iloc[0]

	x = []
	y = []
	weights = []
	vols = []

	for _, row in group.iterrows():
		maturity = row["maturity"]
		price = row["price"]

		now = datetime.combine(date, time(15, 0))
		maturity_dt = datetime.combine(maturity, time(15, 0))

		ttm = (maturity_dt - now).total_seconds() / (365 * 24 * 60 * 60)

		if ttm <= 0:
			continue

		x.append(ttm)
		y.append(np.log(price / spot))
		weights.append(np.sqrt(row["volume"]))
		vols.append(row["volume"])

	if len(x) < 4:
		continue

	# ===== ordenar por TTM =====
	x = np.array(x)
	y = np.array(y)
	weights = np.array(weights)
	vols = np.array(vols)

	idx = np.argsort(x)

	x = x[idx]
	y = y[idx]
	weights = weights[idx]
	vols = vols[idx]

	# ===== normalizar pesos =====
	weights = weights / weights.max()

	# ===== spline =====
	spline = UnivariateSpline(x, y, w=weights, s=0.0001)

	# ===== mispricing por nodo =====
	mispricing_list = []

	for i in range(len(x)):
		y_curve = spline(x[i])

		tea_real = (np.exp(y[i]) ** (1 / x[i]) - 1)
		tea_curve = (np.exp(y_curve) ** (1 / x[i]) - 1)

		mispricing = (tea_real - tea_curve) * 100
		mispricing_list.append(mispricing)

	mispricing_array = np.array(mispricing_list)

	# ===== calcular buckets =====
	bucket_results = {}

	for name, (low, high) in buckets.items():
		
		mask = (x >= low) & (x < high)

		if mask.sum() < 1:
			bucket_results[name] = np.nan
			continue

		vols_bucket = vols[mask]
		vols_bucket = vols_bucket / vols_bucket.sum()

		mispricing_bucket = np.sum(mispricing_array[mask] * vols_bucket)

		bucket_results[name] = mispricing_bucket

	results.append({
		"date": date,
		"short": bucket_results["short"],
		"mid": bucket_results["mid"],
		"long": bucket_results["long"]
	})

# ================== RESULTADOS ==================
def interpret_signal(percentile, zscore):
    
    if percentile > 90 and abs(zscore) > 1.5:
        return "🔴 EXTREMO CARO"
    
    if percentile < 10 and abs(zscore) > 1.5:
        return "🟢 EXTREMO BARATO"
    
    if percentile > 75:
        return "🟠 CARO"
    
    if percentile < 25:
        return "🟢 BARATO"
    
    return "🟡 NEUTRO"

df_res = pd.DataFrame(results).sort_values("date")

if df_res.empty:
	print("No hay suficientes datos para calcular curvas.")
	exit()

print("\n=== HISTÓRICO POR TRAMOS ===")
# print(df_res)

last_row = df_res.iloc[-1]

for col in ["short", "mid", "long"]:
	
	series = df_res[col].dropna()
	
	if len(series) < 5:
		print(f"\n{col.upper()} → datos insuficientes")
		continue

	last_value = last_row[col]

	if pd.isna(last_row[col]):
		print(f"\n=== {col.upper()} ===")
		print("No hay datos en la última fecha para este tramo")
		continue

	percentile = (series < last_value).mean() * 100
	mean = series.mean()
	std = series.std()
	zscore = (last_value - mean) / std if std != 0 else 0
	signal = interpret_signal(percentile, zscore)

	print(f"\n=== {col.upper()} ===")
	print(f"Mispricing: {last_value:.4f}")
	print(f"Percentil: {percentile:.2f}%")
	print(f"Media: {mean:.4f}")
	print(f"Std: {std:.4f}")
	print(f"Z-score: {zscore:.2f}")
	print(f"Señal: {signal}")

spread_sl = last_row["short"] - last_row["long"]

if spread_sl > 0.05:
    print("\n🔴 Curva invertida FUERTE\n")
elif spread_sl > 0:
    print("\n🟡 Curva levemente invertida\n")