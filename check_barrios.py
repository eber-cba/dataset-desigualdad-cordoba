import pandas as pd

try:
    df_clean = pd.read_csv('data/processed/barrios_cordoba_censal_limpio.csv')
    print(f"Candidad de barrios en limpios: {df_clean['barrio'].nunique()}")
except Exception as e:
    print(f"Error reading limpio: {e}")

try:
    df_dashboard = pd.read_csv('data/processed/dataset_dashboard_v19.csv')
    print(f"Candidad de barrios en dashboard: {df_dashboard['barrio'].nunique()}")
except Exception as e:
    print(f"Error reading dashboard: {e}")
