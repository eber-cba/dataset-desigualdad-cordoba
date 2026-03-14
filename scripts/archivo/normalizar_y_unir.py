import pandas as pd
import os
import re

def normalizar_barrio(nombre):
    if pd.isna(nombre):
        return nombre
    nombre = str(nombre).strip().upper()
    # Reemplazos específicos solicitados y otros comunes
    nombre = nombre.replace('Vª', 'VILLA')
    nombre = nombre.replace('Vª ', 'VILLA ')
    nombre = nombre.replace('STA ', 'SANTA ')
    nombre = nombre.replace('STO ', 'SANTO ')
    nombre = nombre.replace('QTAS ', 'QUINTAS ')
    
    # Limpiar múltiples espacios si los hubiera
    nombre = re.sub(r'\s+', ' ', nombre).strip()
    return nombre

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Rutas
    file_escuelas_orig = os.path.join(script_dir, '..', 'data', 'processed', 'escuelas_cordoba_primarias_limpio.csv')
    file_barrios_censal = os.path.join(script_dir, '..', 'data', 'processed', 'barrios_cordoba_censal_limpio.csv')
    
    file_escuelas_agrupado = os.path.join(script_dir, '..', 'data', 'processed', 'escuelas_por_barrio.csv')
    file_final = os.path.join(script_dir, '..', 'data', 'processed', 'dataset_educacion_barrios_cordoba.csv')
    
    print("1. Cargando y normalizando dataset de escuelas primarias...")
    df_escuelas = pd.read_csv(file_escuelas_orig)
    df_escuelas['barrio'] = df_escuelas['barrio'].apply(normalizar_barrio)
    
    print("2. Recalculando cantidad de escuelas por barrio...")
    df_agrupado = df_escuelas.groupby('barrio').size().reset_index(name='escuelas')
    df_agrupado.to_csv(file_escuelas_agrupado, index=False, encoding='utf-8')
    print(f"   - Archivo actualizado: {os.path.basename(file_escuelas_agrupado)}")
    
    print("3. Cargando y normalizando dataset censal de barrios...")
    df_barrios = pd.read_csv(file_barrios_censal)
    df_barrios['barrio'] = df_barrios['barrio'].apply(normalizar_barrio)
    
    print("4. Realizando LEFT JOIN...")
    df_merged = pd.merge(df_barrios, df_agrupado, on='barrio', how='left')
    
    # Llenar nulos con 0 y convertir a entero
    df_merged['escuelas'] = df_merged['escuelas'].fillna(0).astype(int)
    
    # Seleccionar columnas finales
    columnas_finales = ['barrio', 'poblacion', 'hogares', 'nbi', 'escuelas']
    df_final_out = df_merged[columnas_finales]
    
    print("5. Guardando dataset final estructurado...")
    df_final_out.to_csv(file_final, index=False, encoding='utf-8')
    print(f"   - Listo. Guardado en: {os.path.basename(file_final)}")
    print(f"   - Total filas: {len(df_final_out)}")
    
    print("\nMuestra de barrios con escuelas despues del cruce:")
    print(df_final_out[df_final_out['escuelas'] > 0].head(10).to_string(index=False))

if __name__ == "__main__":
    main()
