"""
mejorar_escuelas.py
=====================
Soluciona el problema de matching entre los nombres de barrio
en el dataset de escuelas y el dataset censal.

Problemas detectados:
  - Abreviaturas: "Vª" → "VILLA", "STA" → "SANTA", "STO" → "SARGENTO" etc.
  - Nombres truncados: "QTAS DE ARGUELLO" → "QUINTAS DE ARGUELLO"
  - Secciones: "JOSE I. DIAZ III" → "JOSE IGNACIO DIAZ SECCION 3"
  - Sin match directo: "SAN JORGE I", "SAN JORGE II" → agregar a "RESIDENCIAL SAN JORGE"
  - "LICEO" → "PARQUE LICEO SECCION 1" (en zona del barrio Liceo)
  - "SAN CARLOS" → "RESIDENCIAL SAN CARLOS"
  - "SAN ROQUE" → "RESIDENCIAL SAN ROQUE"
  - "ARENALES" → "GENERAL ARENALES"
  - "URQUIZA" ya existe exacto en censal
  - "STA ISABEL" → "SANTA ISABEL SECCION 1" (la escuela está en la sección 1)

Proceso:
  1. Carga raw dataset de escuelas municipales
  2. Extrae el nombre del barrio de la columna ESTABLECIMIENTO
  3. Aplica mappings manuales + normalización de abreviaturas
  4. Agrupa escuelas por barrio normalizado
  5. Une con dataset censal
  6. Guarda el resultado final
  7. Genera reporte de cobertura
"""

import pandas as pd
import re

# ─────────────────────────────────────────────
# 1. MAPPINGS MANUALES (nombre en escuelas → nombre exacto en censal)
# ─────────────────────────────────────────────
MAPPING_MANUAL = {
    # Abreviaturas de VILLA
    "VILLA AZALAIS": "VILLA AZALAIS",
    "VILLA ALLENDE PARQUE": "VILLA ALLENDE PARQUE",
    "VILLA EL LIBERTADOR": "VILLA EL LIBERTADOR",
    "VILLA CORNU": "VILLA CORNU",
    "VILLA RIVERA INDARTE": "VILLA RIVERA INDARTE",
    "VILLA SIBURU": "VILLA SIBURU",
    "VILLA 9 DE JULIO": "VILLA 9 DE JULIO",
    "VILLA URQUIZA": "URQUIZA",  # En censal es solo URQUIZA

    # Abreviaturas de SANTA / SARGENTO
    "SANTA CECILIA": "SANTA CECILIA",
    "SANTA ISABEL": "SANTA ISABEL SECCION 1",  # La escuela está en sección 1
    "SARGENTO CABRAL": "SARGENTO CABRAL",

    # Secciones Jose Ignacio Diaz
    "JOSE IGNACIO DIAZ III": "JOSE IGNACIO DIAZ SECCION 3",
    "JOSE IGNACIO DIAZ IV": "JOSE IGNACIO DIAZ SECCION 2",  # Sección 4 no existe, aprox. a 2
    "JOSE IGNACIO DIAZ V": "JOSE IGNACIO DIAZ SECCION 1",   # Sección 5 no existe, aprox. a 1

    # Nombre abreviado o diferente
    "QTAS DE ARGUELLO": "QUINTAS DE ARGUELLO",
    "ARENALES": "GENERAL ARENALES",
    "LICEO": "PARQUE LICEO SECCION 1",
    "SAN CARLOS": "RESIDENCIAL SAN CARLOS",
    "SAN ROQUE": "RESIDENCIAL SAN ROQUE",
    "SAN JORGE I": "RESIDENCIAL SAN JORGE",
    "SAN JORGE II": "RESIDENCIAL SAN JORGE",

    # Ya coinciden exacto (no necesitan mapping pero las documentamos)
    "CENTRO AMERICA": "CENTRO AMERICA",
    "COLONIA LOLA": "COLONIA LOLA",
    "COMERCIAL": "COMERCIAL",
    "CONGRESO": "CONGRESO",
    "JOSE HERNANDEZ": "JOSE HERNANDEZ",
    "LAS PALMAS": "LAS PALMAS",
    "LOS BOULEVARES": "LOS BOULEVARES",
    "LOS PLATANOS": "LOS PLATANOS",
    "LOS SAUCES": "LOS SAUCES",
    "MERCANTIL": "MERCANTIL",
    "PARQUE DEL ESTE": "PARQUE DEL ESTE",
    "PATRICIOS": "PATRICIOS",
    "RENACIMIENTO": "RENACIMIENTO",
    "ROSEDAL": "ROSEDAL",
    "SACHI": "SACHI",
}


def normalizar_nombre_barrio(nombre: str) -> str:
    """
    Convierte un nombre de barrio del dataset de escuelas
    al formato usado en el dataset censal.
    """
    if pd.isna(nombre):
        return ""
    
    n = nombre.strip().upper()
    
    # Paso 1: reemplazar abreviaturas comunes
    reemplazos = [
        (r"^Vª\s*", "VILLA "),
        (r"^V\.\s*", "VILLA "),
        (r"^STA\s+", "SANTA "),
        (r"^STO\s+", "SARGENTO "),
        (r"^BRº\s*", "BARRIO "),
        (r"^Bº\s*", ""),
        (r"QTAS\s+DE\s+", "QUINTAS DE "),
        (r"JOSE I\.\s+DIAZ III", "JOSE IGNACIO DIAZ III"),
        (r"JOSE I\.\s+DIAZ IV",  "JOSE IGNACIO DIAZ IV"),
        (r"JOSE I\.\s+DIAZ V",   "JOSE IGNACIO DIAZ V"),
        (r"JOSE I\.\s+DIAZ",     "JOSE IGNACIO DIAZ"),
    ]
    for patron, reemplazo in reemplazos:
        n = re.sub(patron, reemplazo, n, flags=re.IGNORECASE)
    
    n = n.strip()
    
    # Paso 2: buscar en el mapping manual
    if n in MAPPING_MANUAL:
        return MAPPING_MANUAL[n]
    
    return n


def extraer_barrio_de_establecimiento(nombre_escuela: str) -> str:
    """
    Extrae el nombre del barrio desde la columna ESTABLECIMIENTO del raw.
    Formato típico: 'PEDRO CARANDE CARRO Bº CENTRO AMERICA'
    """
    if pd.isna(nombre_escuela):
        return ""
    
    # Buscar patrón: "Bº NOMBRE" o "Vª NOMBRE"
    patron = re.search(r"(?:Bº|Vª|V\.)\s+(.+)$", nombre_escuela, re.IGNORECASE)
    if patron:
        return patron.group(1).strip()
    
    return nombre_escuela.strip()


# ─────────────────────────────────────────────
# 2. CARGAR DATOS
# ─────────────────────────────────────────────
print("=" * 60)
print("SCRIPT: mejorar_escuelas.py")
print("Objetivo: corregir matching escuelas ↔ barrios censales")
print("=" * 60)

# Dataset censal
censal = pd.read_csv("data/processed/barrios_cordoba_censal_limpio.csv")
# Limpiar poblacion/hogares/nbi que vienen con comas de miles
# El CSV tiene valores como "1,061" (comillas incluidas en algunos casos)
for col in ["poblacion", "hogares", "nbi"]:
    censal[col] = (
        censal[col]
        .astype(str)
        .str.replace('"', '', regex=False)
        .str.replace(',', '', regex=False)
        .str.strip()
        .replace('nan', pd.NA)
        .replace('', pd.NA)
    )
    censal[col] = pd.to_numeric(censal[col], errors="coerce")
censal["barrio"] = censal["barrio"].str.strip().str.upper()

# Eliminar fila "SIN BARRIO"
antes = len(censal)
censal = censal[censal["barrio"] != "SIN BARRIO"]
print(f"\n[Censal] Filas originales: {antes} → después de eliminar 'SIN BARRIO': {len(censal)}")

# Dataset escuelas RAW (tiene info más completa con el nombre del establecimiento)
raw = pd.read_csv(
    "data/raw/ZONAS_ESCUELAS_MUNICIPALES_Corregido_2.csv",
    skiprows=1,          # saltar fila del título
    header=0
)
print(f"[Escuelas raw] Columnas: {list(raw.columns)}")
print(f"[Escuelas raw] Filas: {len(raw)}")


# ─────────────────────────────────────────────
# 3. EXTRAER Y NORMALIZAR BARRIOS DESDE EL RAW
# ─────────────────────────────────────────────
# La columna ESTABLECIMIENTO tiene el nombre completo con el barrio incluido
col_establecimiento = "ESTABLECIMIENTO"
raw = raw.dropna(subset=[col_establecimiento])
raw = raw[raw[col_establecimiento].str.strip() != ""]

# Extraer barrio desde el nombre del establecimiento
raw["barrio_original"] = raw[col_establecimiento].apply(extraer_barrio_de_establecimiento)
raw["barrio_normalizado"] = raw["barrio_original"].apply(normalizar_nombre_barrio)

print("\n[Escuelas] Mapeo de nombres de barrio:")
print(f"{'ORIGINAL':<30} {'NORMALIZADO':<35}")
print("-" * 65)
for _, row in raw.iterrows():
    print(f"{str(row['barrio_original']):<30} {str(row['barrio_normalizado']):<35}")


# ─────────────────────────────────────────────
# 4. AGRUPAR ESCUELAS POR BARRIO
# ─────────────────────────────────────────────
escuelas_por_barrio = (
    raw.groupby("barrio_normalizado")
    .size()
    .reset_index(name="escuelas_municipales")
)
escuelas_por_barrio.columns = ["barrio", "escuelas_municipales"]
escuelas_por_barrio = escuelas_por_barrio[escuelas_por_barrio["barrio"] != ""]

print(f"\n[Agrupado] Barrios con escuelas: {len(escuelas_por_barrio)}")
print(escuelas_por_barrio.to_string(index=False))


# ─────────────────────────────────────────────
# 5. VERIFICAR QUÉ BARRIOS COINCIDEN CON CENSAL
# ─────────────────────────────────────────────
censal_set = set(censal["barrio"])
sin_match = []
con_match = []

for barrio in escuelas_por_barrio["barrio"]:
    if barrio in censal_set:
        con_match.append(barrio)
    else:
        sin_match.append(barrio)

print(f"\n[Verificación] ✅ Con match en censal:  {len(con_match)}")
print(f"[Verificación] ❌ Sin match en censal:   {len(sin_match)}")
if sin_match:
    print("  Barrios sin match:", sin_match)


# ─────────────────────────────────────────────
# 6. UNIR CON DATASET CENSAL
# ─────────────────────────────────────────────
dataset_final = censal.merge(
    escuelas_por_barrio,
    on="barrio",
    how="left"
)
dataset_final["escuelas_municipales"] = dataset_final["escuelas_municipales"].fillna(0).astype(int)

# Agregar columna de porcentaje NBI
dataset_final["pct_nbi"] = (
    (dataset_final["nbi"] / dataset_final["hogares"]) * 100
).round(1)

total = len(dataset_final)
con_escuelas = (dataset_final["escuelas_municipales"] > 0).sum()

print(f"\n[Dataset final] Total barrios: {total}")
print(f"[Dataset final] Barrios con ≥1 escuela municipal: {con_escuelas}")
print(f"[Dataset final] Barrios sin escuela municipal: {total - con_escuelas}")
print(f"[Dataset final] Columnas: {list(dataset_final.columns)}")


# ─────────────────────────────────────────────
# 7. GUARDAR
# ─────────────────────────────────────────────
output_path = "data/processed/dataset_final_v2.csv"
dataset_final.to_csv(output_path, index=False)
print(f"\n✅ Dataset guardado en: {output_path}")
print("\n[Muestra de barrios CON escuelas]:")
print(dataset_final[dataset_final["escuelas_municipales"] > 0][
    ["barrio", "poblacion", "hogares", "nbi", "pct_nbi", "escuelas_municipales"]
].to_string(index=False))

print("\n[Muestra de barrios con mayor NBI sin escuelas municipales]:")
priority = dataset_final[
    (dataset_final["escuelas_municipales"] == 0) &
    (dataset_final["pct_nbi"].notna())
].nlargest(10, "pct_nbi")[["barrio", "poblacion", "nbi", "pct_nbi", "escuelas_municipales"]]
print(priority.to_string(index=False))
