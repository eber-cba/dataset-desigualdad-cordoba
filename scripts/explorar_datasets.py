"""Exploración rápida de todos los datasets nuevos"""
import pandas as pd, zipfile, sys

def sec(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print('='*50)

# GTFS
sec("GTFS stops.txt")
with zipfile.ZipFile('data/raw/gtfs_cordoba.zip') as z:
    print("Archivos en ZIP:", [n for n in z.namelist() if not n.endswith('/')])
    with z.open('stops.txt') as f:
        stops = pd.read_csv(f)
    print("Cols:", list(stops.columns))
    print("Filas:", len(stops))
    print(stops[['stop_id','stop_name','stop_lat','stop_lon']].head(5).to_string(index=False))

# Luminarias
sec("LUMINARIAS")
lum = pd.read_csv('data/raw/luminarias_led.csv', encoding='latin1', nrows=5)
print("Cols:", list(lum.columns))
# check if barrio column exists
all_cols = pd.read_csv('data/raw/luminarias_led.csv', encoding='latin1', nrows=0).columns.tolist()
print("ALL COLS:", all_cols)
print(lum.to_string(index=False))

# Comisarias  
sec("COMISARIAS")
com = pd.read_csv('data/raw/comisarias_2023.csv', encoding='latin1', on_bad_lines='skip')
print("Cols:", list(com.columns))
print("Filas:", len(com))
print(com.to_string(index=False))

# Centros vecinales
sec("CENTROS VECINALES")
cv = pd.read_csv('data/raw/centros_vecinales.csv', encoding='latin1', on_bad_lines='skip')
print("Cols:", list(cv.columns))
print("Filas:", len(cv))
print(cv.head(5).to_string(index=False))
