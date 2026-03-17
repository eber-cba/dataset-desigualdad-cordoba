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
        'Cluster 0: Núcleo consolidado': '#10ac84', # Verde Esmeralda oscuro
        'Cluster 1: Zona en transición': '#f1c40f', # Amarillo
        'Cluster 2: Periferia vulnerable': '#ee5253' # Rojo vivo
    }
    
    # Símbolos para distinción visual
    markers = {
        'Cluster 0: Núcleo consolidado': 'o', # Círculo
        'Cluster 1: Zona en transición': 'D', # Diamante
        'Cluster 2: Periferia vulnerable': 's' # Cuadrado
    }

    # 2. Configuración de la figura
    fig, ax = plt.subplots(figsize=(16, 16), dpi=150)
    
    # --- CAPA 1: POLÍGONOS DE BARRIOS (Contornos muy suaves) ---
    print("Dibujando barrios...")
    gdf_web.plot(ax=ax, color='none', edgecolor='black', linewidth=0.3, alpha=0.2)
    
    # Relleno muy sutil
    for cluster, color in custom_palette.items():
        subset = gdf_web[gdf_web['cluster_tag'] == cluster]
        if not subset.empty:
            subset.plot(ax=ax, color=color, alpha=0.15)

    # --- CAPA 2: MAPA BASE ---
    print("Agregando mapa real detrás...")
    # Usando CartoDB Positron para un look más limpio o OSM original
    cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik, zoom=13, zorder=0, alpha=0.8)
    
    # --- CAPA 3: PUNTOS (HIGHLIGHTS ESTÉTICOS) ---
    points_gdf = gpd.GeoDataFrame(
        df, 
        geometry=gpd.points_from_xy(df.centroide_lon, df.centroide_lat),
        crs="EPSG:4326"
    ).to_crs(epsg=3857)
    
    print("Graficando marcadores mejorados...")
    for cluster, color in custom_palette.items():
        subset = points_gdf[points_gdf['cluster_descripcion'].map(cluster_mapping) == cluster]
        
        # Efecto de sombra/borde: Dibujamos el punto dos veces
        # 1. Borde grueso blanco
        ax.scatter(
            subset.geometry.x, 
            subset.geometry.y, 
            c='white', 
            marker=markers[cluster],
            s=180, 
            zorder=4
        )
        
        # 2. Punto real con color y forma
        ax.scatter(
            subset.geometry.x, 
            subset.geometry.y, 
            c=color, 
            marker=markers[cluster],
            s=120, 
            alpha=1.0, 
            edgecolors='black', 
            linewidth=0.5,
            zorder=5,
            label=cluster
        )

    # 3. Estética y Diseño
    ax.set_title('Mapa Estratégico de Tipologías Urbanas\nCórdoba Capital', 
                 fontsize=26, pad=25, fontweight='bold', color='#2d3436')
    
    ax.set_axis_off()

    # Leyenda mejorada
    leg = ax.legend(title='Categorización Social', title_fontsize='16', 
                    fontsize='13', loc='upper right', frameon=True, shadow=True, borderpad=1)
    leg.get_frame().set_alpha(0.9)

    # 4. Guardado
    output_dir = 'figures'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'mapa_clusters_pro.png')
    
    plt.savefig(output_path, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✅ ¡Éxito! Nueva versión estética generada en: {output_path}")

if __name__ == "__main__":
    generate_pro_map()






