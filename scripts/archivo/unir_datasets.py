import pandas as pd
import os

def main():
    # Definir rutas relativas a la carpeta del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Archivos de entrada
    file_barrios = os.path.join(script_dir, '..', 'data', 'processed', 'barrios_cordoba_censal_limpio.csv')
    file_escuelas = os.path.join(script_dir, '..', 'data', 'processed', 'escuelas_por_barrio.csv')
    
    # Archivo de salida
    output_file = os.path.join(script_dir, '..', 'data', 'processed', 'dataset_educacion_barrios_cordoba.csv')
    
    print("Cargando datasets...")
    # Cargar ambos datasets
    df_barrios = pd.read_csv(file_barrios)
    df_escuelas = pd.read_csv(file_escuelas)
    
    # Limpiar la columna 'barrio' en ambos datasets: quitar espacios al inicio/fin y convertir a mayúsculas
    # Se convierte antes a string por seguridad para evitar errores con valores nulls o numéricos
    df_barrios['barrio'] = df_barrios['barrio'].astype(str).str.strip().str.upper()
    df_escuelas['barrio'] = df_escuelas['barrio'].astype(str).str.strip().str.upper()
    
    print("Realizando LEFT JOIN...")
    # Realizar un LEFT JOIN usando la columna 'barrio'
    # df_barrios es la tabla izquierda (left) y df_escuelas la derecha (right)
    df_merged = pd.merge(df_barrios, df_escuelas, on='barrio', how='left')
    
    # Reemplazar valores faltantes en 'escuelas' por 0
    # Al hacer un left join, los barrios sin escuelas tendrán NaN, los rellenamos con 0
    df_merged['escuelas'] = df_merged['escuelas'].fillna(0)
    
    # Convertir 'escuelas' de float (resultado del NaN) a entero para mejor presentación
    df_merged['escuelas'] = df_merged['escuelas'].astype(int)
    
    # Asegurar el orden de las columnas finales solicitado
    columnas_finales = ['barrio', 'poblacion', 'hogares', 'nbi', 'escuelas']
    df_final = df_merged[columnas_finales]
    
    # Guardar el resultado
    df_final.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"Resultado guardado en: {output_file}")
    print(f"Total de filas: {len(df_final)}")
    print("\nEjemplo de los primeros registros del dataset final:")
    print(df_final.head())

if __name__ == "__main__":
    main()
