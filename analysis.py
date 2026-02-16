import pandas as pd

df = pd.read_csv("data.csv", encoding="ISO-8859-1")
print(df.head())

df = df.dropna()

# Usuwamy zwroty (ujemna ilość)
df = df[df["Quantity"] > 0]

# Usuwamy zerowe ceny
df = df[df["UnitPrice"] > 0]

print("Po czyszczeniu:", len(df), "wierszy")

# Obrót = ilość * cena
df["Sales"] = df["Quantity"] * df["UnitPrice"]

# Grupujemy po produkcie
product_sales = (
    df.groupby(["StockCode", "Description"])["Sales"]
    .sum()
    .reset_index()
)

print(product_sales.head())

# Sortujemy od najlepiej sprzedających się
product_sales = product_sales.sort_values("Sales", ascending=False)

# Udział procentowy
total_sales = product_sales["Sales"].sum()
product_sales["Share"] = product_sales["Sales"] / total_sales

# Skumulowany udział
product_sales["CumShare"] = product_sales["Share"].cumsum()

# Klasy ABC
def abc_class(x):
    if x <= 0.80:
        return "A"
    elif x <= 0.95:
        return "B"
    else:
        return "C"

product_sales["ABC"] = product_sales["CumShare"].apply(abc_class)

print(product_sales[["Description", "Sales", "ABC"]].head())

# Konwertujemy datę
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

# Dodajemy miesiąc
df["Month"] = df["InvoiceDate"].dt.to_period("M")

# Liczymy miesięczną sprzedaż
monthly = (
    df.groupby(["StockCode", "Month"])["Sales"]
    .sum()
    .reset_index()
)

# Liczymy średnią i odchylenie
stats = monthly.groupby("StockCode")["Sales"].agg(["mean", "std"]).reset_index()
stats["CV"] = stats["std"] / stats["mean"]

# Klasy XYZ
def xyz_class(cv):
    if cv <= 0.5:
        return "X"
    elif cv <= 1:
        return "Y"
    else:
        return "Z"

stats["XYZ"] = stats["CV"].apply(xyz_class)

print(stats.head())

final = product_sales.merge(stats[["StockCode", "XYZ"]], on="StockCode")
final["Class"] = final["ABC"] + final["XYZ"]

print(final[["Description", "Sales", "Class"]].head())

final.to_excel("ABC_XYZ_results.xlsx", index=False)
print("Zapisano plik ABC_XYZ_results.xlsx")

import matplotlib.pyplot as plt

# ========== WYKRES 1: ile produktów w każdej klasie ==========
class_counts = final["Class"].value_counts().sort_index()

plt.figure(figsize=(8,5))
class_counts.plot(kind="bar")
plt.title("Number of products in ABC-XYZ classes")
plt.xlabel("Class")
plt.ylabel("Number of products")
plt.tight_layout()
plt.savefig("abc_xyz_classes.png")
plt.close()

# ========== WYKRES 2: Pareto ABC ==========
plt.figure(figsize=(8,5))
plt.plot(product_sales["CumShare"].values)
plt.axhline(0.8, linestyle="--")
plt.axhline(0.95, linestyle="--")
plt.title("Pareto curve – ABC classification")
plt.xlabel("Products sorted by sales")
plt.ylabel("Cumulative sales share")
plt.tight_layout()
plt.savefig("abc_pareto.png")
plt.close()

print("Zapisano wykresy")

# ========== PODSUMOWANIE WARTOŚCI KLAS ==========
summary = final.groupby("Class")["Sales"].sum().sort_values(ascending=False)
summary.to_excel("class_summary.xlsx")

print("Podsumowanie klas:")
print(summary)
