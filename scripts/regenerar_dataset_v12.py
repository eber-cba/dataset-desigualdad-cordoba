"""
regenerar_dataset_v12.py
========================
Pipeline V12 - URBAN ANALYTICS & MACHINE LEARNING MASTERY (10/10)

Ejecuta transformaciones finales:
1. Inyección de Área Km2 desde crudo (Cálculo de Densidades Poblacionales).
2. Laplace Smoothing en Ratios Educativos (Prevención Zero-Div).
3. Clustering Espacial y Social K-Means (5 Segmentos Urbanos).
4. Categorización y Tooltips para el consumo en librerías interactivas (React Leaflet).
5. Documentos Auto-Generados: Diccionario de Datos y Diagnóstico Urbano.
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.cluster import KMeans
import os
import re
import warnings
warnings.filterwarnings('ignore')

print("="*65)
print("EJECUTANDO V12: URBAN ANALYTICS Y MACHINE LEARNING (10/10)")
print("="*65)

# 1. Carga de Base V10 Analítica
df = pd.read_csv("data/processed/dataset_final_v10.csv")

# 2. Extracción de Hectáreas desde Censo Crudo para inyectar Área
def normalizar(nombre):
    if pd.isna(nombre): return ''
    n = str(nombre).strip().upper()
    for a, b in [('Á','A'),('É','E'),('Í','I'),('Ó','O'),('Ú','U'),('Ü','U'),('Ñ','N'),
                 ('á','A'),('é','E'),('í','I'),('ó','O'),('ú','U'),('ñ','N')]:
        n = n.replace(a, b)
    return re.sub(r'[^A-Z0-9 ]', '', n).strip()

raw_censo = pd.read_csv("data/raw/Barrios_de_Córdoba_con_información_censal_afkGL16.csv")
nombre_col = "NOMBRE_BAR" if "NOMBRE_BAR" in raw_censo.columns else next((c for c in raw_censo.columns if c.upper() in ("BARRIO", "NOMBRE", "NAME")), None)
raw_censo['barrio_norm'] = raw_censo[nombre_col].apply(normalizar)

if 'SUP_HA_MOD' in raw_censo.columns:
    areas = raw_censo.groupby('barrio_norm')['SUP_HA_MOD'].mean().reset_index()
    areas = areas.rename(columns={'barrio_norm': 'barrio'})
    df = pd.merge(df, areas, on='barrio', how='left')
    df['area_barrio_km2'] = (df['SUP_HA_MOD'] / 100).round(2)
    df = df.drop(columns=['SUP_HA_MOD'])
    
    # Nuevas variables demográficas puras
    df['densidad_poblacional'] = np.where(df['area_barrio_km2'] > 0, (df['poblacion'] / df['area_barrio_km2']).round(2), 0)
    df['densidad_hogares'] = np.where(df['area_barrio_km2'] > 0, (df['hogares'] / df['area_barrio_km2']).round(2), 0)
    df['infraestructura_por_km2'] = np.where(df['area_barrio_km2'] > 0, (df['infraestructura_score'] / df['area_barrio_km2']).round(3), 0)
    print("[1/8] Densidades Urbanas inyectadas empleando area_barrio_km2.")
else:
    print("[1/8] ERROR: No se dispone de SUP_HA_MOD.")

# 3. Corrección Robusta de Ratio Educativo (Laplace Smoothing)
# Laplace evita la división infinita/cero agregando conteos a priori (+1)
df['educacion_ratio_publico_privado'] = ((df['escuelas_estatales'] + 1) / (df['escuelas_privadas'] + 1)).round(2)
print("[2/8] Ratio de educación suavizado con Estimador de Laplace (Sum+1).")

# 4. Ingesta de Coordenadas (GIS)
centroides_path = "data/processed/centroides_barrios_completo.csv"
has_geo = False
if os.path.exists(centroides_path):
    df_geo = pd.read_csv(centroides_path)
    df_geo['barrio'] = df_geo['barrio'].str.strip().str.upper()
    if 'centroide_lat' not in df.columns:
        df = pd.merge(df, df_geo[['barrio', 'centroide_lat', 'centroide_lon']], on='barrio', how='left')
    has_geo = True

# 5. K-Means Clustering Urbano Automático (Machine Learning)
print("[3/8] Entrenando modelo clustering K-Means para segmentar la morfología urbana...")
cols_clustering = ['poblacion', 'pct_nbi', 'infraestructura_score', 'paradas_por_1000_hab', 'escuelas_por_1000_hab']
if 'densidad_poblacional' in df.columns:
    cols_clustering.append('densidad_poblacional')

# StandardScaler es imperativo en K-Means para evitar sesgo Euclidiano
df_cluster = df[cols_clustering].fillna(0).copy()
scaler_km = StandardScaler()
df_cluster_scaled = scaler_km.fit_transform(df_cluster)

kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
df['cluster_barrio'] = kmeans.fit_predict(df_cluster_scaled)

# Generación del Label para el Front-End Map
nbi_means = df.groupby('cluster_barrio')['pct_nbi'].mean()
inf_means = df.groupby('cluster_barrio')['infraestructura_score'].mean()
labels = {i: f"Tipo {chr(65+i)} (Infr {inf_means[i]:.2f} - NBI {nbi_means[i]:.1f}%)" for i in range(5)}
df['cluster_descripcion'] = df['cluster_barrio'].map(labels)

# 6. Preparación para Mapas Interactivos y React Leaflet
print("[4/8] Generando variables interactivas de GIS Front-End (Tooltips y Categorías)")
df['categoria_infraestructura'] = pd.qcut(df['infraestructura_score'].rank(method='first'), q=5, labels=['Muy Baja', 'Baja', 'Media', 'Alta', 'Muy Alta'])
df['categoria_infraestructura'] = df['categoria_infraestructura'].astype(str)
df['tooltip_barrio'] = df.apply(lambda r: f"<b>{r['barrio']}</b><br>Pob: {r['poblacion']}<br>Score: {r['infraestructura_score']:.2f} ({r['categoria_infraestructura']})", axis=1)

# Variables Compuestas Extra
df['servicios_basicos_score'] = ((df['tiene_escuela'] + df['tiene_dispensario'] + df['tiene_transporte'])/3).round(2)
df['infraestructura_por_habitante'] = np.where(df['poblacion'] > 0, (df['infraestructura_score'] / df['poblacion'] * 10000).round(4), 0)

# Rankings y Percentiles
df['ranking_infraestructura'] = df['infraestructura_score'].rank(method='min', ascending=False).astype(int)
df['percentil_infraestructura'] = (df['infraestructura_score'].rank(pct=True) * 100).round(1)


# 7. Diagnóstico Automático MD & Data Dictionary MD
print("[5/8] Redactando Resumen Analítico a Markdown (diagnostico_urbano_v12.md)")
top_infra = df.nlargest(10, 'infraestructura_score')[['barrio', 'infraestructura_score', 'categoria_infraestructura']]
top_nbi = df.nlargest(10, 'pct_nbi')[['barrio', 'pct_nbi', 'poblacion']]
diag_md = [
    "# Diagnóstico Urbano Automático V12 (Geospatial AI)",
    "\n## 🏆 Top 10 Barrios con Mejor Infraestructura", top_infra.to_markdown(index=False),
    "\n## ⚠️ Top 10 Barrios con Mayor Vulnerabilidad (NBI %)", top_nbi.to_markdown(index=False)
]

if 'densidad_poblacional' in df.columns:
    top_dens = df.nlargest(10, 'densidad_poblacional')[['barrio', 'densidad_poblacional', 'area_barrio_km2']]
    diag_md.extend(["\n## 🏢 Top 10 Barrios Hiper-Densos (Habitantes / Km2)", top_dens.to_markdown(index=False)])

with open("diagnostico_urbano_v12.md", "w", encoding="utf-8") as f:
    f.write("\n".join(diag_md))

print("[6/8] Escribiendo Data Dictionary Automático (data_dictionary_v12.md)")
dic_md = ["# Diccionario de Datos V12 - Urban Data Platform", "\n| Variable | Tipo | Rol Analítico |", "|---|---|---|"]
for col in df.columns:
    tipo = str(df[col].dtype)
    rol = "Característica Base Espacial"
    if 'score' in col or 'ratio' in col: rol = "Feature Engineering (Ingeniería Avanzada)"
    elif 'tooltip' in col or 'categoria' in col: rol = "Meta-Feature para Viz (Frontend)"
    elif 'cluster' in col: rol = "Métrica Machine Learning (K-Means)"
    dic_md.append(f"| `{col}` | {tipo} | {rol} |")

with open("data_dictionary_v12.md", "w", encoding="utf-8") as f:
    f.write("\n".join(dic_md))

# 8. Multi-Export System (Dashboard, ML y GeoJSON)
print("[7/8] Subdividiendo Exportaciones Arquitectónicas...")
df.to_csv("data/processed/dataset_dashboard_v12.csv", index=False, encoding='utf-8-sig')

# Data matrix Z-scored para ML Puro
ml_ignore = ['barrio', 'tooltip_barrio', 'categoria_infraestructura', 'cluster_descripcion', 'centroide_lat', 'centroide_lon']
num_cols = df.select_dtypes(include=[np.number]).columns
features_ml = [c for c in num_cols if c not in ml_ignore]
df_ml = df.copy()
df_ml[features_ml] = StandardScaler().fit_transform(df_ml[features_ml].fillna(0)).round(4)
df_ml.to_csv("data/processed/dataset_ml_v12.csv", index=False, encoding='utf-8-sig')

# GeoJSON GIS Vector Ready
if has_geo:
    print("[8/8] Integrando Arquitectura GIS Vector (EPSG:4326)")
    df_geo_valid = df.dropna(subset=['centroide_lat', 'centroide_lon']).copy()
    if len(df_geo_valid) > 0:
        geometry = [Point(xy) for xy in zip(df_geo_valid['centroide_lon'], df_geo_valid['centroide_lat'])]
        gdf = gpd.GeoDataFrame(df_geo_valid, geometry=geometry, crs="EPSG:4326")
        gdf = gdf.drop(columns=['centroide_lat', 'centroide_lon'])
        gdf.to_file("data/processed/dataset_gis_v12.geojson", driver="GeoJSON")

print("\n🚀 DONE! PIPELINE V12 ARQUITECTURA COMPLETADA (10/10)")
