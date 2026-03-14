# 📋 CHANGELOG — Dataset Desigualdad Urbana Córdoba
> Cada entrada tiene: fecha/hora ▪ quién lo pidió ▪ qué se pidió ▪ qué se hizo ▪ por qué se tomó esa decisión

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
