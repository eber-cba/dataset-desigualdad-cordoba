import pandas as pd
import numpy as np
import os

print("Ejecutando Healthcheck Final...")

files = [
    "data/processed/dataset_dashboard_v19.csv",
    "data/processed/dataset_ml_v19.csv",
    "data/processed/dataset_gis_v19.geojson"
]

# Verificamos archivos
for f in files:
    if not os.path.exists(f):
        print(f"Error: falta el archivo {f}")
        exit(1)

df = pd.read_csv("data/processed/dataset_dashboard_v19.csv")
num_cols = df.select_dtypes(include=[np.number]).columns

# Verificamos NaNs y Infinitos
if df[num_cols].isna().sum().sum() > 0:
    print("Error: Existen NaNs en las columnas numéricas.")
    exit(1)

if np.isinf(df[num_cols]).sum().sum() > 0:
    print("Error: Existen valores infinitos en columnas numéricas.")
    exit(1)

# Verificamos Clustering
if 'cluster_descripcion' not in df.columns:
    print("Error: La columna 'cluster_descripcion' no existe.")
    exit(1)

# Verificamos Bounding Box Espacial
if not df['centroide_lat'].between(-32.5, -31.0).all():
    print("Error: Existen centroides fuera de la Latitud válida de Córdoba.")
    exit(1)

if not df['centroide_lon'].between(-64.5, -63.5).all():
    print("Error: Existen centroides fuera de la Longitud válida de Córdoba.")
    exit(1)

print("DATA PIPELINE VERIFIED")
