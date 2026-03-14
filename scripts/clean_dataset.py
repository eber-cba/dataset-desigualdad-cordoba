import pandas as pd
import os

def clean_data():
    """
    Script para limpiar el dataset censal de barrios de Córdoba.
    Realiza carga, filtrado de columnas, limpieza de valores nulos/inválidos,
    eliminación de duplicados y guarda el resultado.
    """
    # Definir rutas de archivos
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, '..', 'data', 'raw', 'Barrios_de_Córdoba_con_información_censal_afkGL16.csv')
    output_file = os.path.join(script_dir, '..', 'data', 'processed', 'barrios_cordoba_censal_limpio.csv')

    # 1. Cargar el archivo CSV
    print(f"Cargando el archivo: {input_file}...\n")
    if not os.path.exists(input_file):
        print(f"Error: No se encontró el archivo {input_file}")
        return
        
    df = pd.read_csv(input_file)

    # 2. Mostrar todas las columnas del dataset para inspección
    print("Columnas originales del dataset:")
    print(list(df.columns))
    print("\n" + "-"*40 + "\n")

    # 3. Eliminar columnas que provienen del sistema GIS (si existen)
    # Convertimos los nombres de columnas a minúsculas temporalmente para buscar
    columnas_gis = ['geometry', 'shape_area', 'shape_length', 'objectid']
    columnas_a_eliminar = [col for col in df.columns if col.lower() in columnas_gis]
    
    if columnas_a_eliminar:
        print(f"Eliminando columnas GIS: {columnas_a_eliminar}")
        df = df.drop(columns=columnas_a_eliminar)

    # 4. Renombrar las columnas a nombres simples en minúscula usando snake_case
    # Mapeo manual para las columnas basado en el dataset inspeccionado
    rename_map = {
        'NOMBRE_BAR': 'barrio',
        'Poblacion': 'poblacion',
        'Hogares': 'hogares',
        'NBI(hogares)': 'nbi'
    }
    # Aplicamos el renombrado
    df = df.rename(columns=rename_map)

    # Para cualquier otra columna, la pasamos a minúsculas y reemplazamos caracteres problemáticos 
    # para asegurar un formato snake_case generalizado.
    df.columns = df.columns.astype(str).str.lower().str.replace(' ', '_').str.replace('%', 'pct_').str.replace(r'[^a-zA-Z0-9_]', '', regex=True)

    # Nos aseguramos de actualizar los nombres que usaremos en la selección a continuación
    # (por si acaso el renombrado genérico los afectó, aunque ya los mapeamos).
    columnas_relevantes = ['barrio', 'poblacion', 'hogares', 'nbi']
    
    # 5. Mantener únicamente las columnas relevantes para análisis social de barrios
    # Filtramos para mantener solo las columnas relevantes que existan en el dataframe
    columnas_finales_mantener = [col for col in columnas_relevantes if col in df.columns]
    print(f"Manteniendo solo las columnas relevantes: {columnas_finales_mantener}\n")
    df = df[columnas_finales_mantener].copy()

    # 6. Eliminar filas con barrios vacíos, "SD", "NULL", o "-"
    # Primero convertimos a string y limpiamos espacios en blanco
    df['barrio'] = df['barrio'].astype(str).str.strip()
    
    # Creamos una lista de valores inválidos (en minúscula para hacer una comparación insensible a mayúsculas)
    valores_invalidos = ['nan', 'sd', 'null', '-', '']
    # Filtramos el dataframe conservando las filas donde el barrio no esté en la lista de valores inválidos
    df = df[~df['barrio'].str.lower().isin(valores_invalidos)]

    # 7. Eliminar barrios duplicados si existen (manteniendo la primera aparición)
    df = df.drop_duplicates(subset=['barrio'], keep='first')

    # 8. Mostrar un resumen del dataset limpio
    print("-" * 40)
    print("RESUMEN DEL DATASET LIMPIO")
    print("-" * 40)
    print(f"Número de filas: {len(df)}")
    print(f"Columnas finales: {list(df.columns)}\n")
    print("Primeras 10 filas:")
    print(df.head(10).to_string(index=False)) # Imprimimos las 10 primeras filas sin el índice
    print("\n" + "-" * 40 + "\n")

    # 9. Guardar el resultado en un nuevo CSV
    df.to_csv(output_file, index=False)
    print(f"Resultado guardado exitosamente como: {output_file}")


if __name__ == '__main__':
    clean_data()
