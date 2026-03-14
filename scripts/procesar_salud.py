"""
procesar_salud.py
=================
Procesa el dataset de Centros de Salud y Hospitales Municipales de Córdoba.

Fuente: Gobierno Abierto Córdoba
URL: https://gobiernoabierto.cordoba.gob.ar/data/datos-abiertos/categoria/geografia-y-mapas/centros-de-salud/3
Archivo raw: data/raw/centros_salud_cordoba.csv

El CSV tiene coordenadas (X=longitud, Y=latitud) y el nombre del establecimiento
que a menudo incluye el barrio: "CS N° 11 - Crisol Sur"

Estrategia de asignación de barrio:
  1. Extraer el barrio del nombre ("CS N° 11 - Crisol Sur" → "CRISOL SUR")
  2. Normalizar con el mismo diccionario de mejorar_escuelas.py
  3. Contar centros de salud por barrio
  4. Unir con dataset_final_v2.csv → generar dataset_final_v3.csv

Tipos de establecimientos incluidos:
  - Centro de Salud (atención primaria, ambulatoria)
  - Hospital (alta complejidad)
  - Hospital de Pronta Atención (urgencias mediana complejidad)
  - Dirección de Especialidades Médicas (DEM) - especialidades
  - Residencia, Banco de Sangre (no cuenta como punto de atención de salud primaria)

Decisión: para el indicador "acceso a salud" se cuentan TODOS los establecimientos
de tipo "Centro de Salud", "Hospital" y "Hospital de Pronta Atención", excluyendo
DEM, Banco de Sangre y Residencias porque no son de atención directa general.

Genera:  data/processed/dataset_final_v3.csv
         (+ columna centros_salud)
"""

import pandas as pd
import re

# ─────────────────────────────────────────────
# MAPEO DE NOMBRES (igual que mejorar_escuelas.py, extendido para salud)
# ─────────────────────────────────────────────
MAPPING_SALUD = {
    # Nombres directos que coinciden con el censal
    "GENERAL MOSCONI": "GENERAL MOSCONI",
    "LOS SAUCES": "LOS SAUCES",
    "LOS PINOS": "LOS PINOS",
    "NUEVA ITALIA": "NUEVA ITALIA",
    "YOFRE NORTE": "YOFRE NORTE",
    "VILLA RIVERA INDARTE": "VILLA RIVERA INDARTE",
    "VILLA CORNU": "VILLA CORNU",          # "Villa Cornú"
    "VILLA CORNÚ": "VILLA CORNU",
    "YAPEYU": "YAPEYU",
    "PUEYRREDON": "GENERAL PUEYRREDON",    # CS Pueyrredon → barrio General Pueyrredon
    "ACOSTA": "ACOSTA",
    "ALBERDI OESTE": "ALBERDI",
    "ALBERDI SUD": "ALBERDI",
    "ALBERDI OESTE": "ALBERDI",
    "COLONIA LOLA": "COLONIA LOLA",
    "CRISOL SUR": "CRISOL SUD",            # Sur → Sud
    "CRISOL NORTE": "CRISOL NORTE",
    "FERREYRA": "FERREYRA",
    "HIPOLITO YRIGOYEN": "HIPOLITO IRIGOYEN",   # Yrigoyen → Irigoyen
    "HIPÓLITO YRIGOYEN": "HIPOLITO IRIGOYEN",
    "GENERAL BUSTOS": "GENERAL BUSTOS",
    "REMEDIOS DE ESCALADA": "REMEDIOS DE ESCALADA",
    "ZUMARAN": "ANA MARIA ZUMARAN",
    "VILLA AZALAIZ OESTE": "VILLA AZALAIS OESTE",
    "VILLA AZALAIS OESTE": "VILLA AZALAIS OESTE",
    "VILLA AZALAIS ESTE": "VILLA AZALAIS",
    "SAN JORGE": "RESIDENCIAL SAN JORGE",
    "SARGENTO CABRAL": "SARGENTO CABRAL",
    "LAS MARGARITAS": "LAS MARGARITAS",
    "MARQUÉS DE SOBREMONTE": "MARQUES DE SOBREMONTE",
    "MARQUES DE SOBREMONTE": "MARQUES DE SOBREMONTE",
    "MARQUÉS DE SOBREMONTE ANEXO": "MARQUES ANEXO",
    "MARQUES DE SOBREMONTE ANEXO": "MARQUES ANEXO",
    "SANTA ANA": "QUINTA SANTA ANA",       # CS Santa Ana → Quinta Santa Ana
    "PILAR": "JARDIN DEL PILAR",
    "LAS VIOLETAS": "LAS VIOLETAS",
    "VILLA SIBURU": "VILLA SIBURU",
    "VILLA PAEZ": "VILLA PAEZ",
    "LA SALLE": "LA SALLE",
    "VILLA 9 DE JULIO": "VILLA 9 DE JULIO",
    "ARGÜELLO": "ARGUELLO",
    "ARGUELLO": "ARGUELLO",
    "ARGUELLO I.P.V": "ARGUELLO",
    "VILLA REVOL": "VILLA REVOL",
    "JOSE IGNACIO DIAZ": "JOSE IGNACIO DIAZ SECCION 1",
    "JOSE IGNACIO DIAZ 1 SECC": "JOSE IGNACIO DIAZ SECCION 1",
    "JOSE IGNACIO DIAZ 1": "JOSE IGNACIO DIAZ SECCION 1",
    "URQUIZA": "URQUIZA",
    "VILLA URQUIZA": "URQUIZA",
    "FERRER": "FERRER",
    "LAS FLORES": "LAS FLORES",
    "VILLA EL LIBERTADOR": "VILLA EL LIBERTADOR",
    "COMERCIAL": "COMERCIAL",
    "GUEMES": "GUEMES",
    "GÜEMES": "GUEMES",
    "BELLA VISTA": "BELLA VISTA",
    "CABO FARINA": "CABO FARINA",
    "SANTA ISABEL": "SANTA ISABEL SECCION 1",
    "CORONEL OLMEDO": "VILLA CORONEL OLMEDO",
    "COLINAS DEL CERRO": "COLINAS DEL CERRO",
    "VILLA ADELA": "VILLA ADELA",
    "GUIÑAZU": "GUINAZU",
    "GUINAZU": "GUINAZU",
    "INAUDI": "INAUDI",
    "LOS BOULEVARES": "LOS BOULEVARES",
    "LAS PALMAS": "LAS PALMAS",
    "EMPALME": "EMPALME",
    "MALDONADO": "MALDONADO",
    "CONGRESO": "CONGRESO",
    "AMEGHINO NORTE": "AMEGHINO NORTE",
    "BAJO GRANDE": "BAJO GENERAL PAZ",
    "PATRICIOS ESTE": "PATRICIOS ESTE",
    "VILLA ALLENDE PARQUE": "VILLA ALLENDE PARQUE",
    "RENACIMIENTO": "RENACIMIENTO",
    "SAN LORENZO": "SAN LORENZO",
    "GENERAL ARENALES": "GENERAL ARENALES",
    "ESTACION FLORES": "ESTACION FLORES",
    "COOPERATIVA EL ARCO": "COOPERATIVA EL FUTURO",  # aprox.
    "LA FLORESTA": "LA FLORESTA",
    "PARQUE FUTURA": "PARQUE FUTURA",
    "VILLA ESQUIÚ": "VILLA ESQUIU",
    "VILLA ESQUIU": "VILLA ESQUIU",
    "CERVECEROS": "CERVECEROS",
    "VILLA UNIÓN": "VILLA UNION",
    "VILLA UNION": "VILLA UNION",
    "DON BOSCO": "PARQUE DON BOSCO",
    "PARQUE LICEO II SECC.": "PARQUE LICEO SECCION 2",
    "PARQUE LICEO II SECC": "PARQUE LICEO SECCION 2",
    "ALBERT SABIN": "VILLA RIVADAVIA",     # CS en zona sur, aprox.
    "VILLA RIVADAVIA": "VILLA RIVADAVIA",
    "ITUZAINGO ANEXO": "ITUZAINGO ANEXO",
    "VILLA BUSTOS": "VILLA BUSTOS",
    "LOS CORTADEROS": "LAS CORTADERAS",
    "VILLA LA TELA": "LAS PALMAS",         # zona Las Palmas
    "PARQUE LICEO III SECC.": "PARQUE LICEO SECCION 3",
    "PARQUE LICEO III SECC": "PARQUE LICEO SECCION 3",
    "CAMINO A 60 CUADRAS": "BH_CAMINO A 60 CUADRAS",
    "JOSE IGNACIO DIAZ 1 SECC": "JOSE IGNACIO DIAZ SECCION 1",
    "CABILDO": "EL CABILDO",
    "MERCADO DE ABASTO": "CENTRO",
    "LOS ROBLES": "LOS ROBLES",
    "HÉROES DE MALVINAS": "VILLA EL LIBERTADOR",  # zona Villa El Libertador
    "HEROES DE MALVINAS": "VILLA EL LIBERTADOR",
    "12 DE JULIO": "ARGUELLO",             # zona Argüello
    "VILLA CORNÚ": "VILLA CORNU",
    "PARQUE REPÚBLICA": "PARQUE REPUBLICA",
    "PARQUE REPUBLICA": "PARQUE REPUBLICA",
    "OÑA / BIALET MASSÉ": "BIALET MASSE",
    "ONA / BIALET MASSE": "BIALET MASSE",
    "SAN ROQUE": "RESIDENCIAL SAN ROQUE",
    "MERCANTIL ANEXO": "MERCANTIL",
    "16 DE NOVIEMBRE": "COOPERATIVA 16 DE NOVIEMBRE",
    "CARCANO": "RAMON J CARCANO",
    "ROSEDAL ANEXO": "ROSEDAL ANEXO",
    "CUPANI": "CUPANI",
    "SAN MARTÍN": "SAN MARTIN",
    "SAN MARTIN": "SAN MARTIN",
    "CENTRO": "CENTRO",
}

# Tipos que se incluyen como "centros de salud"
TIPOS_SALUD = {
    "Centro de Salud",
    "Hospital",
    "Hospital de Pronta Atención",
}


def extraer_barrio_de_nombre(nombre_cs: str) -> str:
    """
    Extrae el nombre del barrio desde el nombre del centro de salud.
    Formato típico: "CS N° 11 - Crisol Sur" → "CRISOL SUR"
    También: "Hospital Municipal de Urgencias" → se ignora (sin barrio en nombre)
    """
    if pd.isna(nombre_cs):
        return ""

    n = str(nombre_cs).strip()

    # Patrón: "CS N° XX - NOMBRE" o "CS NXX - NOMBRE" o "CSN° XX - NOMBRE"
    patron = re.search(r"CS\s*N[°º]?\s*\d+\s*[-–]\s*(.+)$", n, re.IGNORECASE)
    if patron:
        return patron.group(1).strip().upper()

    # Si no tiene el patrón estándar, devolver vacío (hospitales, DEM, etc.)
    return ""


def normalizar_barrio_salud(nombre: str) -> str:
    """Normaliza el nombre del barrio extraído del centro de salud."""
    if not nombre:
        return ""

    n = nombre.strip().upper()

    # Buscar en el mapping
    if n in MAPPING_SALUD:
        return MAPPING_SALUD[n]

    # Intentar algunas normalizaciones automáticas
    n = n.replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")
    n = n.replace("Ñ", "N")

    if n in MAPPING_SALUD:
        return MAPPING_SALUD[n]

    return n


# ─────────────────────────────────────────────
# PROCESAMIENTO PRINCIPAL
# ─────────────────────────────────────────────
print("=" * 60)
print("SCRIPT: procesar_salud.py")
print("Objetivo: agregar centros de salud al dataset final")
print("=" * 60)

# 1. Cargar centros de salud
salud_raw = pd.read_csv(
    "data/raw/centros_salud_cordoba.csv",
    usecols=["X", "Y", "Name", "tipo"],
    on_bad_lines="skip",
)
salud_raw.columns = ["longitud", "latitud", "nombre", "tipo"]
salud_raw = salud_raw.dropna(subset=["nombre"])
salud_raw["nombre"] = salud_raw["nombre"].str.strip()
salud_raw["tipo"] = salud_raw["tipo"].str.strip().fillna("")

print(f"\n[Raw] Total establecimentos leídos: {len(salud_raw)}")
print(f"[Raw] Tipos únicos:")
for t, c in salud_raw["tipo"].value_counts().items():
    print(f"  {t!r}: {c}")

# 2. Filtrar solo los tipos que cuentan para el indicador de salud
salud_filtrado = salud_raw[salud_raw["tipo"].isin(TIPOS_SALUD)].copy()
print(f"\n[Filtrado] Establecimientos de salud directa: {len(salud_filtrado)}")

# 3. Extraer el barrio del nombre
salud_filtrado["barrio_original"] = salud_filtrado["nombre"].apply(extraer_barrio_de_nombre)
salud_filtrado["barrio_normalizado"] = salud_filtrado["barrio_original"].apply(normalizar_barrio_salud)

# Mostrar el mapeo
print("\n[Mapeo de barrios]")
print(f"{'NOMBRE CS':<50} {'BARRIO EXTRAÍDO':<30} {'BARRIO NORMALIZADO'}")
print("-" * 110)
for _, r in salud_filtrado.iterrows():
    print(f"{str(r['nombre'])[:49]:<50} {str(r['barrio_original']):<30} {r['barrio_normalizado']}")

# 4. Separar los que tienen barrio asignado vs los que no
con_barrio = salud_filtrado[salud_filtrado["barrio_normalizado"] != ""]
sin_barrio_cs = salud_filtrado[salud_filtrado["barrio_normalizado"] == ""]

print(f"\n[Resultado] Con barrio asignado: {len(con_barrio)}")
print(f"[Resultado] Sin barrio (hospitales/DEM sin barrio en nombre): {len(sin_barrio_cs)}")
if len(sin_barrio_cs) > 0:
    print("  Sin barrio:")
    for _, r in sin_barrio_cs.iterrows():
        print(f"    - {r['nombre']} (tipo: {r['tipo']})")

# 5. Agrupar por barrio
centros_por_barrio = (
    con_barrio.groupby("barrio_normalizado")
    .size()
    .reset_index(name="centros_salud")
)
centros_por_barrio.columns = ["barrio", "centros_salud"]

print(f"\n[Agrupado] Barrios con ≥1 centro de salud: {len(centros_por_barrio)}")

# 6. Verificar coincidencia con censal
censal = pd.read_csv("data/processed/dataset_final_v2.csv")
censal_set = set(censal["barrio"])

sin_match = [b for b in centros_por_barrio["barrio"] if b not in censal_set]
con_match = [b for b in centros_por_barrio["barrio"] if b in censal_set]

print(f"[Verificación] ✅ Con match en censal: {len(con_match)}")
print(f"[Verificación] ❌ Sin match (revisar): {len(sin_match)}")
if sin_match:
    print("  Sin match:", sin_match)

# 7. Unir con dataset v2
dataset_v3 = censal.merge(centros_por_barrio, on="barrio", how="left")
dataset_v3["centros_salud"] = dataset_v3["centros_salud"].fillna(0).astype(int)

total = len(dataset_v3)
con_cs = (dataset_v3["centros_salud"] > 0).sum()
print(f"\n[Dataset v3] Total barrios: {total}")
print(f"[Dataset v3] Barrios con ≥1 centro de salud: {con_cs}")
print(f"[Dataset v3] Barrios sin centro de salud registrado: {total - con_cs}")
print(f"[Dataset v3] Columnas: {list(dataset_v3.columns)}")

# 8. Guardar
output_path = "data/processed/dataset_final_v3.csv"
dataset_v3.to_csv(output_path, index=False)
print(f"\n✅ Dataset guardado en: {output_path}")

# 9. Muestra de barrios con centros de salud
print("\n[Barrios con centros de salud]:")
print(
    dataset_v3[dataset_v3["centros_salud"] > 0][
        ["barrio", "poblacion", "pct_nbi", "escuelas_municipales", "centros_salud"]
    ].sort_values("centros_salud", ascending=False).to_string(index=False)
)

# 10. Guardar también los datos limpios de centros de salud como referencia
salud_limpio = con_barrio[["nombre", "tipo", "barrio_normalizado", "longitud", "latitud"]].copy()
salud_limpio.columns = ["nombre", "tipo", "barrio", "longitud", "latitud"]
salud_limpio.to_csv("data/processed/centros_salud_limpio.csv", index=False)
print(f"\n✅ Centros de salud limpios guardados en: data/processed/centros_salud_limpio.csv")
