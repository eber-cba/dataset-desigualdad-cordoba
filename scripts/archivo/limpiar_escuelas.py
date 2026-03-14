import pandas as pd
import os

def main():
    # Rutas de los archivos
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, '..', 'data', 'raw', 'ZONAS_ESCUELAS_MUNICIPALES_Corregido_2.csv')
    output_file = os.path.join(script_dir, '..', 'data', 'processed', 'escuelas_cordoba_primarias_limpio.csv')
    
    print(f"Cargando datos desde: {input_file}")
    
    # 1. Cargar el CSV. 
    # Ignoramos la primera fila (skiprows=1) porque no contiene datos estructurados, 
    # sino el título "ESCUELAS MUNICIPALES".
    df = pd.read_csv(input_file, skiprows=1)
    
    # 2. Separar la columna ESTABLECIMIENTO en "escuela" y "barrio"
    # El separador indicado es "Bº"
    establecimiento_split = df['ESTABLECIMIENTO'].str.split('Bº', n=1, expand=True)
    
    # Asignamos a nuevas columnas y eliminamos espacios en blanco (strip)
    df['escuela'] = establecimiento_split[0].str.strip()
    df['barrio'] = establecimiento_split[1].str.strip()
    
    # 3. Mantener solo las columnas requeridas
    columnas_a_mantener = ['escuela', 'barrio', 'DIRECCION', 'ZONAS']
    df_clean = df[columnas_a_mantener].copy()
    
    # 4. Renombrar columnas a minúsculas/singular según lo solicitado
    df_clean.rename(columns={
        'DIRECCION': 'direccion',
        'ZONAS': 'zona'
    }, inplace=True)
    
    # 5. Guardar el resultado en un nuevo CSV
    df_clean.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Limpieza completada. Datos guardados en: {output_file}")

if __name__ == "__main__":
    main()
