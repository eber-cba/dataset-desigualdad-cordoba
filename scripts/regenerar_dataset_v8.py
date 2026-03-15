"""
regenerar_dataset_v8.py
========================
Pipeline Data Science & Feature Engineering (Versión 8)

Transforma la V7 en un dataset final pulido para Modelado Predictivo y Análisis de Desigualdad.
Implementa:
1. Auditoría de valores extremos (capping de outliers irreales).
2. Cálculo de métricas estandarizadas (por 1000 / 10000 hab).
3. Binarización de acceso a infraestructura.
4. Construcción del "infraestructura_score" empleando Normalización Min-Max.

Autor: Eber Coronel - Data Engineer Senior
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os

print("="*65)
print("EJECUTANDO V8 DE DATASET URBANO - DATA SCIENCE & FEATURE ENGINEERING")
print("="*65)

# ── 1. CARGA DE DATASET V7 E INSPECCIÓN BÁSICA ───────────────
input_path = "data/processed/dataset_final_v7.csv"
if not os.path.exists(input_path):
    print(f"Error: {input_path} no encontrado.")
    exit(1)

df = pd.read_csv(input_path)
print(f"\n[1/10] Dataset V7 cargado. Filas: {len(df)} | Columnas: {len(df.columns)}")

# Reporte Markdown (Iniciando)
report_md = [
    "# Reporte Técnico de Validación - Dataset Urbano v8",
    "\n## 1. Resumen de Transformaciones",
    "El presente reporte detalla las transformaciones de Feature Engineering aplicadas para llevar el dataset a nivel analítico (Machine Learning y GIS).",
]

# ── 2. FASE 1: AUDITORÍA ESTRUCTURAL BÁSICA ──────────────────
print("[2/10] Fase 1: Auditoría Estructural")
# Duplicados
dup_count = df.duplicated(subset=['barrio']).sum()
if dup_count > 0:
    df = df.drop_duplicates(subset=['barrio'])

# Columnas vacías y nulos
df = df.fillna(0)
for col in df.select_dtypes(include=[np.number]).columns:
    df.loc[df[col] < 0, col] = 0  # Reemplazar negativos por 0

report_md.extend([
    "\n## 2. Fase 1: Auditoría Estructural",
    f"- **Barrios duplicados removidos:** {dup_count}",
    "- **Manejo de Nulos y Negativos:** Se forzó a cero estadístico."
])

# ── 3. FASE 2: DETECCIÓN Y CORRECCIÓN DE OUTLIERS (Capping) ─
print("[3/10] Fase 2: Control de Outliers")
outliers_log = []

# Población (Rango max: 60,000)
pop_outliers = (df['poblacion'] > 60000).sum()
if pop_outliers > 0:
    outliers_log.append(f"- **Población:** {pop_outliers} barrios limitados al umbral máximo de 60,000 hab.")
    df['poblacion'] = np.clip(df['poblacion'], 0, 60000)

# Escuelas (Rango max: 40)
esc_outliers = (df['escuelas_total'] > 40).sum()
if esc_outliers > 0:
    outliers_log.append(f"- **Escuelas:** {esc_outliers} macro-zonas limitadas a 40 escuelas (filtrando ruido regional).")
    df['escuelas_estatales'] = np.clip(df['escuelas_estatales'], 0, 40)
    df['escuelas_privadas']  = np.clip(df['escuelas_privadas'],  0, 40)

# Centros de Salud (Max: 3)
cs_outliers = (df['centros_salud'] > 3).sum()
if cs_outliers > 0:
    outliers_log.append(f"- **CS:** {cs_outliers} barrios limitados a 3 Centros (evitando hospitales de alta complejidad o duplicaciones).")
    df['centros_salud'] = np.clip(df['centros_salud'], 0, 3)

# Comisarias (Max: 2)
com_outliers = (df['comisarias'] > 2).sum()
if com_outliers > 0:
    df['comisarias'] = np.clip(df['comisarias'], 0, 2)
    outliers_log.append(f"- **Comisarías:** {com_outliers} barrios limitados a 2 dependencias.")

# Paradas (Max: 120)
par_outliers = (df['paradas_colectivo'] > 120).sum()
if par_outliers > 0:
    df['paradas_colectivo'] = np.clip(df['paradas_colectivo'], 0, 120)
    outliers_log.append(f"- **Paradas:** {par_outliers} barrios limitados a 120 (corredores interurbanos descartados).")

report_md.append("\n## 3. Fase 2: Corrección de Outliers (Capping)")
report_md.extend(outliers_log if outliers_log else ["- No se requirió aplicar Capping brusco en variables críticas."])

# ── 4. FASE 3: VALIDACIÓN EDUCATIVA ──────────────────────────
print("[4/10] Fase 3: Restricciones Matemáticas")
df['escuelas_total'] = df['escuelas_estatales'] + df['escuelas_privadas']

report_md.extend([
    "\n## 4. Fase 3: Validación Educativa",
    "- Se recalculó algebraicamente `escuelas_total = estatales + privadas` para asegurar consistencia perfecta.",
    f"- Total de escuelas en el municipio sumadas: {df['escuelas_total'].sum():.0f}"
])

# ── 5. FASE 5: VALIDACIÓN GEOGRÁFICA (Documentación) ─────────
report_md.extend([
    "\n## 5. Fase 5: Validación Geográfica",
    "> [!WARNING] Limitación Espacial",
    "> Ante la falta de un Shapefile / GeoJSON oficial con los polígonos exactos de los 495 barrios censales, fue matemáticamente inviable utilizar el algoritmo `Point-in-Polygon`. Como mitigación documentada (ver v7), se empleó un híbrido de `Fuzzy Matching` Textual de alta precisión (>=75%) y Nearest-Neighbor `KD-Tree`."
])

# ── 6. FASE 7 y 8: FEATURE ENGINEERING (Tasas y Binarias) ────
print("[6/10] Fase 7 & 8: Generación de Features Derivadas")
df['hogares_por_poblacion'] = np.where(df['poblacion'] > 0, (df['hogares'] / df['poblacion']).round(3), 0)

# Tasas
df['escuelas_por_1000_hab'] = np.where(df['poblacion'] > 0, (df['escuelas_total'] / df['poblacion'] * 1000).round(2), 0.0)
df['centros_salud_por_10000_hab'] = np.where(df['poblacion'] > 0, (df['centros_salud'] / df['poblacion'] * 10000).round(2), 0.0)
df['comisarias_por_10000_hab'] = np.where(df['poblacion'] > 0, (df['comisarias'] / df['poblacion'] * 10000).round(2), 0.0)
df['paradas_por_1000_hab'] = np.where(df['poblacion'] > 0, (df['paradas_colectivo'] / df['poblacion'] * 1000).round(2), 0.0)
df['centros_vec_por_10000_hab'] = np.where(df['poblacion'] > 0, (df['centros_vecinales'] / df['poblacion'] * 10000).round(2), 0.0)

# Binarias
df['tiene_escuela'] = (df['escuelas_total'] > 0).astype(int)
df['tiene_centro_salud'] = (df['centros_salud'] > 0).astype(int)
df['tiene_comisaria'] = (df['comisarias'] > 0).astype(int)
df['tiene_transporte'] = (df['paradas_colectivo'] > 0).astype(int)

report_md.extend([
    "\n## 6. Fases 7 y 8: Variables Derivadas y Dummy Access",
    "Para habilitar un análisis equitativo entre macro-barrios y barrios pequeños, se derivaron las siguientes tasas y banderas lógicas:",
    "- `hogares_por_poblacion`, `_por_1000_hab`, `_por_10000_hab`.",
    "- Indicadores binarios `tiene_X`."
])

# ── 7. FASE 9: SCORE SINTÉTICO DE INFRAESTRUCTURA ────────────
print("[7/10] Fase 9: Score Multivariado")
# Escalar las 4 variables proxy de urbanización a rango 0-1
scaler = MinMaxScaler()
cols_to_scale = [
    'escuelas_por_1000_hab', 
    'centros_salud_por_10000_hab', 
    'paradas_por_1000_hab', 
    'comisarias_por_10000_hab'
]
# Preparamos los datos
scaled_data = scaler.fit_transform(df[cols_to_scale])
# Promediamos y re-escalamos suavemente para mejorar distribución
score = scaled_data.mean(axis=1)
df['infraestructura_score'] = np.round(score / score.max() if score.max() > 0 else 0, 3)

report_md.extend([
    "\n## 7. Fase 9: Índice Sintético de Infraestructura",
    "Se instrumentó un `infraestructura_score` [0-1] calculado como la media estandarizada (MinMaxScaler) de las tasas de escuelas, transporte, comisarías y salud. Útil para mapas de calor."
])


# ── 8. FASE 4 y 6 : COBERTURA Y ESTADÍSTICA FINAL ────────────
print("[8/10] Fase 4 & 6: Métricas y Cobertura")
report_md.append("\n## 8. Fase 4 & 6: Tabla de Cobertura y Descriptiva V8\n")
stats = df.describe().T
num_df = df.select_dtypes(include=[np.number])
stats['cobertura_%'] = ((num_df > 0).sum() / len(df) * 100).round(1)

# Tabulación Simple Markdown
report_md.append("| Variable | Cobertura % | Media | Max |")
report_md.append("|---|---|---|---|")
for idx, row in stats.iterrows():
    if idx in df.columns[1:]:  # Ignorar barrio
        report_md.append(f"| `{idx}` | {row['cobertura_%']}% | {row['mean']:.2f} | {row['max']:.2f} |")


# ── 9. EXPORTACIÓN V8 ────────────────────────────────────────
print("[9/10] Finalizando...")
out_csv = "data/processed/dataset_final_v8.csv"
out_md = "reporte_validacion_dataset_v8.md"

df.to_csv(out_csv, index=False, encoding='utf-8-sig')
with open(out_md, "w", encoding='utf-8') as f:
    f.write("\n".join(report_md))

print(f"\n[10/10] ✅ PROCESO EXITOSO!")
print(f" -> CSV Generado: {out_csv} (Columnas: {len(df.columns)})")
print(f" -> MD  Generado: {out_md}")
