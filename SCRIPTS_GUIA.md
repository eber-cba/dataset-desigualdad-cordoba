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

## 7. `procesar_salud.py` 🔜 (POR CREAR)

### ¿Qué hará?
Procesará el dataset de centros de salud municipales de Córdoba, contará cuántos quedan dentro de cada barrio y unirá con `dataset_final_v2.csv`.

### Lógica plannificada
```
Entrada:  data/raw/centros_salud_cordoba.csv (o KML convertido)
          data/processed/dataset_final_v2.csv

Proceso:
  → Normalizar nombres de barrio (igual que mejorar_escuelas.py)
  → Contar centros de salud por barrio
  → LEFT JOIN con dataset_final_v2
  → Generar dataset_final_v3.csv

Salida:   data/processed/dataset_final_v3.csv
          (+ columna centros_salud)
```

---

## 🗂️ Flujo completo de datos

```
FUENTES RAW
  │
  ├── Barrios_censal.csv
  │       └── clean_dataset.py
  │               └── barrios_cordoba_censal_limpio.csv
  │                                   │
  ├── ZONAS_ESCUELAS.csv              │
  │       └── mejorar_escuelas.py ────┤
  │               └── dataset_final_v2.csv
  │                                   │
  └── centros_salud.csv (pendiente)   │
          └── procesar_salud.py ──────┘
                  └── dataset_final_v3.csv  ← DATASET FINAL
```
