"""
regenerar_dataset_v6.py
========================
Re-integra TODOS los datasets usando los centroides del CSV censal original
(560 barrios con coordenadas X/Y), reemplazando los solo 91 centroides usados
anteriormente (derivados de centros de salud).

Esto mejora la cobertura de asignación espacial de ~18% a ~100%.

Genera: data/processed/centroides_barrios_completo.csv  (referencia)
        data/processed/dataset_final_v6.csv              (versión final mejorada)

Autor  : Eber Coronel — DiploDatos 2026
Versión: 1.0 — 2026-03-14
"""

import pandas as pd
import zipfile
import re
from scipy.spatial import cKDTree

# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────
BBOX_LAT = (-31.55, -31.20)
BBOX_LON = (-64.35, -64.00)

# ─────────────────────────────────────────────────────────────
# UTILIDADES (idénticas a integrador_dataset.py)
# ─────────────────────────────────────────────────────────────

def normalizar(nombre):
    if pd.isna(nombre):
        return ""
    n = str(nombre).strip().upper()
    for a, b in [('Á','A'),('É','E'),('Í','I'),('Ó','O'),('Ú','U'),('Ü','U'),('Ñ','N'),
                 ('á','A'),('é','E'),('í','I'),('ó','O'),('ú','U'),('ñ','N')]:
        n = n.replace(a, b)
    return n

def extraer_latlon_wkt(wkt_str):
    if pd.isna(wkt_str):
        return None, None
    m = re.search(r'POINT\s*\(([^)]+)\)', str(wkt_str))
    if m:
        parts = m.group(1).strip().split()
        if len(parts) >= 2:
            try:
                return float(parts[1]), float(parts[0])
            except:
                pass
    return None, None

def asignar_por_centroide(df, lat_col, lon_col, centroides):
    validos = df[[lat_col, lon_col]].dropna()
    result = pd.Series([""] * len(df), index=df.index)
    if validos.empty:
        return result
    tree = cKDTree(centroides[['centroide_lat', 'centroide_lon']].values)
    _, idx = tree.query(validos[[lat_col, lon_col]].values)
    result.loc[validos.index] = centroides['barrio'].iloc[idx].values
    return result

def conteo_por_barrio(df, col_nombre):
    return (
        df[df["barrio_asignado"] != ""]
        .groupby("barrio_asignado").size()
        .reset_index(name=col_nombre)
        .rename(columns={"barrio_asignado": "barrio"})
    )

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
import os

print("=" * 65)
print("SCRIPT: regenerar_dataset_v6.py")
print("Objetivo: integrar TODOS los datasets con 560 centroides del censal")
print("=" * 65)

# ── 1. Cargar CSV censal original (tiene X, Y por barrio) ────
print("\n[1/9] Extrayendo centroides del CSV censal original...")
censal_raw = pd.read_csv(
    "data/raw/Barrios_de_Córdoba_con_información_censal_afkGL16.csv",
    encoding="latin-1", on_bad_lines="skip"
)
print(f"      Columnas: {list(censal_raw.columns)}")

# Identificar columnas de coordenadas
x_col = next((c for c in censal_raw.columns if c.upper() in ("X", "LON", "LONGITUD")), None)
y_col = next((c for c in censal_raw.columns if c.upper() in ("Y", "LAT", "LATITUD")), None)
# Nombre de barrio en el raw — probar variantes
nombre_col = next((c for c in censal_raw.columns if c.upper() in ("NOMBRE_BAR", "BARRIO", "NOMBRE")), None)

print(f"      Columna X: {x_col} | Y: {y_col} | Nombre: {nombre_col}")

# Construir tabla de centroides
censal_raw[x_col] = pd.to_numeric(censal_raw[x_col], errors="coerce")
censal_raw[y_col] = pd.to_numeric(censal_raw[y_col], errors="coerce")
censal_raw["barrio_norm"] = censal_raw[nombre_col].apply(normalizar)

# Agrupar por barrio normalizado (puede haber varios puntos por barrio)
centroides_full = (
    censal_raw.dropna(subset=[x_col, y_col])
    .groupby("barrio_norm")
    .agg(centroide_lat=(y_col, "mean"), centroide_lon=(x_col, "mean"))
    .reset_index()
    .rename(columns={"barrio_norm": "barrio"})
)

# También agregar los centroides de centros de salud (complemento)
cs = pd.read_csv("data/processed/centros_salud_limpio.csv")
centroides_salud = (
    cs.groupby("barrio")
    .agg(centroide_lat=("latitud", "mean"), centroide_lon=("longitud", "mean"))
    .reset_index()
)
centroides_salud["barrio"] = centroides_salud["barrio"].apply(normalizar)

# Fusionar: priorizar los del censal, complementar con los de salud
barrios_ya_cubiertos = set(centroides_full["barrio"])
centroides_extra = centroides_salud[~centroides_salud["barrio"].isin(barrios_ya_cubiertos)]
centroides = pd.concat([centroides_full, centroides_extra], ignore_index=True)

print(f"      Centroides del censal        : {len(centroides_full)}")
print(f"      Centroides extra (salud)     : {len(centroides_extra)}")
print(f"      Total centroides disponibles : {len(centroides)}")

# Guardar centroides como referencia
centroides.to_csv("data/processed/centroides_barrios_completo.csv", index=False)
print(f"      → Guardado: data/processed/centroides_barrios_completo.csv")

# ── 2. Cargar base v2 (censal + escuelas municipales + pct_nbi) ──
print("\n[2/9] Cargando base censal...")
base = pd.read_csv("data/processed/barrios_cordoba_censal_limpio.csv")
# Normalizar columna barrio para los joins
base["barrio_norm"] = base["barrio"].apply(normalizar)
barrios_set = set(base["barrio_norm"])
print(f"      {len(base)} barrios | cols: {list(base.columns)}")

# Función de asignación con barrio normalizado del censal
def asignar_centroide_norm(df, lat_col, lon_col):
    """Asigna por KD-tree usando los centroides completos, retorna barrio NORMALIZADO."""
    validos = df[[lat_col, lon_col]].dropna()
    result = pd.Series([""] * len(df), index=df.index)
    if validos.empty:
        return result
    tree = cKDTree(centroides[['centroide_lat', 'centroide_lon']].values)
    _, idx = tree.query(validos[[lat_col, lon_col]].values)
    result.loc[validos.index] = centroides['barrio'].iloc[idx].values
    return result

# ── 3. CENTROS DE SALUD ──────────────────────────────────────
print("\n[3/9] Re-asignando centros de salud...")
cs_limpio = pd.read_csv("data/processed/centros_salud_limpio.csv")
cs_limpio["barrio_asignado"] = asignar_centroide_norm(cs_limpio, "latitud", "longitud")
cs_por_barrio = conteo_por_barrio(cs_limpio, "centros_salud")
cs_por_barrio["barrio"] = cs_por_barrio["barrio"]  # ya normalizado
n_cs = len(cs_por_barrio)
print(f"      Barrios con centros de salud: {n_cs}")

# ── 4. GTFS — PARADAS Y LINEAS ───────────────────────────────
print("\n[4/9] Re-asignando transporte GTFS...")
with zipfile.ZipFile("data/raw/gtfs_cordoba.zip") as z:
    with z.open("stops.txt") as f:
        stops = pd.read_csv(f)
    with z.open("stop_times.txt") as f:
        stop_times = pd.read_csv(f, usecols=["trip_id", "stop_id"])
    with z.open("trips.txt") as f:
        trips = pd.read_csv(f, usecols=["trip_id", "route_id"])
    with z.open("routes.txt") as f:
        routes = pd.read_csv(f, usecols=["route_id", "route_short_name"])

stops["barrio_asignado"] = asignar_centroide_norm(stops, "stop_lat", "stop_lon")
paradas_por_barrio = conteo_por_barrio(stops, "paradas_colectivo")

stop_route = stop_times.merge(trips, on="trip_id").merge(routes, on="route_id")
stop_route = stop_route.merge(stops[["stop_id", "barrio_asignado"]], on="stop_id")
lineas_por_barrio = (
    stop_route[stop_route["barrio_asignado"] != ""]
    .groupby("barrio_asignado")["route_short_name"].nunique()
    .reset_index()
)
lineas_por_barrio.columns = ["barrio", "lineas_colectivo"]

print(f"      Barrios con paradas: {len(paradas_por_barrio)}")
print(f"      Barrios con líneas : {len(lineas_por_barrio)}")

# Guardar paradas procesadas
stops_export = stops[stops["barrio_asignado"] != ""][
    ["stop_id", "stop_name", "stop_lat", "stop_lon", "barrio_asignado"]
].copy()
stops_export.to_csv("data/processed/paradas_colectivo_limpio.csv", index=False)

# ── 5. LUMINARIAS ────────────────────────────────────────────
print("\n[5/9] Re-asignando luminarias...")
lum = pd.read_csv("data/raw/luminarias_led.csv", encoding="latin1",
                  on_bad_lines="skip", low_memory=False)
barrio_col = next((c for c in lum.columns if "barrio" in c.lower() and "1" not in c), None)
if barrio_col:
    lum_barrios = lum[barrio_col].dropna().apply(normalizar)
    lum_por_barrio = lum_barrios.value_counts().reset_index()
    lum_por_barrio.columns = ["barrio", "luminarias_reportes"]
    print(f"      Total registros: {len(lum)} | Barrios: {len(lum_por_barrio)}")
else:
    lum_por_barrio = pd.DataFrame(columns=["barrio", "luminarias_reportes"])
    print("      AVISO: columna Barrio no encontrada")

# ── 6. COMISARIAS ────────────────────────────────────────────
print("\n[6/9] Re-asignando comisarías...")
com = pd.read_csv("data/raw/comisarias_2023.csv", encoding="latin1", on_bad_lines="skip")
com_por_barrio = pd.DataFrame(columns=["barrio", "comisarias"])

if "Latitud" in com.columns and "Longitud" in com.columns:
    com = com.rename(columns={"Latitud": "lat", "Longitud": "lon"})
    com["lat"] = pd.to_numeric(com["lat"], errors="coerce")
    com["lon"] = pd.to_numeric(com["lon"], errors="coerce")
    com_validas = com.dropna(subset=["lat", "lon"]).copy()
    com_validas["barrio_asignado"] = asignar_centroide_norm(com_validas, "lat", "lon")
    com_por_barrio = conteo_por_barrio(com_validas, "comisarias")
    print(f"      Comisarías asignadas: {len(com_validas)} | Barrios: {len(com_por_barrio)}")
else:
    # Buscar columna WKT
    geo_col = None
    for col in com.columns:
        sample = str(com[col].dropna().iloc[0]) if len(com[col].dropna()) > 0 else ""
        if "POINT" in sample.upper():
            geo_col = col
            break
    if geo_col:
        com[["lat", "lon"]] = com[geo_col].apply(lambda x: pd.Series(extraer_latlon_wkt(x)))
        com_validas = com.dropna(subset=["lat", "lon"]).copy()
        com_validas["barrio_asignado"] = asignar_centroide_norm(com_validas, "lat", "lon")
        com_por_barrio = conteo_por_barrio(com_validas, "comisarias")
        print(f"      Barrios con comisarías: {len(com_por_barrio)}")

# ── 7. ESCUELAS IDECOR ───────────────────────────────────────
print("\n[7/9] Re-asignando establecimientos educativos IDECOR...")
esc = pd.read_csv("data/raw/escuelas_cordoba.csv")
esc["lat"] = pd.to_numeric(esc["lat"], errors="coerce")
esc["lon"] = pd.to_numeric(esc["lon"], errors="coerce")

# Filtrar a ciudad de Córdoba Capital
if "est_departamento" in esc.columns:
    esc_capital = esc[esc["est_departamento"].str.strip().str.lower() == "capital"].copy()
else:
    esc_capital = esc.copy()

esc_ciudad = esc_capital[
    esc_capital["lat"].between(*BBOX_LAT) &
    esc_capital["lon"].between(*BBOX_LON)
].copy()
print(f"      Establecimientos en la ciudad: {len(esc_ciudad):,}")

esc_ciudad["barrio_asignado"] = asignar_centroide_norm(esc_ciudad, "lat", "lon")

total_por_barrio   = conteo_por_barrio(esc_ciudad, "escuelas_total")
esc_estatal = esc_ciudad[esc_ciudad["est_sector"].str.strip() == "Estatal"]
estatal_por_barrio = conteo_por_barrio(esc_estatal, "escuelas_estatales")
esc_privado = esc_ciudad[esc_ciudad["est_sector"].str.strip() == "Privado"]
privado_por_barrio = conteo_por_barrio(esc_privado, "escuelas_privadas")

# Guardar escuelas procesadas con centroides completos
esc_ciudad_exp = esc_ciudad[[
    "cueanexo", "nombre", "est_sector", "est_ambito",
    "est_barrio", "est_localidad", "nivel", "lat", "lon", "barrio_asignado"
]].copy()
esc_ciudad_exp.to_csv("data/processed/escuelas_idecor_limpio.csv", index=False, encoding="utf-8-sig")

print(f"      Barrios con escuelas (total)    : {len(total_por_barrio)}")
print(f"      Barrios con escuelas estatales  : {len(estatal_por_barrio)}")
print(f"      Barrios con escuelas privadas   : {len(privado_por_barrio)}")

# ── 8. CENTROS VECINALES ──────────────────────────────────
print("\n[8/9] Re-asignando centros vecinales...")
cv_path = "data/raw/centros_vecinales.csv"
cv_por_barrio = pd.DataFrame(columns=["barrio", "centros_vecinales"])
if os.path.exists(cv_path):
    cv = pd.read_csv(cv_path, low_memory=False)
    cv["centroid_lat"] = pd.to_numeric(cv["centroid_lat"], errors="coerce")
    cv["centroid_lon"] = pd.to_numeric(cv["centroid_lon"], errors="coerce")
    cv = cv.dropna(subset=["centroid_lat", "centroid_lon"])
    cv_ciudad = cv[
        cv["centroid_lat"].between(*BBOX_LAT) &
        cv["centroid_lon"].between(*BBOX_LON)
    ].copy()
    cv_ciudad["barrio_asignado"] = asignar_centroide_norm(cv_ciudad, "centroid_lat", "centroid_lon")
    cv_por_barrio = conteo_por_barrio(cv_ciudad, "centros_vecinales")
    # Guardar procesado
    cv_export = cv_ciudad[["centroid_lat", "centroid_lon", "label", "CPC", "DIRECCION", "barrio_asignado"]].copy()
    cv_export.to_csv("data/processed/centros_vecinales_limpio.csv", index=False, encoding="utf-8-sig")
    print(f"      Centros vecinales en ciudad: {len(cv_ciudad)} | Barrios: {len(cv_por_barrio)}")
else:
    print("      AVISO: data/raw/centros_vecinales.csv no encontrado — columna en 0")

# ── 9. UNIR TODO ─────────────────────────────────────────────
print("\n[9/9] Uniendo todos los datasets en v6...")
dataset = base.copy()

# Asegurar tipos numéricos
for col in ["poblacion", "hogares", "nbi"]:
    if col in dataset.columns:
        dataset[col] = pd.to_numeric(dataset[col], errors="coerce").fillna(0).astype(int)

# Filtrar barrios con nombre vacío
dataset = dataset[dataset["barrio"].str.strip().str.len() > 0].copy()
print(f"  Barrios válidos: {len(dataset)}")

# Calcular pct_nbi (evitar inf cuando hogares=0)
dataset["pct_nbi"] = 0.0
mask = dataset["hogares"] > 0
dataset.loc[mask, "pct_nbi"] = (dataset.loc[mask, "nbi"] / dataset.loc[mask, "hogares"] * 100).round(2)

# Escuelas municipales (de CSV raw, 38 establecimientos)
esc_muni_path = "data/raw/ZONAS_ESCUELAS_MUNICIPALES_Corregido_2.csv"
if os.path.exists(esc_muni_path):
    esc_muni = pd.read_csv(esc_muni_path)
    barrio_col_muni = next((c for c in esc_muni.columns if "barrio" in c.lower()), None)
    if barrio_col_muni:
        esc_muni["barrio_norm"] = esc_muni[barrio_col_muni].apply(normalizar)
        muni_por_barrio = esc_muni.groupby("barrio_norm").size().reset_index(name="escuelas_municipales")
        dataset["barrio_norm_tmp"] = dataset["barrio"].apply(normalizar)
        dataset = dataset.merge(muni_por_barrio, left_on="barrio_norm_tmp", right_on="barrio_norm", how="left")
        dataset["escuelas_municipales"] = dataset["escuelas_municipales"].fillna(0).astype(int)
        dataset = dataset.drop(columns=["barrio_norm", "barrio_norm_tmp"], errors="ignore")
        print(f"  ✓ escuelas_municipales       : {(dataset['escuelas_municipales'] > 0).sum():3d} barrios con datos")
    else:
        dataset["escuelas_municipales"] = 0
else:
    dataset["escuelas_municipales"] = 0

# Normalizar barrio en el dataset base para el join
dataset["barrio_norm"] = dataset["barrio"].apply(normalizar)

joins = [
    (cs_por_barrio,       "centros_salud"),
    (paradas_por_barrio,  "paradas_colectivo"),
    (lineas_por_barrio,   "lineas_colectivo"),
    (lum_por_barrio,      "luminarias_reportes"),
    (com_por_barrio,      "comisarias"),
    (total_por_barrio,    "escuelas_total"),
    (estatal_por_barrio,  "escuelas_estatales"),
    (privado_por_barrio,  "escuelas_privadas"),
    (cv_por_barrio,       "centros_vecinales"),
]

for df_join, col_name in joins:
    if len(df_join) > 0:
        # Normalizar el barrio de la tabla join
        df_join = df_join.copy()
        df_join["barrio"] = df_join["barrio"].apply(normalizar)
        dataset = dataset.merge(
            df_join.rename(columns={"barrio": "barrio_norm"}),
            on="barrio_norm", how="left"
        )
        dataset[col_name] = dataset[col_name].fillna(0).astype(int)
        n = (dataset[col_name] > 0).sum()
        print(f"  ✓ {col_name:<25}: {n:3d} barrios con datos")
    else:
        dataset[col_name] = 0
        print(f"  ✗ {col_name:<25}: sin datos")


# Eliminar columna auxiliar
dataset = dataset.drop(columns=["barrio_norm"], errors="ignore")

# Reordenar columnas en el orden lógico
cols_orden = [
    "barrio", "poblacion", "hogares", "nbi", "pct_nbi",
    "escuelas_municipales",
    "escuelas_total", "escuelas_estatales", "escuelas_privadas",
    "centros_salud", "paradas_colectivo", "lineas_colectivo",
    "luminarias_reportes", "comisarias", "centros_vecinales",
]
cols_final = [c for c in cols_orden if c in dataset.columns]
dataset = dataset[cols_final]

# Guardar
output = "data/processed/dataset_final_v6.csv"
dataset.to_csv(output, index=False, encoding="utf-8-sig")

# ─────────────────────────────────────────────────────────────
# RESUMEN
# ─────────────────────────────────────────────────────────────
print(f"\n{'='*65}")
print("RESUMEN COBERTURA")
print(f"{'='*65}")
print(f"  {'Variable':<28} {'Barrios con datos':>18}")
print(f"  {'-'*48}")

for col in ["centros_salud", "paradas_colectivo", "lineas_colectivo",
            "luminarias_reportes", "comisarias", "escuelas_total",
            "escuelas_estatales", "escuelas_privadas", "centros_vecinales"]:
    if col in dataset.columns:
        n = (dataset[col] > 0).sum()
        print(f"  {col:<28} {n:>5} / {len(dataset)}")

print(f"\n✅ dataset_final_v6.csv guardado: {output}")
print(f"   Filas: {len(dataset)} | Columnas: {len(dataset.columns)}: {list(dataset.columns)}")

