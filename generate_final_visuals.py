import os

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from shapely.geometry import Point
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# Cargar dataset final
df = pd.read_csv("data/processed/dataset_dashboard_v19.csv")

# 1. Mapa de Clusters Urbanos
print("Generando mapa_clusters_barrios_final.png...")
df_geo = df.dropna(subset=["centroide_lon", "centroide_lat"]).copy()
gdf = gpd.GeoDataFrame(
    df_geo,
    geometry=[
        Point(xy) for xy in zip(df_geo["centroide_lon"], df_geo["centroide_lat"])
    ],
    crs="EPSG:4326",
)

fig, ax = plt.subplots(1, 1, figsize=(10, 10))
colormap = {
    "Núcleo Urbano Consolidado": "#0ea5e9",
    "Anillo Denso Residencial": "#8b5cf6",
    "Suburbio Popular Consolidado": "#10b981",
    "Periferia Vulnerable": "#e11d48",
    "Área Mixta de Transición P1": "#f59e0b",
    "Área Mixta de Transición P2": "#f59e0b",
    "Área Mixta de Transición P3": "#f59e0b",
}

for desc in gdf["cluster_descripcion"].unique():
    subset = gdf[gdf["cluster_descripcion"] == desc]
    color = colormap.get(desc, "#555555")
    subset.plot(
        ax=ax,
        markersize=50,
        color=color,
        label=desc,
        alpha=0.85,
        edgecolor="black",
        linewidth=0.5,
    )

ax.legend(title="Tipología Urbana Final", loc="best")
plt.title(
    "Zonificación Socio-Urbana de Córdoba (Modelado K-Means)",
    fontsize=14,
    fontweight="bold",
)
plt.grid(True, linestyle=":", alpha=0.4)
plt.savefig("mapa_clusters_barrios_final.png", dpi=300, bbox_inches="tight")
plt.close()


# 2. PCA Visualization
print("Generando clusters_pca_visualization.png...")
cols_clustering = [
    "poblacion_log",
    "pct_nbi",
    "infraestructura_score",
    "densidad_poblacional",
]
X_raw = df[cols_clustering].fillna(0)
X_scaled = StandardScaler().fit_transform(X_raw)

pca = PCA(n_components=2, random_state=42)
pca_coords = pca.fit_transform(X_scaled)
df["pca_x"] = pca_coords[:, 0]
df["pca_y"] = pca_coords[:, 1]
var_expl = pca.explained_variance_ratio_.sum() * 100

fig, ax = plt.subplots(figsize=(10, 7))
sns.scatterplot(
    x=df["pca_x"],
    y=df["pca_y"],
    hue=df["cluster_descripcion"],
    palette=colormap,
    s=100,
    alpha=0.8,
    edgecolor="black",
    ax=ax,
)
plt.title(
    f"PCA Separación de Clusters (Varianza Explicada: {var_expl:.1f}%)",
    fontweight="bold",
)
plt.xlabel("Componente Principal 1")
plt.ylabel("Componente Principal 2")
plt.legend(title="Tipología", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig("clusters_pca_visualization.png", dpi=300)
plt.close()


# 3. Feature Importance
print("Generando feature_importance_clusters.png...")
rf = RandomForestClassifier(random_state=42, n_estimators=100)
# Reconstruir target
from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
base_labels = le.fit_transform(df["cluster_descripcion"].astype(str))
rf.fit(X_scaled, base_labels)

feat_imp = pd.DataFrame(
    {"Variable": cols_clustering, "Importancia": rf.feature_importances_}
).sort_values("Importancia", ascending=False)

plt.figure(figsize=(8, 5))
sns.barplot(x="Importancia", y="Variable", data=feat_imp, palette="magma")
plt.title("Feature Importance (Surrogate Random Forest)")
plt.xlabel("Importancia Relativa")
plt.ylabel("Variable")
plt.tight_layout()
plt.savefig("feature_importance_clusters.png", dpi=300)
plt.close()

print("Métricas Visuales Extraídas Exitosamente.")
