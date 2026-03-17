import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

def generate_pro_map():
    # 1. Configuración de estilos
    sns.set_theme(style="whitegrid")
    
    # 2. Carga de datos
    # Usamos dataset_dashboard_v19.csv que tiene las descripciones de los clusters
    file_path = 'data/processed/dataset_dashboard_v19.csv'
    if not os.path.exists(file_path):
        print(f"Error: No se encuentra el archivo {file_path}")
        return

    df = pd.read_csv(file_path)
    
    # Mapeo manual de descripciones a categorías simplificadas para la leyenda profesional solicitada
    # Lógica basada en el análisis previo del proyecto
    cluster_mapping = {
        'Núcleo Urbano Consolidado': 'Cluster 0: Núcleo consolidado',
        'Anillo Denso Residencial': 'Cluster 0: Núcleo consolidado',
        'Suburbio Popular Consolidado': 'Cluster 1: Zona en transición',
        'Periferia Vulnerable': 'Cluster 2: Periferia vulnerable'
    }
    
    df['cluster_tag'] = df['cluster_descripcion'].map(cluster_mapping)

    # 3. Crear la visualización
    plt.figure(figsize=(14, 10), dpi=150)
    
    # Paleta moderna y profesional
    # Cluster 0: Azul/Verde (Estable), Cluster 1: Amarillo/Naranja (Transición), Cluster 2: Rojo/Rosa (Vulnerable)
    custom_palette = {
        'Cluster 0: Núcleo consolidado': '#2ecc71', # Esmeralda
        'Cluster 1: Zona en transición': '#f1c40f',  # Girasol
        'Cluster 2: Periferia vulnerable': '#e74c3c' # Alizarina (Rojo)
    }

    # Dibujar el scatter plot
    # Aumentamos el tamaño basado en la población para dar una sensación de densidad, o fijo según pedido
    scatter = sns.scatterplot(
        data=df,
        x='centroide_lon',
        y='centroide_lat',
        hue='cluster_tag',
        palette=custom_palette,
        s=120,          # Tamaño sugerido aumentado
        alpha=0.7,      # Transparencia para solapamiento
        edgecolor='w',  # Borde blanco para suavizar
        linewidth=0.5
    )

    # 4. Estética de mapa (limpieza total)
    plt.title('Mapa Estratégico de Tipologías Urbanas - Córdoba Capital', fontsize=18, pad=20, fontweight='bold', color='#2c3e50')
    plt.xlabel('Longitud', fontsize=12, color='#7f8c8d')
    plt.ylabel('Latitud', fontsize=12, color='#7f8c8d')
    
    # Ajustar leyenda
    plt.legend(title='Categorización Social', title_fontsize='13', fontsize='11', loc='upper right', frameon=True, shadow=True)

    # Eliminar spines innecesarios
    sns.despine(left=True, bottom=True)

    # 5. Centrado y Zoom (basado en los datos de Córdoba)
    # Limites aproximados de la ciudad para evitar outliers geográficos si los hubiera
    plt.xlim(df['centroide_lon'].min() - 0.02, df['centroide_lon'].max() + 0.02)
    plt.ylim(df['centroide_lat'].min() - 0.02, df['centroide_lat'].max() + 0.02)

    # 6. Guardado
    output_dir = 'figures'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, 'mapa_clusters_pro.png')
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    
    print(f"✅ ¡Éxito! Mapa profesional generado en: {output_path}")

if __name__ == "__main__":
    generate_pro_map()
