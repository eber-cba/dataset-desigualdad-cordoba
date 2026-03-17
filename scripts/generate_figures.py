import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import geopandas as gpd
import os

# Create figures directory
os.makedirs('figures', exist_ok=True)

# 1. Load Data
df = pd.read_csv('data/processed/dataset_dashboard_v19.csv')

# Use actual numeric columns for clustering / PCA / Heatmap
numeric_cols = ['pct_nbi', 'escuelas_por_1000_hab', 'paradas_por_1000_hab', 'luminarias_por_1000_hab', 'dispensarios_municipales', 'comisarias', 'centros_vecinales', 'infraestructura_score']
available_cols = [c for c in numeric_cols if c in df.columns]

if 'cluster' not in df.columns:
    if 'cluster_kmeans' in df.columns:
        df['cluster'] = df['cluster_kmeans']
    else:
        # Fit KMeans if not present
        kmeans_model = KMeans(n_clusters=3, init='k-means++', random_state=42, n_init=10)
        X = df[available_cols].fillna(0)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        df['cluster'] = kmeans_model.fit_predict(X_scaled)
        
        # Name the clusters according to average NBI
        cluster_means = df.groupby('cluster')['pct_nbi'].mean().sort_values()
        cluster_mapping = {cluster_means.index[0]: 'Núcleo Consolidado', cluster_means.index[1]: 'Zona en Transición', cluster_means.index[2]: 'Periferia Vulnerable'}
        df['cluster'] = df['cluster'].map(cluster_mapping)

# For other models, regenerate X_scaled with new variables
X = df[available_cols].fillna(0)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# A. Mapa geográfico de clusters
try:
    gdf = gpd.read_file('data/processed/dataset_gis_v19.geojson')
    # Merge with df to get 'cluster'
    gdf = gdf.merge(df[['barrio', 'cluster']], on='barrio', how='left')
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    gdf.plot(column='cluster', ax=ax, legend=True, cmap='viridis', 
             edgecolor='white', linewidth=0.2)
    ax.set_title("Identificación de Tipologías Urbanas en Córdoba (Clusters)", fontsize=16, fontweight='bold', pad=20)
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig('figures/mapa_clusters.png', dpi=300, bbox_inches='tight')
    plt.close()
except Exception as e:
    print(f"Error drawing map: {e}")

# B. Elbow Method
wcss = []
K_range = range(1, 11)
for i in K_range:
    kmeans = KMeans(n_clusters=i, init='k-means++', random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    wcss.append(kmeans.inertia_)
plt.figure(figsize=(10, 6))
plt.plot(K_range, wcss, marker='o', linestyle='--', color='#2563eb', linewidth=2, markersize=8)
plt.title('Método del Codo (Elbow Method) para determinar K óptimo', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Número de Clusters (K)', fontsize=12)
plt.ylabel('Inercia (WCSS)', fontsize=12)
plt.xticks(K_range)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('figures/elbow.png', dpi=300, bbox_inches='tight')
plt.close()

# C. Perfil de clusters
cluster_profile = df.groupby('cluster')[available_cols].mean().reset_index()
# Normalize for radar or use bar
cluster_profile_melted = cluster_profile.melt(id_vars='cluster', var_name='Variable', value_name='Promedio')
plt.figure(figsize=(12, 6))
sns.barplot(data=cluster_profile_melted, x='Variable', y='Promedio', hue='cluster', palette='viridis')
plt.title('Perfil Promedio de Variables por Cluster', fontsize=14, fontweight='bold', pad=15)
plt.xticks(rotation=45, ha='right')
plt.legend(title='Cluster')
plt.tight_layout()
plt.savefig('figures/perfil_clusters.png', dpi=300, bbox_inches='tight')
plt.close()

# D. Ranking de barrios vulnerables
top_10_nbi = df.sort_values(by='pct_nbi', ascending=False).head(10)
plt.figure(figsize=(10, 6))
sns.barplot(data=top_10_nbi, y='barrio', x='pct_nbi', palette='magma')
plt.title('Top 10 Barrios con Mayor Vulnerabilidad Social (% NBI)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Porcentaje de NBI (%)', fontsize=12)
plt.ylabel('Barrio', fontsize=12)
for i, v in enumerate(top_10_nbi['pct_nbi']):
    plt.text(v + 0.5, i, f"{v:.1f}%", color='black', va='center')
plt.tight_layout()
plt.savefig('figures/ranking_vulnerables.png', dpi=300, bbox_inches='tight')
plt.close()

# E. Heatmap de correlación
plt.figure(figsize=(10, 8))
corr = df[available_cols].corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", vmin=-1, vmax=1, linewidths=0.5)
plt.title('Matriz de Correlación de Variables Socio-Urbanas', fontsize=14, fontweight='bold', pad=15)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('figures/heatmap_correlacion.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. Mejora del scatter plot (PCA) actual
pca = PCA(n_components=2)
components = pca.fit_transform(X_scaled)
df['PCA1'] = components[:, 0]
df['PCA2'] = components[:, 1]
plt.figure(figsize=(10, 8))
sns.scatterplot(data=df, x='PCA1', y='PCA2', hue='cluster', palette='Set1', s=100, alpha=0.8, edgecolor='w')
plt.title('Proyección PCA de Tipologías Urbanas (Análisis de Componentes Principales)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel(f'Componente Principal 1 ({pca.explained_variance_ratio_[0]*100:.1f}%)', fontsize=12)
plt.ylabel(f'Componente Principal 2 ({pca.explained_variance_ratio_[1]*100:.1f}%)', fontsize=12)
plt.legend(title='Tipología (Cluster)', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('figures/clusters_pca_visualization.png', dpi=300, bbox_inches='tight')
plt.close()

print("Todas las figuras generadas en /figures/")
