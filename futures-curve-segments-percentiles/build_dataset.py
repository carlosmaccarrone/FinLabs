from datetime import datetime
import pandas as pd

# ------------------ CONTRACTS ------------------

contracts = {
	"DLR112025":"28/11/2025",
	"DLR122025":"30/12/2025",
	"DLR012026":"30/1/2026",
	"DLR022026":"27/2/2026",
	"DLR032026":"31/3/2026",
	"DLR042026":"30/4/2026",
	"DLR052026":"29/5/2026",
	"DLR062026":"30/6/2026",
	"DLR072026":"31/7/2026",
	"DLR082026":"31/8/2026",
	"DLR092026":"30/9/2026",
	"DLR102026":"30/10/2026",
	"DLR112026":"30/11/2026",
	"DLR122026":"30/12/2026",
	"DLR012027":"29/1/2027",
	"DLR022027":"26/2/2027"
} 

# ------------------ LOAD DATA ------------------
def parse_spot(x):
    x = str(x).strip()
    x = x.replace("$", "")

    # si tiene formato argentino: 1.234,56
    if "," in x and "." in x:
        x = x.replace(".", "").replace(",", ".")
    # si ya viene tipo 1394,00
    elif "," in x:
        x = x.replace(",", ".")

    return float(x)

def parse_price(x):
    return float(str(x).replace(",", "."))

spot_df = pd.read_excel("DollarSpot.xlsx")

spot_df["FECHA"] = pd.to_datetime(spot_df["FECHA"], dayfirst=True)
spot_df["SPOT"] = spot_df["DÓLAR UST ART 000"].apply(parse_spot)

hist = pd.read_csv("closing_prices_contratos.csv", sep=";")

hist["fecha"] = pd.to_datetime(hist["FECHA"], dayfirst=True)
hist["ajuste"] = hist["AJUSTE / PRIMA REF."].apply(parse_price)
hist["volumen"] = pd.to_numeric(hist["CONTRATOS"], errors="coerce")

# ------------------ BUILD DATASET ------------------

rows = []

for _, srow in spot_df.iterrows():

    date = srow["FECHA"]
    spot = srow["SPOT"]

    df_day = hist[hist["fecha"] == date]

    for contract, maturity in contracts.items():

        row = df_day[df_day["TIPO CONTRATO"] == contract]

        if row.empty:
            continue

        vol = row["volumen"].values[0]
        if vol < 5000:
            continue

        rows.append({
            "date": date,
            "spot": spot,
            "contract": contract,
            "maturity": pd.to_datetime(maturity, dayfirst=True),
            "price": float(row["ajuste"].values[0]),
            "volume": int(vol)
        })

dataset = pd.DataFrame(rows)

dataset.to_csv("clean_dataset.csv", index=False, sep=";")

# print(dataset.tail(20))
print("\nDONE → clean_dataset.csv generated")
