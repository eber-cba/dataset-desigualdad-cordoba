import pandas as pd
import os

def main():
    # Definir rutas relativas a la carpeta del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, '..', 'data', 'processed', 'escuelas_cordoba_primarias_limpio.csv')
    output_file = os.path.join(script_dir, '..', 'data', 'processed', 'escuelas_por_barrio.csv')
    
    print(f"Cargando datos desde: {input_file}")
    
    # Cargar el archivo CSV
    df = pd.read_csv(input_file)
    
    # Agrupar por la columna 'barrio' y contar el número de escuelas (filas)
    # size() cuenta el total de registros por 'barrio' y lo retorna como Serie
    # reset_index() lo convierte en DataFrame y le pone el nombre deseado a la nueva columna
    df_agrupado = df.groupby('barrio').size().reset_index(name='escuelas')
    
    # Guardar en un nuevo CSV
    df_agrupado.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"Proceso finalizado. Total de barrios encontrados: {len(df_agrupado)}")
    print(f"Datos agrupados guardados en: {output_file}")
    
    # Mostrar las primeras filas como ejemplo
    print("\nEjemplo de los primeros registros:")
    print(df_agrupado.head())

if __name__ == "__main__":
    main()
