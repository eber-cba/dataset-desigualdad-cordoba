"""
integrador_dataset.py  — v2 (clean rewrite)
=============================================
Integra transporte (GTFS), luminarias, comisarias y centros vecinales
al dataset base de barrios de Cordoba (dataset_final_v3.csv).

Genera: data/processed/dataset_final_v4.csv
"""

import pandas as pd
import zipfile
import re
from scipy.spatial import cKDTree

# ─────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────

def normalizar(nombre):
    if pd.isna(nombre):
        return ""
    n = str(nombre).strip().upper()
    for a, b in [('A','A'),('E','E'),('I','I'),('O','O'),('U','U'),
                 ('\u00c1','A'),('\u00c9','E'),('\u00cd','I'),('\u00d3','O'),('\u00da','U'),('\u00dc','U'),
                 ('\u00d1','N'),('\u00e1','A'),('\u00e9','E'),('\u00ed','I'),('\u00f3','O'),('\u00fa','U'),('\u00f1','N')]:
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
                return float(parts[1]), float(parts[0])  # lat, lon
            except:
                pass
    return None, None

def asignar_por_centroide(df, lat_col, lon_col, centroides):
    validos = df[[lat_col, lon_col]].dropna()
    if validos.empty:
        return pd.Series([""] * len(df), index=df.index)
    tree = cKDTree(centroides[['centroide_lat','centroide_lon']].values)
    _, idx = tree.query(validos[[lat_col, lon_col]].values)
    barrios = centroides['barrio'].iloc[idx].values
    result = pd.Series([""] * len(df), index=df.index)
    result.loc[validos.index] = barrios
    return result

print("=" * 60)
print("SCRIPT: integrador_dataset.py")
print("=" * 60)

# ─────────────────────────────────────
# 1. BASE
# ─────────────────────────────────────
print("\n[1] Cargando base v3...")
base = pd.read_csv("data/processed/dataset_final_v3.csv")
barrios_set = set(base["barrio"])
print(f"    {len(base)} barrios")

# Centroides a partir de centros de salud (ya tienen lat/lon y barrio asignado)
cs = pd.read_csv("data/processed/centros_salud_limpio.csv")
centroides = (
    cs.groupby("barrio")
    .agg(centroide_lat=("latitud","mean"), centroide_lon=("longitud","mean"))
    .reset_index()
)
print(f"    {len(centroides)} centroides de barrio calculados")

# ─────────────────────────────────────
# 2. GTFS — PARADAS Y LINEAS
# ─────────────────────────────────────
print("\n[2] GTFS (paradas + lineas)...")
with zipfile.ZipFile("data/raw/gtfs_cordoba.zip") as z:
    with z.open("stops.txt") as f:
        stops = pd.read_csv(f)
    with z.open("stop_times.txt") as f:
        stop_times = pd.read_csv(f, usecols=["trip_id","stop_id"])
    with z.open("trips.txt") as f:
        trips = pd.read_csv(f, usecols=["trip_id","route_id"])
    with z.open("routes.txt") as f:
        routes = pd.read_csv(f, usecols=["route_id","route_short_name"])

print(f"    Paradas: {len(stops)} | Rutas: {len(routes)}")

stops["barrio_asignado"] = asignar_por_centroide(stops, "stop_lat", "stop_lon", centroides)

paradas_por_barrio = (
    stops[stops["barrio_asignado"] != ""]
    .groupby("barrio_asignado").size().reset_index(name="paradas_colectivo")
)
paradas_por_barrio.columns = ["barrio","paradas_colectivo"]

stop_route = stop_times.merge(trips, on="trip_id").merge(routes, on="route_id")
stop_route = stop_route.merge(stops[["stop_id","barrio_asignado"]], on="stop_id")
lineas_por_barrio = (
    stop_route[stop_route["barrio_asignado"] != ""]
    .groupby("barrio_asignado")["route_short_name"].nunique()
    .reset_index()
)
lineas_por_barrio.columns = ["barrio","lineas_colectivo"]

print(f"    Barrios con paradas: {len(paradas_por_barrio)}")
print(f"    Barrios con lineas: {len(lineas_por_barrio)}")

# Guardar paradas limpias
paradas_limpias = stops[stops["barrio_asignado"] != ""][
    ["stop_id","stop_name","stop_lat","stop_lon","barrio_asignado"]
].copy()
paradas_limpias.to_csv("data/processed/paradas_colectivo_limpio.csv", index=False)
print(f"    Paradas guardadas: {len(paradas_limpias)}")

# ─────────────────────────────────────
# 3. LUMINARIAS
# ─────────────────────────────────────
print("\n[3] Luminarias...")
lum = pd.read_csv("data/raw/luminarias_led.csv", encoding="latin1",
                  on_bad_lines="skip", low_memory=False)
# Find barrio column
barrio_col = next((c for c in lum.columns if "barrio" in c.lower() and "1" not in c), None)
if barrio_col:
    lum_barrios = lum[barrio_col].dropna().apply(normalizar)
    lum_por_barrio = lum_barrios.value_counts().reset_index()
    lum_por_barrio.columns = ["barrio","luminarias_reportes"]
    print(f"    Total registros: {len(lum)} | Barrios: {len(lum_por_barrio)}")
    match = sum(1 for b in lum_por_barrio["barrio"] if b in barrios_set)
    print(f"    Match directo con censal: {match}/{len(lum_por_barrio)}")
else:
    print("    AVISO: columna Barrio no encontrada")
    lum_por_barrio = pd.DataFrame(columns=["barrio","luminarias_reportes"])

# ─────────────────────────────────────
# 4. COMISARIAS
# ─────────────────────────────────────
print("\n[4] Comisarias...")
com = pd.read_csv("data/raw/comisarias_2023.csv", encoding="latin1", on_bad_lines="skip")
print(f"    Cols: {list(com.columns)}")

com_por_barrio = pd.DataFrame(columns=["barrio","comisarias"])

# Strategy 1: direct lat/lon columns
if "Latitud" in com.columns and "Longitud" in com.columns:
    print("    Usando columnas Latitud/Longitud directas")
    com = com.rename(columns={"Latitud":"lat","Longitud":"lon"})
    com["lat"] = pd.to_numeric(com["lat"], errors="coerce")
    com["lon"] = pd.to_numeric(com["lon"], errors="coerce")
    com_validas = com.dropna(subset=["lat","lon"]).copy()
    com_validas["barrio_asignado"] = asignar_por_centroide(com_validas, "lat", "lon", centroides)
    com_por_barrio = (
        com_validas[com_validas["barrio_asignado"] != ""]
        .groupby("barrio_asignado").size().reset_index(name="comisarias")
    )
    com_por_barrio.columns = ["barrio","comisarias"]
    print(f"    Registros: {len(com_validas)} | Barrios: {len(com_por_barrio)}")

# Strategy 2: direct Barrio column
elif "Barrio" in com.columns:
    print("    Usando columna Barrio directa")
    com["barrio_norm"] = com["Barrio"].apply(normalizar)
    com_por_barrio = (
        com[com["barrio_norm"] != ""]
        .groupby("barrio_norm").size().reset_index(name="comisarias")
    )
    com_por_barrio.columns = ["barrio","comisarias"]
    print(f"    Registros: {len(com)} | Barrios: {len(com_por_barrio)}")

# Strategy 3: WKT geometry
else:
    geo_col = None
    for col in com.columns:
        sample = str(com[col].dropna().iloc[0]) if len(com[col].dropna()) > 0 else ""
        if "POINT" in sample.upper():
            geo_col = col
            break
    if geo_col:
        com[["lat","lon"]] = com[geo_col].apply(lambda x: pd.Series(extraer_latlon_wkt(x)))
        com_validas = com.dropna(subset=["lat","lon"]).copy()
        com_validas["barrio_asignado"] = asignar_por_centroide(com_validas, "lat", "lon", centroides)
        com_por_barrio = (
            com_validas[com_validas["barrio_asignado"] != ""]
            .groupby("barrio_asignado").size().reset_index(name="comisarias")
        )
        com_por_barrio.columns = ["barrio","comisarias"]
        print(f"    Barrios: {len(com_por_barrio)}")
    else:
        print("    AVISO: sin columnas de ubicacion en comisarias")

# ─────────────────────────────────────
# 5. CENTROS VECINALES
# ─────────────────────────────────────
print("\n[5] Centros Vecinales...")
cv = pd.read_csv("data/raw/centros_vecinales.csv", encoding="latin1", on_bad_lines="skip")
print(f"    Cols: {list(cv.columns)}")

cv_por_barrio = pd.DataFrame(columns=["barrio","centros_vecinales"])

# Detect geometry column with WKT POINT
cv_geo_col = None
for col in cv.columns:
    sample = str(cv[col].dropna().iloc[0]) if len(cv[col].dropna()) > 0 else ""
    if "POINT" in sample.upper():
        cv_geo_col = col
        break

if cv_geo_col:
    print(f"    Usando WKT: {cv_geo_col}")
    cv[["lat","lon"]] = cv[cv_geo_col].apply(lambda x: pd.Series(extraer_latlon_wkt(x)))
elif any(c.lower() == "lat" for c in cv.columns):
    lat_c = next(c for c in cv.columns if c.lower() == "lat")
    lon_c = next(c for c in cv.columns if c.lower() == "lon")
    cv = cv.rename(columns={lat_c:"lat", lon_c:"lon"})
    print("    Usando lat/lon directas")
elif any("latit" in c.lower() for c in cv.columns):
    lat_c = next(c for c in cv.columns if "latit" in c.lower())
    lon_c = next(c for c in cv.columns if "longi" in c.lower())
    cv = cv.rename(columns={lat_c:"lat", lon_c:"lon"})
    print("    Usando latitude/longitude")
else:
    cv["lat"] = None
    cv["lon"] = None
    print("    AVISO: sin columnas de ubicacion")

cv_validas = cv.dropna(subset=["lat","lon"]).copy()
if len(cv_validas) > 0:
    cv_validas["barrio_asignado"] = asignar_por_centroide(cv_validas, "lat", "lon", centroides)
    cv_por_barrio = (
        cv_validas[cv_validas["barrio_asignado"] != ""]
        .groupby("barrio_asignado").size().reset_index(name="centros_vecinales")
    )
    cv_por_barrio.columns = ["barrio","centros_vecinales"]
    print(f"    Registros con coords: {len(cv_validas)} | Barrios: {len(cv_por_barrio)}")
else:
    print("    AVISO: sin coordenadas validas")

# ─────────────────────────────────────
# 6. UNIR TODO
# ─────────────────────────────────────
print("\n[6] Uniendo todos los datasets...")
dataset = base.copy()

for df_join, col_name in [
    (paradas_por_barrio,   "paradas_colectivo"),
    (lineas_por_barrio,    "lineas_colectivo"),
    (lum_por_barrio,       "luminarias_reportes"),
    (com_por_barrio,       "comisarias"),
    (cv_por_barrio,        "centros_vecinales"),
]:
    if len(df_join) > 0:
        dataset = dataset.merge(df_join, on="barrio", how="left")
        dataset[col_name] = dataset[col_name].fillna(0).astype(int)
        n = (dataset[col_name] > 0).sum()
        print(f"    OK {col_name}: {n} barrios con datos")
    else:
        dataset[col_name] = 0
        print(f"    SKIP {col_name}: sin datos")

# ─────────────────────────────────────
# 7. GUARDAR
# ─────────────────────────────────────
output = "data/processed/dataset_final_v4.csv"
dataset.to_csv(output, index=False)

print(f"\n{'='*60}")
print(f"DATASET FINAL v4 guardado: {output}")
print(f"Filas: {len(dataset)} | Columnas: {len(dataset.columns)}")
print(f"Columnas: {list(dataset.columns)}")

print("\n--- RESUMEN ---")
for col in ["escuelas_municipales","centros_salud","paradas_colectivo",
            "lineas_colectivo","luminarias_reportes","comisarias","centros_vecinales"]:
    if col in dataset.columns:
        n = (dataset[col] > 0).sum()
        print(f"  {col:<25}: {n:3d} barrios ({n/len(dataset)*100:.0f}%)")

print("\nTop 10 por servicios:")
dataset["_score"] = sum(
    (dataset[c] > 0).astype(int)
    for c in ["escuelas_municipales","centros_salud","paradas_colectivo","comisarias","centros_vecinales"]
    if c in dataset.columns
)
top10 = dataset.nlargest(10, "_score")[
    ["barrio","poblacion","pct_nbi","escuelas_municipales","centros_salud",
     "paradas_colectivo","lineas_colectivo","comisarias","centros_vecinales"]
]
print(top10.to_string(index=False))
dataset.drop(columns=["_score"]).to_csv(output, index=False)
