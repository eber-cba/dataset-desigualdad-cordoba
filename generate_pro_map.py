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
    
    # Asegurar que el GeoDataFrame tenga un CRS (sistema de coordenadas)
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True) # WGS84 (Lat/Lon)

    # Convertir a Web Mercator (EPSG:3857) que es el formato que usan los mapas base como OSM
    gdf_web = gdf.to_crs(epsg=3857)
    
    # Crear un DataFrame con coordenadas de puntos convertidas a Web Mercator
    points_gdf = gpd.GeoDataFrame(
        df, 
        geometry=gpd.points_from_xy(df.centroide_lon, df.centroide_lat),
        crs="EPSG:4326"
    ).to_crs(epsg=3857)

    # Mapeo de clusters
    cluster_mapping = {
        'Núcleo Urbano Consolidado': 'Cluster 0: Núcleo consolidado',
        'Anillo Denso Residencial': 'Cluster 0: Núcleo consolidado',
        'Suburbio Popular Consolidado': 'Cluster 1: Zona en transición',
        'Periferia Vulnerable': 'Cluster 2: Periferia vulnerable'
    }
    points_gdf['cluster_tag'] = points_gdf['cluster_descripcion'].map(cluster_mapping)
    
    # Colores profesionales
    custom_palette = {
        'Cluster 0: Núcleo consolidado': '#2ecc71', # Verde
        'Cluster 1: Zona en transición': '#f1c40f', # Amarillo
        'Cluster 2: Periferia vulnerable': '#e74c3c' # Rojo
    }

    # 2. Configuración de la figura
    fig, ax = plt.subplots(figsize=(15, 15), dpi=150)
    
    # --- CAPA 1: MAPA BASE (OpenStreetMap) ---
    print("Agregando mapa base...")
    # Dibujamos primero los límites de los barrios con transparencia para definir el área
    gdf_web.plot(ax=ax, alpha=0.1, edgecolor='black', linewidth=0.5)
    
    # Agregar el mapa base real debajo
    cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik, zoom=13)
    
    # --- CAPA 2: PUNTOS DE CLUSTERS ---
    print("Graficando puntos...")
    for cluster, color in custom_palette.items():
        subset = points_gdf[points_gdf['cluster_tag'] == cluster]
        ax.scatter(
            subset.geometry.x, 
            subset.geometry.y, 
            c=color, 
            label=cluster, 
            s=80, 
            alpha=0.8, 
            edgecolors='black', 
            linewidth=0.5,
            zorder=5
        )

    # 3. Estética y Diseño
    ax.set_title('Segmentación Socioeconómica - Córdoba Capital', 
                 fontsize=22, pad=20, fontweight='bold', color='#2c3e50')
    
    # Ocultar ejes pero mantener el marco
    ax.set_axis_off()

    # Leyenda elegante
    ax.legend(title='Tipologías Urbanas', title_fontsize='13', fontsize='11', 
              loc='upper right', frameon=True, shadow=True)

    # 4. Guardado
    output_dir = 'figures'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'mapa_clusters_pro.png')
    
    plt.savefig(output_path, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✅ ¡Éxito! Imagen con MAPA REAL generada en: {output_path}")

if __name__ == "__main__":
    generate_pro_map()




