"""
regenerar_dataset_v13.py
========================
Pipeline V13 - ADVANCED MLOps & URBAN ANALYTICS (10/10 PROFESIONAL)

Evolución final arquitectónica. Implementa:
1. Data Quality Healthcheck (NaNs, Infinitos, Logic Inconsistencies).
2. K-Means Dinámico: Auto-selección de `k` óptimo (Silhouette & Elbow).
3. Matriz de Correlación y Profiling (Seaborn/Matplotlib).
4. Generación Autómata de 4 Reportes Analíticos (Markdown).
5. Output GeoJSON súper ligero para Mapbox/Kepler.gl.

Autor: Lead Urban Data Scientist & ML Architect
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings

warnings.filterwarnings('ignore')

print("="*65)
print("EJECUTANDO V13: ADVANCED MLOps & URBAN ANALYTICS (10/10)")
print("="*65)

# ── 1. CARGA DE BASE Y DATA QUALITY CONTROL ──────────────────
print("\n[1/8] Iniciando Data Quality Control...")
df = pd.read_csv("data/processed/dataset_final_v10.csv")

# Intentaremos hidratar con los Centroides y Areas V12 equivalentes
centroides_path = "data/processed/centroides_barrios_completo.csv"
if os.path.exists(centroides_path):
    df_geo = pd.read_csv(centroides_path)
    df_geo['barrio'] = df_geo['barrio'].str.strip().str.upper()
    df = pd.merge(df, df_geo[['barrio', 'centroide_lat', 'centroide_lon']], on='barrio', how='left')

# Calcular Area para la base V13 (como en V12)
raw_censo = pd.read_csv("data/raw/Barrios_de_Córdoba_con_información_censal_afkGL16.csv")
nombre_col = "NOMBRE_BAR" if "NOMBRE_BAR" in raw_censo.columns else next((c for c in raw_censo.columns if c.upper() in ("BARRIO", "NOMBRE", "NAME")), None)
raw_censo['barrio_norm'] = raw_censo[nombre_col].str.replace(r'[^A-Z0-9 ]', '', regex=True).str.strip().str.upper()

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

# ── A. Reporte de Data Quality ──
dq_report = ["# Data Quality Report V13", "\n## 1. Verificación de Integridad Lógica y Estructural"]
anomalias = []

num_df = df.select_dtypes(include=[np.number])
if (num_df < 0).sum().sum() > 0: anomalias.append("- **Aviso:** Se detectaron valores negativos inesperados.")
if np.isinf(num_df).sum().sum() > 0: anomalias.append("- **CRÍTICO:** Valores infinitos (Division by Zero) detectados.")
if df.isna().sum().sum() > 0: anomalias.append(f"- **Aviso:** {df.isna().sum().sum()} valores nulos (NaN) detectados.")
if df['barrio'].duplicated().sum() > 0: anomalias.append("- **CRÍTICO:** Existen barrios duplicados en la llave primaria.")
if (df['hogares'] > df['poblacion']).sum() > 0: anomalias.append("- **CRÍTICO:** Barrios donde la cantidad de hogares supera a la población habitante (Anomalía Censo).")

if not anomalias:
    dq_report.append("\n✅ **El dataset es analíticamente prístino. Cero anomalías estructurales detectadas.**")
else:
    dq_report.extend(anomalias)
    df = df.replace([np.inf, -np.inf], 0).fillna(0) # Autocorrector de emergencia para ML

with open("data_quality_report_v13.md", "w", encoding='utf-8') as f: f.write("\n".join(dq_report))

# ── 2. OPTIMIZACIÓN DEL FEATURE ENGINEERING Y LAPLACE ────────
print("[2/8] Feature Engineering: Laplace Smoothing...")
# Suavizado Laplace para Ratio (Evitar ZeroDivs)
df['educacion_ratio_publico_privado'] = ((df['escuelas_estatales'] + 1) / (df['escuelas_privadas'] + 1)).round(2)
df['servicios_basicos_score'] = ((df['tiene_escuela'] + df['tiene_dispensario'] + df['tiene_transporte'])/3).round(2)

# Varianza Check - Se erradica hogares_por_poblacion si existía (se usa tamaño de hogar real)
if 'hogares_por_poblacion' in df.columns: df = df.drop(columns=['hogares_por_poblacion'])
if 'tamano_promedio_hogar' not in df.columns:
    df['tamano_promedio_hogar'] = np.where(df['hogares'] > 0, (df['poblacion'] / df['hogares']).round(2), 0)


# ── 3. MACHINE LEARNING: K-MEANS DINÁMICO & SILHOUETTE ───────
print("\n[3/8] Machine Learning: Searching Optimal 'k' (Elbow Method)...")
cols_clustering = ['poblacion_log', 'pct_nbi', 'infraestructura_score', 'paradas_por_1000_hab', 'escuelas_por_1000_hab']
if 'densidad_poblacional' in df.columns: cols_clustering.append('densidad_poblacional')

df_cluster = df[cols_clustering].fillna(0).copy()
X_scaled = StandardScaler().fit_transform(df_cluster)

inertias = []
silhouettes = []
K_range = range(2, 9)

for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X_scaled, labels))

best_k = K_range[np.argmax(silhouettes)]
print(f" -> K Óptimo calculado (Max Silhouette): {best_k}")

# Plotting
sns.set_theme(style="whitegrid")
fig, ax1 = plt.subplots(figsize=(8, 5))
ax1.plot(K_range, inertias, 'bo-', marker='o', color="teal")
ax1.set_xlabel('Number of Clusters (k)')
ax1.set_ylabel('Inertia (Elbow)', color='teal')
ax2 = ax1.twinx()
ax2.plot(K_range, silhouettes, 'rD-', color="coral")
ax2.set_ylabel('Silhouette Score', color='coral')
plt.title("K-Means Clustering: Optimal K Selection")
plt.savefig("cluster_selection_elbow.png", dpi=300, bbox_inches='tight')
plt.close()

# Entrenamiento Final
final_km = KMeans(n_clusters=best_k, random_state=42, n_init=10)
df['cluster_barrio'] = final_km.fit_predict(X_scaled) 

# Auto-generación de Etiquetas Topográficas
cluster_stats = df.groupby('cluster_barrio')[['pct_nbi', 'infraestructura_score', 'poblacion']].mean()
labels_map = {}
for i in range(best_k):
    nbi = cluster_stats.loc[i, 'pct_nbi']
    inf = cluster_stats.loc[i, 'infraestructura_score']
    
    if nbi > cluster_stats['pct_nbi'].mean() and inf < cluster_stats['infraestructura_score'].mean():
        cat = "Vulnerabilidad Alta / Infraestructura Escasa"
    elif inf > cluster_stats['infraestructura_score'].quantile(0.7):
        cat = "Urbano Consolidado (Alta Infraestructura)"
    elif cluster_stats.loc[i, 'poblacion'] > cluster_stats['poblacion'].mean() * 1.5:
        cat = "Urbano Denso (Alta Población)"
    else:
        cat = "Periferia / Vulnerabilidad Media"
        
    labels_map[i] = f"Cluster {i+1}: {cat}"

df['cluster_descripcion'] = df['cluster_barrio'].map(labels_map)

# ── B. Reporte de Clustering ──
print("[4/8] Escribiendo Clustering Report MD...")
cl_rep = [
    "# Machine Learning Clustering Report V13",
    f"\n## 1. Selección Autómata del Modelo",
    f"- **Best K:** {best_k} (basado en Maximización del Silhouette Score de {max(silhouettes):.3f})",
    "- Gráfico del Codo exportado a `cluster_selection_elbow.png`.",
    "\n## 2. Tipologías Barriales Identificadas (Diagnóstico K-Means)\n"
]
cl_rep.append(df.groupby('cluster_descripcion')[['poblacion', 'pct_nbi', 'infraestructura_score', 'escuelas_por_1000_hab']].mean().round(2).reset_index().to_markdown(index=False))
with open("clustering_report_v13.md", "w", encoding='utf-8') as f: f.write("\n".join(cl_rep))


# ── 4. ANALISIS ESTADISTICO Y CORRELACIONES ──────────────────
print("\n[5/8] Análisis Estadístico y Correlaciones de Pearson...")
corr_cols = ['pct_nbi', 'infraestructura_score', 'poblacion', 'tamano_promedio_hogar', 'escuelas_por_1000_hab', 'paradas_por_1000_hab']
if 'densidad_poblacional' in df.columns: corr_cols.append('densidad_poblacional')

corr_matrix = df[corr_cols].corr()

# Generar Heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", center=0, fmt=".2f")
plt.title("Pearson Correlation Matrix - Urban Features V13")
plt.savefig("correlation_matrix_v13.png", dpi=300, bbox_inches='tight')
plt.close()

# ── C. Reporte Estadístico ──
st_rep = [
    "# Análisis Estadístico Urbano V13",
    "\n## 1. Correlaciones con Pobreza Estructural (pct_nbi)",
    corr_matrix['pct_nbi'].sort_values().to_markdown(),
    "\n## 2. Radiografía de Infraestructura",
    df['infraestructura_score'].describe().to_frame().T.to_markdown()
]
with open("analisis_estadistico_v13.md", "w", encoding='utf-8') as f: f.write("\n".join(st_rep))


# ── 5. PREPARACIÓN ECOSISTEMA GIS & FRONTEND ─────────────────
print("\n[6/8] Optimizando Ecosistema Interactivo (Mapbox/Kepler/Dashboard)")

# Creación de Tooltip HTML (Reducirá peso en el GeoJSON de frontend al tener la data preconstruida)
df['categoria_infraestructura'] = pd.qcut(df['infraestructura_score'].rank(method='first'), q=5, labels=['Muy Baja', 'Baja', 'Media', 'Alta', 'Muy Alta']).astype(str)
df['tooltip_html'] = df.apply(lambda r: f"<b>{r['barrio']}</b><hr>Pob: {r['poblacion']}<br>Cluster: {r['cluster_descripcion']}<br>Infr: {r['categoria_infraestructura']}", axis=1)

# Extracción de diccionario final
# ── D. Reporte de Diccionario ──
dic_md = ["# Data Dictionary - Urban Analytics Platform V13", "\n| Componente Analítico | Datatype | Descripción / Unit |", "|---|---|---|"]
for c in df.columns: dic_md.append(f"| `{c}` | {df[c].dtype} | Feature Urbano (Ver Script) |")
with open("data_dictionary_v13.md", "w", encoding='utf-8') as f: f.write("\n".join(dic_md))


# ── 6. MULTIPLEXADO DE SALIDAS (FINAL) ───────────────────────
print("\n[7/8] Subdividiendo Ecosistema de Datos V13...")
# A. Dashboard (Tabla completa humana)
df.to_csv("data/processed/dataset_dashboard_v13.csv", index=False, encoding='utf-8-sig')

# B. Tensor ML Z-Scored
ml_ignore = ['barrio', 'tooltip_html', 'categoria_infraestructura', 'cluster_descripcion', 'centroide_lat', 'centroide_lon']
features_ml = [c for c in df.select_dtypes(include=[np.number]).columns if c not in ml_ignore]
df_ml = df.copy()
df_ml[features_ml] = StandardScaler().fit_transform(df_ml[features_ml].fillna(0)).round(4)
df_ml.to_csv("data/processed/dataset_ml_v13.csv", index=False, encoding='utf-8-sig')

# C. GIS Vector EPSG:4326 (Liviano para Web)
print("[8/8] Rendering EPSG:4326 GIS GeoJSON...")
if 'centroide_lat' in df.columns and 'centroide_lon' in df.columns:
    df_geo_valid = df.dropna(subset=['centroide_lat', 'centroide_lon']).copy()
    if len(df_geo_valid) > 0:
        geometry = [Point(xy) for xy in zip(df_geo_valid['centroide_lon'], df_geo_valid['centroide_lat'])]
        gdf = gpd.GeoDataFrame(df_geo_valid, geometry=geometry, crs="EPSG:4326")
        
        # Para Leaflet/Kepler la velocidad y peso del JSON es vital. Dejamos solo variables puras Frontend.
        columnas_frontend = ['barrio', 'poblacion', 'infraestructura_score', 'categoria_infraestructura', 'cluster_descripcion', 'tooltip_html', 'geometry']
        gdf_light = gdf[columnas_frontend]
        gdf_light.to_file("data/processed/dataset_gis_v13.geojson", driver="GeoJSON")

print("\n🚀 SUCCESS! ARCHITECTURE V13 'THE GOLDEN ERA' COMPLETED (10/10)")
