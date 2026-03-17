import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
import os

def generate_pro_map():
    # 1. Carga de datos
    file_path = 'data/processed/dataset_dashboard_v19.csv'
    geojson_path = 'data/processed/dataset_gis_v19.geojson'
    
    if not os.path.exists(file_path) or not os.path.exists(geojson_path):
        print("Error: No se encuentran los archivos de datos (CSV o GeoJSON).")
        return

    # Cargar datos
    df = pd.read_csv(file_path)
    gdf = gpd.read_file(geojson_path)
    
    # Mapeo de clusters
    cluster_mapping = {
        'Núcleo Urbano Consolidado': 'Cluster 0: Núcleo consolidado',
        'Anillo Denso Residencial': 'Cluster 0: Núcleo consolidado',
        'Suburbio Popular Consolidado': 'Cluster 1: Zona en transición',
        'Periferia Vulnerable': 'Cluster 2: Periferia vulnerable'
    }
    df['cluster_tag'] = df['cluster_descripcion'].map(cluster_mapping)
    
    # Unir datos al GeoDataFrame para pintar los polígonos
    gdf = gdf.merge(df[['barrio', 'cluster_tag']], on='barrio', how='left')
    
    # Asegurar CRS y convertir a Web Mercator para el mapa base
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)
    gdf_web = gdf.to_crs(epsg=3857)

    # Colores profesionales
    custom_palette = {
        'Cluster 0: Núcleo consolidado': '#2ecc71', # Verde
        'Cluster 1: Zona en transición': '#f1c40f', # Amarillo
        'Cluster 2: Periferia vulnerable': '#e74c3c' # Rojo
    }

    # 2. Configuración de la figura
    fig, ax = plt.subplots(figsize=(15, 15), dpi=150)
    
    # --- CAPA 1: POLÍGONOS DE BARRIOS (COLOREADOS) ---
    print("Dibujando barrios...")
    for cluster, color in custom_palette.items():
        subset = gdf_web[gdf_web['cluster_tag'] == cluster]
        if not subset.empty:
            subset.plot(ax=ax, color=color, alpha=0.3, edgecolor='black', linewidth=0.4, label=cluster)
    
    # Dibujar barrios sin cluster asignado (si los hay) en gris
    gdf_web[gdf_web['cluster_tag'].isna()].plot(ax=ax, color='#bdc3c7', alpha=0.1, edgecolor='black', linewidth=0.2)

    # --- CAPA 2: MAPA BASE ---
    print("Agregando mapa real detrás...")
    cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik, zoom=13, zorder=0)
    
    # --- CAPA 3: PUNTOS (HIGHLIGHTS) ---
    # Creamos los puntos desde el CSV directamente proyectados
    points_gdf = gpd.GeoDataFrame(
        df, 
        geometry=gpd.points_from_xy(df.centroide_lon, df.centroide_lat),
        crs="EPSG:4326"
    ).to_crs(epsg=3857)
    
    print("Graficando puntos destacados...")
    for cluster, color in custom_palette.items():
        subset = points_gdf[points_gdf['cluster_descripcion'].map(cluster_mapping) == cluster]
        ax.scatter(
            subset.geometry.x, 
            subset.geometry.y, 
            c=color, 
            s=60, 
            alpha=0.9, 
            edgecolors='white', 
            linewidth=0.6,
            zorder=5
        )

    # 3. Estética y Diseño
    ax.set_title('Segmentación Socioeconómica - Córdoba Capital\n(Vista por Barrios e Infraestructura)', 
                 fontsize=22, pad=20, fontweight='bold', color='#2c3e50')
    
    ax.set_axis_off()

    # Leyenda (usando los proxies de las capas plot)
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], marker='s', color='w', label=k, 
                              markerfacecolor=v, markersize=15, alpha=0.6) for k, v in custom_palette.items()]
    ax.legend(handles=legend_elements, title='Categorización Social', title_fontsize='13', 
              fontsize='11', loc='upper right', frameon=True, shadow=True)

    # 4. Guardado
    output_dir = 'figures'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'mapa_clusters_pro.png')
    
    plt.savefig(output_path, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✅ ¡Éxito! Mapa con BARRIOS y FONDO REAL generado en: {output_path}")

if __name__ == "__main__":
    generate_pro_map()





