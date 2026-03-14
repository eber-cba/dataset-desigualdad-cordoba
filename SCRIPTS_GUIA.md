# 📖 GUÍA DE SCRIPTS — Dataset Desigualdad Urbana Córdoba
> Qué hace cada script, por qué existe, cómo funciona, qué genera

---

## 📁 Ubicación: `scripts/`

---

## 1. `clean_dataset.py`

### ¿Qué hace?
Limpia el dataset censal de barrios de Córdoba. Es el **primer script** que se ejecuta.

### ¿Por qué existe?
El archivo raw descargado del portal tiene:
- Columnas técnicas de GIS (`geometry`, `shape_area`, `shape_length`, `objectid`) que no sirven para análisis de datos
- Nombres de columnas en inglés o con mayúsculas/minúsculas inconsistentes
- Filas con barrios vacíos, con valor `SD` (sin datos), o `NULL`
- Barrios duplicados (el mapa tiene múltiples puntos por barrio)
- Números con comas de miles como texto (`"1,061"` en vez de `1061`)

### ¿Cómo funciona?
```
Entrada:  data/raw/Barrios_de_Córdoba_con_información_censal_afkGL16.csv
          (formato censal con ~500 barrios, campos: barrio, poblacion, hogares, nbi)

Proceso:
  1. Carga el CSV con pandas
  2. Elimina columnas GIS irrelevantes
  3. Renombra columnas a snake_case
  4. Elimina filas donde barrio == 'SD', 'NULL', '-', vacío
  5. Elimina barrios duplicados (mantiene el primero)
  6. Convierte poblacion, hogares, nbi de texto a número

Salida:   data/processed/barrios_cordoba_censal_limpio.csv
          (~496 barrios limpios con: barrio, poblacion, hogares, nbi)
```

### Variables que produce
| Columna | Qué mide |
|---------|----------|
| `barrio` | Nombre oficial del barrio |
| `poblacion` | Personas residentes (Censo 2010) |
| `hogares` | Familias / unidades domésticas |
| `nbi` | Hogares con al menos 1 Necesidad Básica Insatisfecha |

### ¿Qué es NBI?
Un hogar tiene NBI si tiene al menos uno de estos problemas:
- Vivienda inadecuada (rancho, casilla, pieza de hotel)
- Hacinamiento crítico (>3 personas por cuarto)
- Sin baño con descarga de agua
- Sin escolaridad (ningún miembro con primaria completa)
- Niños de 6-12 años que no asisten a la escuela

**NBI solo cuenta hogares, no personas.** Por eso existe `pct_nbi`.

---

## 2. `limpiar_escuelas.py` ⚠️ (OBSOLETO — ver mejorar_escuelas.py)

### ¿Qué hacía?
Limpiaba el dataset de escuelas municipales extrayendo el nombre del barrio.

### ¿Por qué está obsoleto?
El script extraía el barrio de forma incorrecta y el matching con el censal fallaba (21 de 37 nombres no coincidían). Fue reemplazado por `mejorar_escuelas.py`.

---

## 3. `agrupar_escuelas.py` ⚠️ (OBSOLETO)

### ¿Qué hacía?
Agrupaba las escuelas por barrio para contar cuántas hay en cada uno.

### ¿Por qué está obsoleto?
Esta lógica fue absorbida por `mejorar_escuelas.py` de forma más correcta.

---

## 4. `normalizar_y_unir.py` / `unir_datasets.py` ⚠️ (OBSOLETOS)

### ¿Qué hacían?
Unían el dataset de escuelas con el censal.

### ¿Por qué están obsoletos?
Reemplazados por `mejorar_escuelas.py` que hace todo el pipeline de punta a punta.

---

## 5. `mejorar_escuelas.py` ✅ (ACTUAL)

### ¿Qué hace?
Es el script **principal** de procesamiento de escuelas. Resuelve el problema de matching de nombres y genera el dataset v2.

### ¿Por qué existe?
El problema central era que los nombres de barrio en el dataset de escuelas usaban abreviaturas distintas a las del dataset censal:

| En dataset escuelas | En dataset censal |
|--------------------|-------------------|
| `Vª AZALAIS` | `VILLA AZALAIS` |
| `STA ISABEL` | `SANTA ISABEL SECCION 1` |
| `JOSE I. DIAZ III` | `JOSE IGNACIO DIAZ SECCION 3` |
| `QTAS DE ARGUELLO` | `QUINTAS DE ARGUELLO` |
| `ARENALES` | `GENERAL ARENALES` |
| `LICEO` | `PARQUE LICEO SECCION 1` |
| `STO CABRAL` | `SARGENTO CABRAL` |
| ... (21 casos en total) | |

### ¿Cómo funciona?
```
Entrada:  data/raw/ZONAS_ESCUELAS_MUNICIPALES_Corregido_2.csv
          data/processed/barrios_cordoba_censal_limpio.csv

Proceso:
  Función extraer_barrio_de_establecimiento():
    → El nombre del establecimiento tiene el barrio embebido
    → Ejemplo: "PEDRO CARANDE Bº CENTRO AMERICA" → "CENTRO AMERICA"
    → Busca el patrón "Bº X" o "Vª X" con regex

  Función normalizar_nombre_barrio():
    → Aplica sustituciones regex:
        Vª → VILLA
        STA → SANTA
        STO → SARGENTO
        Bº → (eliminar)
        QTAS DE → QUINTAS DE
        JOSE I. DIAZ III → JOSE IGNACIO DIAZ III
    → Busca en el diccionario MAPPING_MANUAL para casos especiales

  MAPPING_MANUAL (diccionario Python):
    → 21 entradas con casos que no se resuelven con regex
    → La lógica de mapping está documentada como comentario junto a cada entrada

  Luego:
    → Agrupa escuelas por barrio_normalizado (cuenta cuántas hay)
    → Elimina filas donde barrio = "SIN BARRIO"
    → Hace LEFT JOIN escuelas → censal (por columna barrio)
    → Rellena barrios sin escuelas con 0
    → Calcula pct_nbi = (nbi / hogares) * 100

Salida:   data/processed/dataset_final_v2.csv
          (494 barrios con: barrio, poblacion, hogares, nbi, escuelas_municipales, pct_nbi)
```

### Decisiones técnicas tomadas
- **LEFT JOIN en vez de INNER JOIN:** para mantener TODOS los barrios del censal, aunque no tengan escuelas
- **fillna(0)** en escuelas: un barrio sin escuelas municipales registradas = 0 (no NaN)
- **pct_nbi en vez de nbi solo:** el NBI absoluto favorece barrios más poblados. El % permite comparar cualquier barrio independientemente de su tamaño.

### Variables que produce
| Columna | Qué mide | Cómo se calcula |
|---------|----------|-----------------|
| `escuelas_municipales` | Escuelas primarias municipales | Conteo por barrio desde el dataset raw |
| `pct_nbi` | % de hogares con NBI | `(nbi / hogares) * 100` redondeado a 1 decimal |

### ⚠️ Limitación importante
Solo incluye las **38 escuelas municipales** de Córdoba. Córdoba tiene además escuelas nacionales y provinciales que **no están en este dataset**. Un barrio con `escuelas_municipales = 0` puede tener escuelas de otro tipo.

---

## 6. `analisis_prioridad.py`

### ¿Qué hace?
Genera un ranking de barrios por urgencia social: barrios con alta población Y alto NBI pero sin escuelas registradas.

### ¿Por qué existe?
Sirve para que el mentor y los alumnos puedan responder preguntas como: *"¿cuáles son los barrios que más necesitan servicios?"*

### ¿Cómo funciona?
```
Entrada:  data/processed/dataset_educacion_barrios_cordoba.csv (versión anterior)

Proceso:
  Criterio 1: Alta población (top 75% de población)
  Criterio 2: Alto NBI (top 75% de NBI)
  Criterio 3: Sin escuelas registradas

  Score compuesto = normalizar(poblacion) + normalizar(nbi)
  → Ranking por score descendente

Salida:   salida_analisis.txt (imprime en consola)
```

### Nota
Este script usa el dataset v1 (con bugs de matching). Conviene actualizarlo para usar `dataset_final_v2.csv`.

---

## 7. `procesar_salud.py` ✅ (ACTIVO — v3)

### ¿Qué hace?
Procesa el dataset de centros de salud municipales de Córdoba y genera `dataset_final_v3.csv`.

### ¿Cómo funciona?
```
Entradas: data/raw/centros_salud_cordoba.csv
          data/processed/dataset_final_v2.csv

Proceso:
  → Filtra por tipo: Centro de Salud, Hospital, HPA
  → Extrae barrio desde el nombre del centro (regex sobre "CS N° XX - NOMBRE")
  → Diccionario MAPPING_SALUD con ~70 entradas de normalización
  → Conteo por barrio, LEFT JOIN con v2

Salida: data/processed/centros_salud_limpio.csv
        data/processed/dataset_final_v3.csv (+ columna centros_salud)
```

---

## 8. `integrador_dataset.py` ✅ (ACTIVO — v4)

### ¿Qué hace?
Integra transporte (GTFS), luminarias, comisarías y centros vecinales. Genera `dataset_final_v4.csv`.

### ¿Cómo funciona?
- Usa **KD-tree** (`scipy.cKDTree`) con centroides de barrio (derivados de `centros_salud_limpio.csv`)
- Asigna cada punto GPS (parada, comisaría, etc.) al barrio más cercano
- LEFT JOINs sucesivos sobre `dataset_final_v3.csv`

---

## 9. `descargar_escuelas_wfs.py` ✅ (NUEVO — v0.7)

### ¿Qué hace?
Descarga automáticamente los establecimientos educativos desde el WFS oficial de IDECOR (MapasCórdoba), sin necesidad de QGIS ni interfaz gráfica.

### ¿Por qué existe?
El usuario pidió descargar el mapa https://mapascordoba.gob.ar/viewer/mapa/77. El sitio es una SPA con JavaScript. Se descubrió el endpoint WFS subyacente y se automatizó la descarga con Python puro (`urllib` + `geopandas`).

### ¿Cómo funciona?
```
Proceso:
  1. Prueba una lista de endpoints GeoServer conocidos
  2. Al encontrar el WFS activo (idecor-ws.mapascordoba.gob.ar),
     hace GetCapabilities para listar capas disponibles
  3. Filtra capas con "educ" en el nombre
  4. Descarga con GetFeature → outputFormat=application/json
  5. Convierte GeoJSON a CSV con coordenadas lat/lon

Salidas: data/raw/escuelas_cordoba_wfs.geojson  ← GeoJSON completo
         data/raw/escuelas_cordoba.csv           ← CSV listo para pandas
         (5,471 establecimientos de toda la provincia)
```

### Variables que produce
| Columna | Qué contiene |
|---------|-------------|
| `cueanexo` | Código único del establecimiento (CUEANEXO) |
| `nombre` | Nombre completo del establecimiento |
| `est_sector` | "Estatal" o "Privado" |
| `est_ambito` | "Urbano" o "Rural" |
| `est_domicilio` | Dirección |
| `est_barrio` | Barrio declarado (texto libre) |
| `est_localidad` | Localidad |
| `est_departamento` | Departamento de Córdoba |
| `nivel` | Nivel educativo (Inicial, Primario, Secundario, etc.) |
| `n_plan_estudio` | Plan de estudio |
| `lat` / `lon` | Coordenadas WGS84 |

---

## 10. `integrar_escuelas_idecor.py` ✅ (NUEVO — v0.7)

### ¿Qué hace?
Integra los datos de IDECOR al `dataset_final_v4.csv`, generando `dataset_final_v5.csv` con 3 columnas nuevas de establecimientos educativos.

### ¿Por qué existe?
El dataset anterior solo tenía `escuelas_municipales` (38 establecimientos). Con los datos de IDECOR se puede cuantificar la **cobertura educativa real** de cada barrio, distinguiendo sector público de privado.

### ¿Cómo funciona?
```
Entradas: data/raw/escuelas_cordoba.csv
          data/processed/dataset_final_v4.csv
          data/processed/centros_salud_limpio.csv (para centroides)

Proceso:
  1. Filtra establecimientos al departamento Capital + bbox ciudad:
     lat ∈ [-31.55, -31.20], lon ∈ [-64.35, -64.00]
  2. Calcula centroides de barrio (igual que integrador_dataset.py)
  3. KD-tree: asigna cada escuela al barrio más cercano
  4. Cuenta por barrio: total, estatales, privadas
  5. Guarda escuelas_idecor_limpio.csv para referencia
  6. LEFT JOIN sobre dataset_final_v4 → dataset_final_v5

Salidas: data/processed/escuelas_idecor_limpio.csv
         data/processed/dataset_final_v5.csv (15 columnas)
```

### Variables que produce
| Columna | Qué mide |
|---------|----------|
| `escuelas_total` | Total de establecimientos asignados al barrio |
| `escuelas_estatales` | Solo establecimientos estatales (públicos) |
| `escuelas_privadas` | Solo establecimientos privados |

### ⚠️ Limitación
Usa los mismos 91 centroides del script anterior. Los ~400 barrios sin centroide conocido quedan con 0 en las columnas nuevas. Para mejorar se necesita el shapefile de polígonos de todos los barrios.

---

## 11. `test_dataset.py` ✅ (NUEVO — v0.7)

### ¿Qué hace?
Suite de tests automáticos (22 en total) que validan la integridad del dataset y los archivos intermedios. Debe ejecutarse después de cualquier cambio.

### ¿Cómo correrlo?
```bash
# Ejecución directa
python scripts/test_dataset.py

# Con pytest (más detallado)
python -m pytest scripts/test_dataset.py -v
```

### Tests incluidos

| Clase | Test | Qué valida |
|-------|------|-----------|
| `TestDatasetV5` | `test_01_columnas_presentes` | Las 15 columnas de v5 existen |
| `TestDatasetV5` | `test_02_tipos_numericos` | Columnas numéricas no son object |
| `TestDatasetV5` | `test_03_cantidad_barrios` | Exactamente 494 filas |
| `TestDatasetV5` | `test_04_barrios_sin_duplicados` | Sin barrios repetidos |
| `TestDatasetV5` | `test_05_sin_barrio_sin_nombre` | Ningún barrio vacío/NaN |
| `TestDatasetV5` | `test_06_pct_nbi_rango` | pct_nbi ∈ [0, 100] |
| `TestDatasetV5` | `test_07_sin_valores_negativos` | Sin negativos en columnas numéricas |
| `TestDatasetV5` | `test_08_cobertura_escuelas_total` | ≥50 barrios con escuelas_total > 0 |
| `TestDatasetV5` | `test_09_cobertura_escuelas_estatales` | ≥40 barrios con escuelas_estatales > 0 |
| `TestDatasetV5` | `test_10_estatales_leq_total` | estatales ≤ total en todos los barrios |
| `TestDatasetV5` | `test_11_privadas_leq_total` | privadas ≤ total en todos los barrios |
| `TestDatasetV5` | `test_12_suma_leq_total` | estatales + privadas ≤ total |
| `TestDatasetV5` | `test_13_retrocompat_columnas_v4` | Todas las columnas de v4 presentes en v5 |
| `TestDatasetV5` | `test_14_retrocompat_escuelas_municipales` | `escuelas_municipales` no cambió |
| `TestEscuelasRaw` | `test_01_columnas_basicas` | Columnas clave en el raw |
| `TestEscuelasRaw` | `test_02_cantidad_minima` | ≥5000 registros descargados |
| `TestEscuelasRaw` | `test_03_coordenadas_validas` | lat/lon en rango Argentina |
| `TestEscuelasRaw` | `test_04_sectores_conocidos` | Solo "Estatal" o "Privado" |
| `TestEscuelasRaw` | `test_05_sin_nombres_vacios` | Menos del 1% sin nombre |
| `TestEscuelasProcesadas` | `test_01_columna_barrio_asignado` | `barrio_asignado` presente |
| `TestEscuelasProcesadas` | `test_02_tasa_asignacion` | ≥80% de escuelas asignadas a un barrio |
| `TestEscuelasProcesadas` | `test_03_escuelas_en_ciudad` | Todas dentro del bbox de Córdoba |

---

## 🗂️ Flujo completo de datos — v5

```
FUENTES RAW
  │
  ├── Barrios_censal.csv
  │       └── clean_dataset.py
  │               └── barrios_cordoba_censal_limpio.csv
  │                                   │
  ├── ZONAS_ESCUELAS_MUNICIPALES.csv  │
  │       └── mejorar_escuelas.py ────┤
  │               └── dataset_final_v2.csv
  │                                   │
  ├── centros_salud_cordoba.csv       │
  │       └── procesar_salud.py ──────┤──→ centros_salud_limpio.csv (centroides)
  │               └── dataset_final_v3.csv           │
  │                                   │              │
  ├── gtfs + luminarias + comisarías  │              │
  │       └── integrador_dataset.py ──┤              │
  │               └── dataset_final_v4.csv           │
  │                                   │              │
  └── WFS IDECOR (5,471 escuelas)    │              │
          └── descargar_escuelas_wfs.py              │
          └── escuelas_cordoba.csv                   │
                  └── integrar_escuelas_idecor.py ───┘
                          └── dataset_final_v5.csv  ← DATASET FINAL

VALIDACIÓN:
          └── test_dataset.py  (22 tests, todos OK ✅)
```
