import pandas as pd
import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import os

def generate_pro_map():
    # 1. Carga de datos
    file_path = 'data/processed/dataset_dashboard_v19.csv'
    geojson_path = 'data/processed/dataset_gis_v19.geojson'
    
    if not os.path.exists(file_path) or not os.path.exists(geojson_path):
        print("Error: No se encuentran los archivos de datos.")
        return

    df = pd.read_csv(file_path)
    gdf = gpd.read_file(geojson_path)
    
    # Mapeo manual de descripciones a categorías
    cluster_mapping = {
        'Núcleo Urbano Consolidado': 'Cluster 0: Núcleo consolidado',
        'Anillo Denso Residencial': 'Cluster 0: Núcleo consolidado',
        'Suburbio Popular Consolidado': 'Cluster 1: Zona en transición',
        'Periferia Vulnerable': 'Cluster 2: Periferia vulnerable'
    }
    df['cluster_tag'] = df['cluster_descripcion'].map(cluster_mapping)
    
    # Unir clusters al GeoDataFrame
    gdf = gdf.merge(df[['barrio', 'cluster_tag', 'poblacion', 'pct_nbi']], on='barrio', how='left')

    # Paleta de colores consistente
    custom_palette = {
        'Cluster 0: Núcleo consolidado': '#2ecc71', # Verde
        'Cluster 1: Zona en transición': '#f1c40f', # Amarillo
        'Cluster 2: Periferia vulnerable': '#e74c3c' # Rojo
    }

    # --- PARTE A: GENERAR PNG ESTÁTICO (Para el README) ---
    print("Generando imagen estática PNG...")
    fig, ax = plt.subplots(figsize=(14, 12), dpi=150)
    
    # Dibujar polígonos de barrios
    for cluster, color in custom_palette.items():
        subset = gdf[gdf['cluster_tag'] == cluster]
        subset.plot(ax=ax, color=color, alpha=0.6, edgecolor='white', linewidth=0.3, label=cluster)
    
    # Estética del gráfico
    ax.set_title('Segmentación socioeconómica - Córdoba Capital', fontsize=20, pad=20, fontweight='bold', color='#2c3e50')
    ax.set_axis_off()
    
    # Leyenda personalizada
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], marker='o', color='w', label=k, markerfacecolor=v, markersize=12) for k, v in custom_palette.items()]
    ax.legend(handles=legend_elements, title='Categorización Social', loc='upper right', frameon=True, shadow=True, fontsize=12)

    output_dir = 'figures'
    os.makedirs(output_dir, exist_ok=True)
    png_path = os.path.join(output_dir, 'mapa_clusters_pro.png')
    plt.savefig(png_path, bbox_inches='tight', transparent=False, facecolor='white')
    plt.close()

    # --- PARTE B: GENERAR HTML INTERACTIVO (Para visualización profunda) ---
    print("Generando mapa interactivo HTML...")
    m = folium.Map(location=[-31.42, -64.18], zoom_start=12, tiles='OpenStreetMap')
    
    # Título HTML
    title_html = '<h3 align="center" style="font-size:18px; color: #2c3e50; font-family: Arial;"><b>Segmentación socioeconómica - Córdoba Capital</b></h3>'
    m.get_root().html.add_child(folium.Element(title_html))

    # Agregar marcadores
    for idx, row in df.iterrows():
        color = custom_palette.get(row['cluster_tag'], '#7f8c8d')
        tooltip_content = f"""
            <div style="font-family: Arial; font-size: 12px;">
                <b style="color: {color};">{row['barrio']}</b><br>
                <b>Categoría:</b> {row['cluster_tag']}<br>
                <b>Población:</b> {int(row['poblacion']):,} hab.<br>
                <b>NBI:</b> {row['pct_nbi']}%
            </div>
        """
        folium.CircleMarker(
            location=[row['centroide_lat'], row['centroide_lon']],
            radius=6, color=color, fill=True, fill_color=color, fill_opacity=0.7, tooltip=tooltip_content
        ).add_to(m)

    # Leyenda HTML
    legend_html = f'''
     <div style="position: fixed; bottom: 50px; left: 50px; width: 260px; z-index:9999; font-size:14px;
     background-color: white; opacity: 0.9; padding: 10px; border-radius: 5px; font-family: Arial; border:2px solid #bdc3c7;">
     <b>Categorización Social</b> <br>
     <i class="fa fa-circle" style="color:#2ecc71"></i>&nbsp; Cluster 0: Núcleo consolidado <br>
     <i class="fa fa-circle" style="color:#f1c40f"></i>&nbsp; Cluster 1: Zona en transición <br>
     <i class="fa fa-circle" style="color:#e74c3c"></i>&nbsp; Cluster 2: Periferia vulnerable
     </div>
     '''
    m.get_root().html.add_child(folium.Element(legend_html))

    html_path = os.path.join(output_dir, 'mapa_clusters_pro.html')
    m.save(html_path)
    
    print(f"✅ ¡Éxito! Imagen guardada en: {png_path}")
    print(f"✅ ¡Éxito! Mapa interactivo en: {html_path}")

if __name__ == "__main__":
    generate_pro_map()


