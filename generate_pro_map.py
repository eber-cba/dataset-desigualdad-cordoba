import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import seaborn as sns

def generate_pro_map():
    # 1. Carga de datos
    file_path = 'data/processed/dataset_dashboard_v19.csv'
    geojson_path = 'data/processed/dataset_gis_v19.geojson'
    
    if not os.path.exists(file_path) or not os.path.exists(geojson_path):
        print("Error: No se encuentran los archivos de datos (CSV o GeoJSON).")
        return

    # Cargar datos tabulares y geográficos
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
    
    # Colores profesionales
    custom_palette = {
        'Cluster 0: Núcleo consolidado': '#2ecc71', # Verde esmeralda
        'Cluster 1: Zona en transición': '#f1c40f', # Amarillo girasol
        'Cluster 2: Periferia vulnerable': '#e74c3c' # Rojo alizarina
    }

    # 2. Configuración de la figura
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(15, 15), dpi=150)
    
    # --- CAPA 1: FONDO DE BARRIOS ---
    # Dibujamos todos los barrios en un gris muy suave para dar contexto geográfico
    gdf.plot(ax=ax, color='#f2f2f2', edgecolor='#d1d1d1', linewidth=0.5, alpha=0.8)
    
    # --- CAPA 2: PUNTOS DE CLUSTERS ---
    # Dibujamos los puntos (centroides) sobre el mapa de fondo
    for cluster, color in custom_palette.items():
        subset = df[df['cluster_tag'] == cluster]
        ax.scatter(
            subset['centroide_lon'], 
            subset['centroide_lat'], 
            c=color, 
            label=cluster, 
            s=100, 
            alpha=0.9, 
            edgecolors='white', 
            linewidth=0.8,
            zorder=3
        )

    # 3. Estética y Diseño
    ax.set_title('Segmentación Socioeconómica - Córdoba Capital', 
                 fontsize=24, pad=30, fontweight='bold', color='#1a252f', family='sans-serif')
    
    # Eliminamos ejes para que parezca un mapa limpio
    ax.set_axis_off()
    
    # Añadimos una anotación de fuente o contexto
    plt.text(0.99, 0.01, 'Fuente: Datos Abiertos Municipalidad de Cba / INDEC', 
             transform=ax.transAxes, ha='right', fontsize=10, color='#7f8c8d')

    # Leyenda elegante
    leg = ax.legend(title='Tipologías Urbanas', title_fontsize='15', fontsize='12', 
                    loc='upper right', frameon=True, shadow=True, borderpad=1)
    leg.get_frame().set_edgecolor('#bdc3c7')

    # 4. Guardado y Limpieza
    output_dir = 'figures'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'mapa_clusters_pro.png')
    
    # Guardar con fondo blanco sólido
    plt.savefig(output_path, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    
    # Eliminar el archivo HTML si existe (pedido del usuario)
    html_file = os.path.join(output_dir, 'mapa_clusters_pro.html')
    if os.path.exists(html_file):
        os.remove(html_file)
        print(f"🗑️ Archivo HTML eliminado: {html_file}")

    print(f"✅ ¡Éxito! Mapa estático generado con fondo cartográfico en: {output_path}")

if __name__ == "__main__":
    generate_pro_map()



