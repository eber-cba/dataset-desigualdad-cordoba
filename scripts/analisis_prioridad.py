import pandas as pd
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(script_dir, '..', 'data', 'processed', 'dataset_educacion_barrios_cordoba.csv')

    df = pd.read_csv(file)

    # Limpiar columnas numéricas: remover comas (ej: "1,234" -> 1234) y convertir a numérico
    for col in ['poblacion', 'hogares', 'nbi']:
        df[col] = df[col].astype(str).str.replace(',', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Filtrar solo barrios con datos censales completos
    df_validos = df.dropna(subset=['poblacion', 'nbi']).copy()

    sin_escuelas = df_validos[df_validos['escuelas'] == 0].copy()

    # Percentiles del dataset completo para definir umbrales
    p75_pob = df_validos['poblacion'].quantile(0.75)
    p75_nbi = df_validos['nbi'].quantile(0.75)
    mediana_pob = df_validos['poblacion'].median()

    print(f"=== UMBRALES UTILIZADOS ===")
    print(f"Percentil 75 poblacion: {p75_pob:.0f}")
    print(f"Percentil 75 NBI:       {p75_nbi:.0f}")
    print(f"Mediana poblacion:       {mediana_pob:.0f}")
    print()

    # --- CRITERIO 1: Alta poblacion y sin escuelas ---
    c1 = sin_escuelas[sin_escuelas['poblacion'] >= p75_pob].sort_values('poblacion', ascending=False)

    # --- CRITERIO 2: Alto NBI y sin escuelas ---
    c2 = sin_escuelas[sin_escuelas['nbi'] >= p75_nbi].sort_values('nbi', ascending=False)

    # --- CRITERIO 3: Combinado (poblacion > mediana Y alto NBI) sin escuelas ---
    c3 = sin_escuelas[
        (sin_escuelas['poblacion'] >= mediana_pob) &
        (sin_escuelas['nbi'] >= p75_nbi)
    ].copy()
    # Score de prioridad: normalizar poblacion y NBI y sumar
    c3 = c3.copy()
    c3['score'] = (
        (c3['poblacion'] - c3['poblacion'].min()) / (c3['poblacion'].max() - c3['poblacion'].min()) +
        (c3['nbi'] - c3['nbi'].min()) / (c3['nbi'].max() - c3['nbi'].min())
    )
    c3 = c3.sort_values('score', ascending=False)

    print("=== CRITERIO 1: Alta poblacion sin escuelas (top pobla, percentil 75+) ===")
    print(c1[['barrio', 'poblacion', 'nbi', 'escuelas']].head(20).to_string(index=False))
    print()

    print("=== CRITERIO 2: Alto NBI sin escuelas (percentil 75+) ===")
    print(c2[['barrio', 'poblacion', 'nbi', 'escuelas']].head(20).to_string(index=False))
    print()

    print("=== CRITERIO 3: Barrios PRIORITARIOS (alta poblacion + alto NBI sin escuelas) ===")
    print(c3[['barrio', 'poblacion', 'nbi', 'score', 'escuelas']].head(30).to_string(index=False))

if __name__ == "__main__":
    main()
