"""
integrar_escuelas_idecor.py
============================
Integra los datos de Establecimientos Educativos descargados del WFS de IDECOR
(MapasCórdoba) al dataset final de barrios de Córdoba.

Fuente de escuelas : data/raw/escuelas_cordoba.csv
                     (5,471 establecimientos — todos niveles, estatal y privado)
Dataset base       : data/processed/dataset_final_v4.csv
Salida             : data/processed/dataset_final_v5.csv

Columnas nuevas generadas:
  - escuelas_total     : total de establecimientos asignados al barrio (todos)
  - escuelas_estatales : solo establecimientos del sector ESTATAL (público)
  - escuelas_privadas  : solo establecimientos del sector PRIVADO

Estrategia de asignación:
  - Se filtra a la ciudad de Córdoba (departamento == "Capital" o bbox de coords)
  - Se usa KD-tree con centroides de barrio (igual que integrador_dataset.py)
  - Los centroides se derivan del archivo centros_salud_limpio.csv (91 barrios)

Autor  : Eber Coronel — DiploDatos 2026 / FAMAF-UNC
Versión: 1.0 — 2026-03-14
"""

import pandas as pd
from scipy.spatial import cKDTree

# ─────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────

# Bounding box aproximado de la ciudad de Córdoba capital
# (para filtrar solo establecimientos dentro del municipio)
LAT_MIN, LAT_MAX = -31.55, -31.20
LON_MIN, LON_MAX = -64.35, -64.00

# Valores conocidos en la columna est_sector
SECTOR_ESTATAL  = "Estatal"
SECTOR_PRIVADO  = "Privado"


# ─────────────────────────────────────────────────────────────
# FUNCIONES AUXILIARES
# ─────────────────────────────────────────────────────────────

def asignar_por_centroide(df: pd.DataFrame,
                          lat_col: str,
                          lon_col: str,
                          centroides: pd.DataFrame) -> pd.Series:
    """
    Asigna a cada fila de `df` el barrio más cercano usando KD-tree.
    Filas sin coordenadas válidas reciben cadena vacía ''.

    Args:
        df         : DataFrame con columnas de latitud y longitud.
        lat_col    : Nombre de la columna de latitud.
        lon_col    : Nombre de la columna de longitud.
        centroides : DataFrame con columnas 'barrio', 'centroide_lat', 'centroide_lon'.

    Returns:
        Series con el nombre del barrio asignado (mismo índice que df).
    """
    validos = df[[lat_col, lon_col]].dropna()
    result  = pd.Series([""] * len(df), index=df.index)

    if validos.empty:
        return result

    coords_centroid = centroides[["centroide_lat", "centroide_lon"]].values
    tree = cKDTree(coords_centroid)
    _, idx = tree.query(validos[[lat_col, lon_col]].values)
    result.loc[validos.index] = centroides["barrio"].iloc[idx].values
    return result


def conteo_por_barrio(df: pd.DataFrame, col_nombre: str) -> pd.DataFrame:
    """
    Cuenta filas por barrio y devuelve un DataFrame con columnas
    ['barrio', col_nombre].
    """
    return (
        df[df["barrio_asignado"] != ""]
        .groupby("barrio_asignado")
        .size()
        .reset_index(name=col_nombre)
        .rename(columns={"barrio_asignado": "barrio"})
    )


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

print("=" * 60)
print("SCRIPT: integrar_escuelas_idecor.py")
print("Agrega columnas de establecimientos educativos IDECOR")
print("al dataset_final_v4.csv → genera dataset_final_v5.csv")
print("=" * 60)


# ── 1. Cargar base v4 ────────────────────────────────────────
print("\n[1/6] Cargando base v4...")
base = pd.read_csv("data/processed/dataset_final_v4.csv")
print(f"      {len(base)} barrios  |  columnas: {list(base.columns)}")


# ── 2. Calcular centroides de barrio ─────────────────────────
print("\n[2/6] Calculando centroides de barrio (desde centros de salud)...")
cs = pd.read_csv("data/processed/centros_salud_limpio.csv")
centroides = (
    cs.groupby("barrio")
    .agg(centroide_lat=("latitud", "mean"),
         centroide_lon=("longitud", "mean"))
    .reset_index()
)
print(f"      {len(centroides)} centroides calculados")


# ── 3. Cargar y filtrar escuelas IDECOR ──────────────────────
print("\n[3/6] Cargando establecimientos educativos IDECOR...")
esc = pd.read_csv("data/raw/escuelas_cordoba.csv")
print(f"      Total descargado  : {len(esc):,} establecimientos")
print(f"      Columnas          : {list(esc.columns)}")

# Convertir coordenadas
esc["lat"] = pd.to_numeric(esc["lat"], errors="coerce")
esc["lon"] = pd.to_numeric(esc["lon"], errors="coerce")

# Filtrar solo ciudad de Córdoba Capital
# Estrategia 1: por departamento (si la columna existe)
if "est_departamento" in esc.columns:
    esc_capital = esc[
        esc["est_departamento"].str.strip().str.lower() == "capital"
    ].copy()
    print(f"      Filtro Departamento Capital: {len(esc_capital):,} establecimientos")
else:
    esc_capital = esc.copy()

# Estrategia 2: bbox geográfico (filtro adicional o único si no hay depto)
esc_ciudad = esc_capital[
    esc_capital["lat"].between(LAT_MIN, LAT_MAX) &
    esc_capital["lon"].between(LON_MIN, LON_MAX)
].copy()

print(f"      Filtro bbox ciudad: {len(esc_ciudad):,} establecimientos")
print(f"      Descartados (fuera de la ciudad): {len(esc) - len(esc_ciudad):,}")

# Revisar valores de sectores disponibles
sectores = esc_ciudad["est_sector"].value_counts().to_dict() if "est_sector" in esc_ciudad.columns else {}
print(f"      Sectores encontrados: {sectores}")

# Revisar niveles disponibles
if "nivel" in esc_ciudad.columns:
    niveles = esc_ciudad["nivel"].value_counts().to_dict()
    print(f"      Niveles encontrados: {niveles}")


# ── 4. Asignar barrio por cercanía al centroide ──────────────
print("\n[4/6] Asignando barrio por KD-tree...")
esc_ciudad["barrio_asignado"] = asignar_por_centroide(
    esc_ciudad, "lat", "lon", centroides
)
asignados = (esc_ciudad["barrio_asignado"] != "").sum()
print(f"      Establecimientos asignados a un barrio: {asignados:,}/{len(esc_ciudad):,}")


# ── 5. Contar por barrio ─────────────────────────────────────
print("\n[5/6] Contando establecimientos por barrio y sector...")

# Total
total_por_barrio = conteo_por_barrio(esc_ciudad, "escuelas_total")

# Estatal
esc_estatal = esc_ciudad[esc_ciudad["est_sector"].str.strip() == SECTOR_ESTATAL]
estatal_por_barrio = conteo_por_barrio(esc_estatal, "escuelas_estatales")

# Privado
esc_privado = esc_ciudad[esc_ciudad["est_sector"].str.strip() == SECTOR_PRIVADO]
privado_por_barrio = conteo_por_barrio(esc_privado, "escuelas_privadas")

print(f"      Barrios con escuelas (total): {len(total_por_barrio)}")
print(f"      Barrios con escuelas estatales: {len(estatal_por_barrio)}")
print(f"      Barrios con escuelas privadas: {len(privado_por_barrio)}")

# Guardar escuelas procesadas (para referencia)
esc_ciudad_export = esc_ciudad[
    ["cueanexo", "nombre", "est_sector", "est_ambito",
     "est_barrio", "est_localidad", "nivel",
     "lat", "lon", "barrio_asignado"]
].copy()
esc_ciudad_export.to_csv("data/processed/escuelas_idecor_limpio.csv", index=False, encoding="utf-8-sig")
print(f"      Archivo de referencia guardado: data/processed/escuelas_idecor_limpio.csv")


# ── 6. Integrar al dataset base v4 ───────────────────────────
print("\n[6/6] Integrando al dataset_final_v4 → dataset_final_v5...")
dataset = base.copy()

for df_join, col_name in [
    (total_por_barrio,   "escuelas_total"),
    (estatal_por_barrio, "escuelas_estatales"),
    (privado_por_barrio, "escuelas_privadas"),
]:
    if len(df_join) > 0:
        dataset = dataset.merge(df_join, on="barrio", how="left")
        dataset[col_name] = dataset[col_name].fillna(0).astype(int)
        n_con_datos = (dataset[col_name] > 0).sum()
        print(f"      ✓ {col_name:<22}: {n_con_datos:3d} barrios con datos")
    else:
        dataset[col_name] = 0
        print(f"      ✗ {col_name:<22}: sin datos")

# Reordenar columnas — mantener las de v4 + agregar las nuevas delante de la antigua
cols_v4     = list(base.columns)
cols_nuevas = ["escuelas_total", "escuelas_estatales", "escuelas_privadas"]

# Columnas finales: base v4 primero, luego las nuevas (antes de escuelas_municipales si existe)
if "escuelas_municipales" in cols_v4:
    idx_esc = cols_v4.index("escuelas_municipales")
    cols_final = cols_v4[:idx_esc] + cols_nuevas + cols_v4[idx_esc:]
else:
    cols_final = cols_v4 + cols_nuevas

# Solo incluir las que realmente existen
cols_final = [c for c in cols_final if c in dataset.columns]
dataset = dataset[cols_final]

# Guardar
output = "data/processed/dataset_final_v5.csv"
dataset.to_csv(output, index=False, encoding="utf-8-sig")

# ─────────────────────────────────────────────────────────────
# RESUMEN FINAL
# ─────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("RESUMEN FINAL")
print(f"{'='*60}")
print(f"  Dataset guardado : {output}")
print(f"  Filas            : {len(dataset)}")
print(f"  Columnas ({len(dataset.columns)})  : {list(dataset.columns)}")
print()
print("  Cobertura por variable:")
for col in ["escuelas_total", "escuelas_estatales", "escuelas_privadas",
            "escuelas_municipales", "centros_salud", "paradas_colectivo",
            "lineas_colectivo", "luminarias_reportes", "comisarias"]:
    if col in dataset.columns:
        n = (dataset[col] > 0).sum()
        pct = n / len(dataset) * 100
        bar = "█" * int(pct / 5)
        print(f"  {col:<25}: {n:3d} barrios ({pct:4.0f}%)  {bar}")

print()
print("  Top 10 barrios por total de establecimientos educativos:")
top10 = dataset.nlargest(10, "escuelas_total")[
    ["barrio", "poblacion", "pct_nbi", "escuelas_total",
     "escuelas_estatales", "escuelas_privadas"]
]
print(top10.to_string(index=False))

print(f"\n{'='*60}")
print("✅ dataset_final_v5.csv generado exitosamente")
print(f"{'='*60}")
