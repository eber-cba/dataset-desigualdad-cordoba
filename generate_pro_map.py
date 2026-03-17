import pandas as pd
import folium
import os

def generate_pro_map():
    # 1. Carga de datos
    # Usamos dataset_dashboard_v19.csv que tiene las descripciones de los clusters
    file_path = 'data/processed/dataset_dashboard_v19.csv'
    if not os.path.exists(file_path):
        print(f"Error: No se encuentra el archivo {file_path}")
        return

    df = pd.read_csv(file_path)
    
    # Mapeo manual de descripciones a categorías simplificadas
    cluster_mapping = {
        'Núcleo Urbano Consolidado': 'Cluster 0: Núcleo consolidado',
        'Anillo Denso Residencial': 'Cluster 0: Núcleo consolidado',
        'Suburbio Popular Consolidado': 'Cluster 1: Zona en transición',
        'Periferia Vulnerable': 'Cluster 2: Periferia vulnerable'
    }
    
    df['cluster_tag'] = df['cluster_descripcion'].map(cluster_mapping)

    # 2. Configuración de colores y mapa
    # Cluster 0: Verde, Cluster 1: Amarillo, Cluster 2: Rojo
    custom_palette = {
        'Cluster 0: Núcleo consolidado': '#2ecc71', # Esmeralda (Verde)
        'Cluster 1: Zona en transición': '#f1c40f', # Girasol (Amarillo)
        'Cluster 2: Periferia vulnerable': '#e74c3c' # Alizarina (Rojo)
    }

    # Crear el mapa base centrado en Córdoba Capital
    # Coordenadas aproximadas: -31.42, -64.18
    m = folium.Map(
        location=[-31.42, -64.18], 
        zoom_start=12,
        tiles='OpenStreetMap',
        control_scale=True
    )

    # Título del mapa
    title_html = '''
             <h3 align="center" style="font-size:18px; color: #2c3e50; font-family: Arial; margin-top: 10px;">
                <b>Segmentación socioeconómica - Córdoba Capital</b>
             </h3>
             '''
    m.get_root().html.add_child(folium.Element(title_html))

    # 3. Agregar los puntos (CircleMarker)
    for idx, row in df.iterrows():
        color = custom_palette.get(row['cluster_tag'], '#7f8c8d')
        
        # Tooltip con información enriquecida
        tooltip_content = f"""
            <div style="font-family: Arial; font-size: 12px;">
                <b style="color: {color};">{row['barrio']}</b><br>
                <b>Categoría:</b> {row['cluster_tag']}<br>
                <b>Población:</b> {int(row['poblacion']):,} habitantes<br>
                <b>NBI:</b> {row['pct_nbi']}%
            </div>
        """
        
        folium.CircleMarker(
            location=[row['centroide_lat'], row['centroide_lon']],
            radius=7,
            color=color,
            weight=1,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            tooltip=tooltip_content
        ).add_to(m)

    # 4. Agregar leyenda (HTML/CSS inyectado)
    legend_html = f'''
     <div style="position: fixed; 
     bottom: 50px; left: 50px; width: 260px; height: 120px; 
     border:2px solid #bdc3c7; z-index:9999; font-size:14px;
     background-color: white; opacity: 0.9;
     padding: 10px; border-radius: 5px; font-family: Arial; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
     <b>Categorización Social</b> <br>
     <i class="fa fa-circle" style="color:#2ecc71"></i>&nbsp; Cluster 0: Núcleo consolidado <br>
     <i class="fa fa-circle" style="color:#f1c40f"></i>&nbsp; Cluster 1: Zona en transición <br>
     <i class="fa fa-circle" style="color:#e74c3c"></i>&nbsp; Cluster 2: Periferia vulnerable
     </div>
     '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # 5. Guardado
    output_dir = 'figures'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, 'mapa_clusters_pro.html')
    m.save(output_path)
    
    print(f"✅ ¡Éxito! Mapa interactivo generado en: {output_path}")

if __name__ == "__main__":
    generate_pro_map()

