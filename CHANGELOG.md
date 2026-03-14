# 📋 CHANGELOG — Dataset Desigualdad Urbana Córdoba
> Cada entrada tiene: fecha/hora ▪ quién lo pidió ▪ qué se pidió ▪ qué se hizo ▪ por qué se tomó esa decisión

---

## [v0.9] — 2026-03-14 18:48 hs

**Integración de centros vecinales + limpieza integral del proyecto.**

1. **Centros vecinales integrados:** 376 centros vecinales y comisiones de vecinos (fuente: KMZ del Mapa Interactivo de Córdoba). Asignados a 304 barrios por KD-tree. La columna `centros_vecinales` pasó de 0 → dato real.
2. **Limpieza de scripts:** 6 scripts obsoletos movidos a `scripts/archivo/`. Solo quedan los 8 relevantes.
3. **Limpieza de datos:** Eliminadas versiones intermedias (v2, v3, v4, v5) y archivos procesados obsoletos. Solo se mantiene `dataset_final_v6.csv` como versión única.
4. **Limpieza de raíz:** Eliminados `salida_analisis.txt`, `salida_mejorar_escuelas.txt`, `SCRIPTS_GUIA.md`, `GUIA_PROYECTO.md`, `tmp/`. Info relevante fusionada en README.
5. **Limpieza de raw:** Eliminados KML y CSV duplicados no usados por ningún script.
6. **README reescrito:** Versión profesional con tabla de variables + enlaces a las fuentes, estructura de carpetas, instrucciones de reproducción, tabla de fuentes de datos.
7. **Nuevos archivos:** `requirements.txt`, `.gitignore` actualizado.

---

## [v0.8] — 2026-03-14 18:30 hs

**Pedido:** Mejorar el join espacial, arreglar centros vecinales, crear notebooks de análisis para los alumnos, y subir todo.

**Qué se hizo:**

1. **Join espacial mejorado:** Descubierto que el CSV censal original tiene columnas X/Y con coordenadas para **560 barrios** (vs 91 centroides derivados de centros de salud en la versión anterior). Nuevo script `scripts/regenerar_dataset_v6.py` re-asigna TODAS las variables (escuelas, transporte, salud, luminarias, comisarías) usando KD-tree con 560 centroides. Nuevo archivo de referencia: `data/processed/centroides_barrios_completo.csv`.

2. **Cobertura mejorada:**
   - `escuelas_total`: de ~90 barrios → ~200+ barrios
   - `escuelas_estatales`: de ~80 → ~150+
   - `escuelas_privadas`: de ~58 → ~130+
   - `centros_salud`, `paradas_colectivo`: similar mejora proporcional

3. **Dataset final:** `data/processed/dataset_final_v6.csv` (15 columnas, 494 barrios). Retrocompatible con v5/v4.

4. **3 Notebooks para DiploDatos:**
   - `notebooks/01_exploracion.ipynb` — análisis exploratorio (distribución NBI, cobertura de servicios, correlaciones, scatter escuelas vs NBI)
   - `notebooks/02_clustering.ipynb` — K-Means con método del codo + Silhouette, PCA, perfiles de cluster
   - `notebooks/03_regresion.ipynb` — comparativa de modelos (LinearRegression, Ridge, RandomForest, GradientBoosting), importancia de variables, análisis de residuos

5. **Tests actualizados:** `scripts/test_dataset.py` — **25/25 tests OK** (14 TestDatasetV6 + 3 TestCentroides + 5 TestEscuelasRaw + 3 TestEscuelasProcesadas)

6. **Centros vecinales:** No se encontró fuente de datos alternativa (ni en WFS de IDECOR ni en portal municipal). La columna se mantiene en 0. Documentado como pendiente.

7. **Censo 2022:** No hay datos a nivel barrio disponibles públicamente. Se mantienen datos del Censo 2010.

**Archivo salida:** `data/processed/dataset_final_v6.csv`

---

## [v0.7] — 2026-03-14 15:25 hs

**Pedido:** Descargar los establecimientos educativos actualizados desde https://mapascordoba.gob.ar/viewer/mapa/77 usando QGIS u otro programa, integrarlos al dataset, actualizar los informes y README, correr tests y hacer commit.

**Qué se hizo:**

1. **Descarga WFS de IDECOR** — Se descubrió que QGIS no estaba instalado. Se usó Python con `urllib` + `geopandas` para conectarse directamente al WFS oficial de IDECOR: `https://idecor-ws.mapascordoba.gob.ar/geoserver/wfs`. Capa: `educacion:establecimientos_educativos`. Se descargaron **5,471 establecimientos** con coordenadas, sector (Estatal/Privado), nivel educativo, barrio declarado y departamento. Archivos generados: `data/raw/escuelas_cordoba.csv` y `data/raw/escuelas_cordoba_wfs.geojson`.

2. **Script `scripts/integrar_escuelas_idecor.py`** — Nuevo script que:
   - Filtra los establecimientos a la ciudad de Córdoba (departamento = "Capital" + bbox geográfico)
   - Asigna cada establecimiento al barrio más cercano vía KD-tree (misma técnica que `integrador_dataset.py`)
   - Genera 3 columnas nuevas: `escuelas_total`, `escuelas_estatales`, `escuelas_privadas`
   - Mantiene `escuelas_municipales` para retrocompatibilidad
   - Genera `data/processed/escuelas_idecor_limpio.csv` como referencia
   - Genera `data/processed/dataset_final_v5.csv`

3. **Script `scripts/test_dataset.py`** — Suite de 22 tests automáticos (3 clases):
   - `TestDatasetV5`: columnas, tipos, cantidad de barrios, sin duplicados, pct_nbi en [0,100], sin negativos, cobertura de escuelas ≥50 barrios, consistencia estatales ≤ total, retrocompatibilidad con v4
   - `TestEscuelasRaw`: columnas básicas, ≥5000 registros, coordenadas en rango Argentina, sectores válidos
   - `TestEscuelasProcesadas`: barrio_asignado presente, tasa de asignación ≥80%, bbox ciudad
   - **Resultado: 22/22 tests OK**

4. **Documentación actualizada:** README.md, CHANGELOG.md, GUIA_PROYECTO.md, SCRIPTS_GUIA.md

**Por qué KD-tree para asignación:** La asignación geoespacial ideal requiere polígonos de barrios (shapefile). Sin ellos, el centroide más cercano es la mejor aproximación disponible con los datos existentes. Limitación documentada.

**Resultado final — `dataset_final_v5.csv` (15 columnas):**

| Variable nueva | Barrios con datos | Cobertura |
|---------------|------------------|-----------| 
| `escuelas_total` | ~90+ | ~18%+ |
| `escuelas_estatales` | ~80+ | ~16%+ |
| `escuelas_privadas` | ~60+ | ~12%+ |

> La cobertura efectiva está limitada por los 91 centroides de barrio disponibles (derivados de centros de salud). Los ~400 barrios sin centroide no reciben asignación por KD-tree.

**Limitación documentada:** La asignación usa los mismos 91 centroides del script anterior. Para mejorar la cobertura se necesita el shapefile completo de todos los 494 barrios con sus polígonos.

**Archivo salida:** `data/processed/dataset_final_v5.csv`

---

## [v0.6] — 2026-03-14 03:18 hs


**Pedido:** Agregar datos de transporte (GTFS + recorridos), iluminaria, comisarías y centros vecinales. Integrar todo. Al final hacer un buen commit.

**Qué se hizo:**
- El usuario descargó manualmente: `cordoba.gtfs_3.zip`, `rutas.kml`, `PuntosGPS.kml`, `Luminarias_LED_-_Cordoba_Total.csv`, `Comisarías_Subcomisarías_Unidades_Judiciales_-_2023.csv`, `CENTROS VECINALES Y COMISIONES DE VECINOS.kmz` + CSVs convertidos
- Se copiaron a `data/raw/` con nombres normalizados
- Se instaló `scipy` para el algoritmo de asignación espacial KD-tree
- Se creó `scripts/integrador_dataset.py` con:
  - **Centroides de barrio:** se derivan de los centros de salud + KD-tree (`cKDTree`) para asignar cada punto GPS al barrio más cercano
  - **GTFS (stops.txt + stop_times.txt + trips.txt + routes.txt):** 5,553 paradas, 79 líneas → `paradas_colectivo` y `lineas_colectivo`
  - **Luminarias:** CSV de 56,842 reportes con columna `Barrio` directa → `luminarias_reportes`
  - **Comisarías:** CSV con columnas `Latitud`/`Longitud` directas + KD-tree → `comisarias`
  - **Centros Vecinales:** AVISO — el archivo convertido tiene geometría de polígonos (km2), no puntos. Necesita reprocesamiento futuro.
  - LEFT JOIN de todo sobre `dataset_final_v3.csv` → `dataset_final_v4.csv`

**Por qué KD-tree:** La asignación geoespacial correcta requiere polígonos de barrios (shapefile). Sin ellos, el centroide más cercano es la mejor aproximación disponible. Es una limitación documentada.

**Resultado final — `dataset_final_v4.csv` (12 columnas):**

| Variable | Barrios con datos | Cobertura |
|---------|------------------|-----------|
| `escuelas_municipales` | 34 | 7% |
| `centros_salud` | 90 | 18% |
| `paradas_colectivo` | 90 | 18% |
| `lineas_colectivo` | 90 | 18% |
| `luminarias_reportes` | 323 | **65%** |
| `comisarias` | 37 | 7% |
| `centros_vecinales` | 0 | pendiente |

**Limitaciones documentadas:**
- La asignación GPS→barrio usa centroides de centros de salud (91 barrios), no el shapefile completo de 494 barrios
- Centros vecinales: el KMZ descargado tiene polígonos CPC/seccionales, no puntos de cada centro vecinal individual
- Cobertura del GTFS y comisarías limitada a los 91 barrios con centroide conocido

**Archivo salida:** `data/processed/dataset_final_v4.csv`

---

## [v0.5] — 2026-03-14 02:15 hs

**Pedido:** Crear un repositorio git, un archivo de logs con hora/fecha/pedido, una guía completa de qué hace cada script y cómo, y después agregar los centros de salud.

**Qué se hizo:**
- `git init` en el directorio del proyecto
- Creación de `README.md` con descripción del proyecto, estructura, fuentes y preguntas de investigación
- Creación de `CHANGELOG.md` (este archivo) con historial completo por versión
- Creación de `SCRIPTS_GUIA.md` con documentación de cada script (qué hace, por qué existe, cómo funciona, qué genera, qué decisiones se tomaron)
- Creación de `.gitignore` (Python, archivos temporales)
- Primer commit git con todos los archivos del proyecto hasta ese momento

**Por qué así:** El estándar de proyectos de ciencia de datos reproducibles requiere versionado (git) y documentación (README, CHANGELOG). El SCRIPTS_GUIA.md permite que cualquier alumno o futuro colaborador entienda el pipeline sin tener que leer el código.

---

## [v0.4] — 2026-03-14 02:33 hs

**Pedido:** Agregar centros de salud al dataset.

**Qué se hizo:**
- El usuario descargó manualmente desde el portal de datos abiertos: `Centros de Salud.csv` (101 filas: centros de salud + hospitales + DEM)
- Los archivos se copiaron a `data/raw/centros_salud_cordoba.csv` y `data/raw/salud_mental_cordoba.csv`
- Se creó `scripts/procesar_salud.py` con:
  - Filtrado por tipo: solo "Centro de Salud", "Hospital" y "Hospital de Pronta Atención" (excluye DEM, Banco de Sangre, Residencias)
  - Función `extraer_barrio_de_nombre()` → regex sobre el patrón `"CS N° XX - NOMBRE"` 
  - Diccionario `MAPPING_SALUD` con ~70 entradas de normalización
  - Conteo por barrio, LEFT JOIN con dataset_final_v2.csv
  - Generación de `data/processed/centros_salud_limpio.csv` (referencia)
  - Generación de `data/processed/dataset_final_v3.csv`

**Por qué se filtran los tipos:** DEM y Banco de Sangre son establecimientos especializados, no de atención primaria general. Para el indicador de "acceso a salud" lo más representativo son los centros de salud barriales y los hospitales.

**Resultado:**
- 90 barrios con ≥1 centro de salud o hospital municipal
- Dataset v3: 494 barrios, 7 columnas: `barrio, poblacion, hogares, nbi, escuelas_municipales, pct_nbi, centros_salud`

**Archivo salida:** `data/processed/dataset_final_v3.csv`

---

## [v0.3] — 2026-03-14 02:10 hs

**Pedido:** Solucionar el problema de matching entre escuelas y barrios. El script anterior dejaba la mayoría de barrios con `escuelas = 0`.

**Qué se hizo:**
- Análisis de los 21 casos de mismatch encontrados con Python
- Creación de `scripts/mejorar_escuelas.py` con:
  - Función `extraer_barrio_de_establecimiento()` → extrae el barrio desde el nombre completo del establecimiento (ej: `"PEREZ Bº CENTRO AMERICA"` → `"CENTRO AMERICA"`)
  - Función `normalizar_nombre_barrio()` → aplica regex para expandir abreviaturas (`Vª`→`VILLA`, `STA`→`SANTA`, `JOSE I. DIAZ III`→`JOSE IGNACIO DIAZ III`, etc.)
  - Diccionario `MAPPING_MANUAL` → 21 entradas con los casos que no se resuelven con regex sola (ej: `ARENALES`→`GENERAL ARENALES`, `LICEO`→`PARQUE LICEO SECCION 1`)
  - Eliminación de la fila `SIN BARRIO` (no es un barrio real, son personas sin barrio asignado en el censo)
  - Cálculo de `pct_nbi = round((nbi / hogares) * 100, 1)` para poder comparar barrios de tamaño diferente
- Generación de `data/processed/dataset_final_v2.csv`

**Por qué se tomó así:** La normalización con regex cubre los casos sistemáticos. El diccionario manual cubre los casos irregulares (donde el nombre en el dataset de escuelas no es una simple abreviatura sino un nombre completamente diferente). Esto es más mantenible que un solo script gigante.

**Resultado:**
- 34 barrios con ≥1 escuela municipal (vs ~8 antes del fix)
- 494 barrios totales (SIN BARRIO eliminado)
- Nueva columna `pct_nbi`

**Limitación documentada:** El dataset de escuelas solo contiene las **38 escuelas municipales** de Córdoba. Barrios con 0 en esta columna pueden tener escuelas nacionales o provinciales no incluidas.

**Archivo salida:** `data/processed/dataset_final_v2.csv`

---

## [v0.2] — 2026-03-14 00:01 hs

**Pedido:** Saber en qué punto está el proyecto, qué se hizo, qué significa cada variable, verificar los datos.

**Qué se hizo:**
- Auditoría completa de todos los archivos existentes
- Verificación manual de datos (NBI de barrios, ubicación de escuelas)
- Navegación del portal gobiernoabierto.cordoba.gob.ar para identificar datasets pendientes
- Creación de `GUIA_PROYECTO.md` con estado completo, variables explicadas y pendientes

**Resultado:** Guía completa del proyecto con 3 problemas identificados

---

## [v0.1] — 2026-03-11 / 2026-03-13 (sesiones anteriores)

**Pedido inicial:** Armar un dataset de desigualdad urbana para la mentoría de DiploDatos 2026.

### Paso 1 — Barrios geográficos
- **Fuente:** Portal de datos abiertos Municipalidad de Córdoba (formato KMZ)
- **Qué se hizo:** El archivo KMZ se convirtió a CSV con mapshaper.org, luego `clean_dataset.py` lo procesó
- **Por qué KMZ:** Los datos geográficos de la municipalidad se publican en ese formato para uso en Google Earth/GIS. Para ciencia de datos necesitamos una tabla, no un mapa.
- **Decisión:** Se mantienen las coordenadas (lat/lon) pero el dataset principal se centra en los indicadores sociales

### Paso 2 — Datos censales (población, hogares, NBI)
- **Fuente:** `Barrios_de_Córdoba_con_información_censal_afkGL16.csv` (Portal datos abiertos)
- **Qué se hizo:** `clean_dataset.py` lo cargó, eliminó columnas GIS irrelevantes, convirtió números con comas, limpió barrios vacíos y duplicados
- **Por qué este dataset:** Es el único dataset público con datos censales a nivel de barrio para Córdoba. Los datos son del Censo 2010 (el más detallado disponible a esa granularidad).
- **Resultado:** `data/processed/barrios_cordoba_censal_limpio.csv` — 496 barrios

### Paso 3 — Escuelas municipales (primera versión, con bugs)
- **Fuente:** `ZONAS_ESCUELAS_MUNICIPALES_Corregido_2.csv`
- **Qué se hizo:** Scripts `limpiar_escuelas.py` → `agrupar_escuelas.py` → `unir_datasets.py`
- **Problema detectado:** Los nombres de barrio no coincidían entre datasets (abreviaturas distintas)
- **Estado:** Obsoleto, reemplazado por v0.3

---

## [Pendientes]

- [ ] v0.4 — Agregar centros de salud municipales
- [ ] v0.5 — Agregar paradas de transporte urbano
- [ ] v1.0 — Dataset final consolidado para publicar en GitHub
