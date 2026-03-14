# 📋 GUÍA DEL PROYECTO — DiploDatos 2026
## Análisis de Desigualdad Urbana en Barrios de Córdoba
*Última actualización: 14/03/2026 — Actualizar este archivo cada vez que avancés*

---

## 🎯 Objetivo del proyecto

Construir un dataset que permita analizar **desigualdades urbanas** entre barrios de Córdoba usando datos públicos.

Los alumnos van a poder responder preguntas como:
- ¿Qué barrios tienen mayor pobreza y menor acceso a servicios?
- ¿Hay relación entre nivel de NBI, población y cantidad de escuelas?
- ¿Se pueden agrupar barrios por perfil socioeconómico? (clustering)

---

## ✅ LO QUE HICISTE HASTA AHORA

### Paso 1 — Conseguir barrios de Córdoba ✅
- **Fuente:** Portal de datos abiertos de la Municipalidad de Córdoba
- **Archivo original:** `Barrio_1.kmz` (formato de mapa)
- **Lo que hiciste:** Convertiste el KMZ a CSV usando una herramienta online (mapshaper.org)
- **Por qué:** Para poder trabajar con los datos como tabla en lugar de mapa

### Paso 2 — Limpiar el dataset de barrios (geográfico) ✅
- **Script:** `scripts/clean_dataset.py`
- **Archivo entrada:** CSV generado desde KMZ
- **Lo que hiciste:** Eliminaste columnas técnicas del mapa, renombraste columnas, filtraste barrios `SD` y duplicados
- **Por qué:** Para tener una tabla limpia donde cada fila sea un barrio real

### Paso 3 — Agregar datos censales (población, hogares, NBI) ✅
- **Fuente:** Portal de datos abiertos — dataset censal de barrios
- **Archivo raw:** `data/raw/Barrios_de_Córdoba_con_información_censal_afkGL16.csv`
- **Archivo salida:** `data/processed/barrios_cordoba_censal_limpio.csv`
- **Resultado:** **496 barrios** con datos de población, hogares y NBI

### Paso 7 — Descarga de establecimientos educativos desde WFS de IDECOR ✅ (14/03/2026)
- **Fuente:** IDECOR — MapasCórdoba, servidor WFS `idecor-ws.mapascordoba.gob.ar`
- **Mapa original:** https://mapascordoba.gob.ar/viewer/mapa/77
- **Script de descarga:** `scripts/descargar_escuelas_wfs.py` (descubrimiento automático de endpoint WFS)
- **Script de integración:** `scripts/integrar_escuelas_idecor.py`
- **Archivo raw:** `data/raw/escuelas_cordoba.csv` (5,471 establecimientos)
- **Archivo procesado:** `data/processed/escuelas_idecor_limpio.csv` (filtrado a ciudad de Córdoba Capital)
- **Resultado:** 3 columnas nuevas en el dataset: `escuelas_total`, `escuelas_estatales`, `escuelas_privadas`
- **Tests:** `scripts/test_dataset.py` — **22/22 tests OK**
- **Dataset final:** `data/processed/dataset_final_v5.csv` (15 columnas)

### Paso 5 — Análisis de prioridad ✅
- **Script:** `scripts/analisis_prioridad.py`
- **Archivo salida:** `salida_analisis.txt`
- **Resultado:** Ranking de barrios con mayor urgencia (alta población + alto NBI + sin escuelas registradas)

### Paso 6 — Columna pct_nbi calculada ✅ (14/03/2026)
- **Script:** `scripts/mejorar_escuelas.py`
- **Fórmula:** `pct_nbi = round((nbi / hogares) * 100, 1)`
- **Por qué:** El NBI absoluto no permite comparar barrios de distinto tamaño. El porcentaje sí.

---

## 📂 ESTRUCTURA DE ARCHIVOS ACTUAL

```
dataset_cordoba/
├── data/
│   ├── raw/                              → Datos originales sin modificar
│   │   ├── Barrios_de_Córdoba_con_información_censal_afkGL16.csv
│   │   └── ZONAS_ESCUELAS_MUNICIPALES_Corregido_2.csv
│   └── processed/                        → Datos ya procesados/limpios
│       ├── barrios_cordoba_censal_limpio.csv    ← Dataset principal
│       ├── escuelas_cordoba_primarias_limpio.csv
│       ├── escuelas_por_barrio.csv
│       └── dataset_educacion_barrios_cordoba.csv  ← Dataset combinado actual
├── scripts/
│   ├── clean_dataset.py
│   ├── limpiar_escuelas.py
│   ├── agrupar_escuelas.py
│   ├── normalizar_y_unir.py
│   ├── unir_datasets.py
│   └── analisis_prioridad.py
└── salida_analisis.txt
```

---

## 📊 VARIABLES DEL DATASET — QUÉ SIGNIFICA CADA UNA

### Archivo principal: `barrios_cordoba_censal_limpio.csv`

| Variable | Tipo | Qué significa | Ejemplo |
|----------|------|---------------|---------|
| `barrio` | texto | Nombre del barrio | ALBERDI |
| `poblacion` | número | Personas que viven en el barrio (Censo 2010) | 32,729 |
| `hogares` | número | Cantidad de hogares (familias/viviendas) | 15,505 |
| `nbi` | número | Hogares con Necesidades Básicas Insatisfechas | 858 |

#### ¿Qué es NBI?
Es un indicador que cuenta los hogares que tienen al menos UNO de estos problemas:
- Vivienda inadecuada (rancho, casilla, pieza en inquilinato)
- Hacinamiento (más de 3 personas por cuarto)
- Sin baño con descarga de agua
- Sin ningún miembro con educación primaria completa
- Niños de 6 a 12 años que no van a la escuela

**Número alto de NBI = más pobreza estructural en ese barrio**

> ⚠️ **Dato clave:** NBI cuenta **hogares**, no personas. Para comparar barrios de distinto tamaño conviene calcular: `porcentaje_nbi = (nbi / hogares) * 100`

### Archivo combinado: `dataset_educacion_barrios_cordoba.csv`

Tiene las mismas columnas del censal + una columna extra:

| Variable | Qué significa |
|----------|---------------|
| `escuelas` | Cantidad de escuelas **municipales** detectadas en el barrio (¡ver problema!) |

---

## 🐛 PROBLEMAS ENCONTRADOS EN LOS DATOS

### ✅ Problema 1 — Matching de escuelas (RESUELTO 14/03/2026)
**Qué pasaba:** Los nombres de barrio en el dataset de escuelas usaban abreviaturas (`Vª AZALAIS`, `STA ISABEL`, `JOSE I. DIAZ III`) que no coindicían con el dataset censal (`VILLA AZALAIS`, `SANTA ISABEL SECCION 1`, `JOSE IGNACIO DIAZ SECCION 3`).

**Cómo se resolvió:** Script `mejorar_escuelas.py` con:
1. Función de normalización de abreviaturas (regex)
2. Diccionario de mapping manual para los 21 casos problemáticos
3. Elimina la fila `SIN BARRIO` que no es un barrio real

**Resultado:** 34 barrios con al menos 1 escuela municipal. El dataset de escuelas es solo **escuelas municipales** (38 en total en Córdoba). Los barrios con 0 escuelas pueden tener escuelas nacionales o provinciales que no están en este dataset → es una **limitación documentada** del proyecto.

**Archivo corregido:** `data/processed/dataset_final_v2.csv`

### ⚠️ Problema 2 — Barrios con datos vacíos
Algunos barrios tienen `poblacion`, `hogares` y `nbi` vacíos. Ejemplos:
- ROCIO DEL SUR, PARQUE SARMIENTO, GUARNICION AEREA CORDOBA
- CIUDAD UNIVERSITARIA, LOS CIELOS, LOS ARBOLES

**Por qué:** Son barrios nuevos o zonas sin registro censal 2010.
**¿Qué hacer?** Mantenerlos pero dejar los valores vacíos (NaN) — los scripts de ML los pueden manejar.

### ⚠️ Problema 3 — Fila "SIN BARRIO"
Hay una fila con ese nombre: 18,570 personas y NBI = 982. Son personas sin barrio asignado en el censo. **No es un barrio real.** Hay que eliminarla del dataset final.

---

## ❌ LO QUE FALTA HACER

### 🔴 Prioritario — Mejorar el dataset de escuelas
El dataset actual solo tiene 37 escuelas. Para el proyecto necesitamos más.

**Opción A (recomendada):** Descargar dataset completo de establecimientos educativos
- URL: https://gobiernoabierto.cordoba.gob.ar/data/datos-abiertos
- Buscar: "establecimientos educativos" o "escuelas"

**Opción B:** Usar datos del Ministerio de Educación nacional
- URL: https://datos.gob.ar/dataset/educacion-establecimientos-educativos

### 🔴 Prioritario — Calcular `porcentaje_nbi`
Agregar columna: `porcentaje_nbi = round((nbi / hogares) * 100, 1)`

### 🟡 Importante — Agregar centros de salud
- URL: https://gobiernoabierto.cordoba.gob.ar/data/datos-abiertos
- Buscar: "centros de salud" o "dispensarios"

### 🟡 Importante — Agregar datos de transporte
- Paradas de colectivo por barrio
- URL: https://gobiernoabierto.cordoba.gob.ar/data/datos-abiertos/categoria/movilidad

### 🟢 Opcional — Agregar coordenadas (lat/lon)
Volver a cruzar con el dataset geográfico KMZ para agregar `latitud` y `longitud` al dataset final. Permite hacer mapas de calor.

### 🟢 Opcional — Agregar espacios verdes / plazas
Del portal de datos abiertos.

---

## ✅ VERIFICACIÓN DE DATOS — CHEQUEOS REALIZADOS

| Chequeo | Estado | Resultado |
|---------|--------|-----------|
| ¿Cada fila es un barrio único? | ✅ OK | Sí |
| ¿Los barrios "SD" fueron eliminados? | ✅ OK | Sí |
| ¿La fila "SIN BARRIO" fue eliminada? | ⚠️ Pendiente | Todavía existe en el archivo |
| ¿Escuela ALICIA MOREAU está en Villa El Libertador? | ✅ Verificado | Sí — Pilcomayo 5100, Villa El Libertador ✓ |
| ¿Escuela BRIG. SAN MARTIN está en José Hernández? | ✅ Verificado | Sí — Trenque Lauquen 3200 ✓ |
| ¿NBI de Alberdi (858/15505 hogares = 5.5%) es razonable? | ✅ OK | Sí, zona comercial céntrica, NBI bajo esperable |
| ¿NBI de Villa El Libertador (1048/7541 = 13.9%) es razonable? | ✅ OK | Sí, barrio popular periférico, NBI alto esperable |
| ¿NBI de Nuestro Hogar II (33/209 = 15.8%) es razonable? | ✅ OK | Sí, barrio periférico con vulnerabilidad ✓ |
| ¿Escuelas detectadas son correctas para los barrios que tienen? | ✅ OK | Los 37 registros verificados están correctos geográficamente |

---

## 📈 ESTADO ACTUAL DEL DATASET

| Dimensión | Valor actual | Objetivo para mentoría |
|-----------|-------------|------------------------|
| Barrios en dataset | **494** (SIN BARRIO eliminado) | OK |
| Columnas | **15** (v5) | OK |
| Escuelas (municipales, histórico) | 34 barrios — 38 establecimientos | OK (fuente original mantenida) |
| **Escuelas total (IDECOR WFS 2026)** | **≥ 50 barrios** | ✅ Nuevo — supera objetivo |
| **Escuelas estatales (IDECOR)** | **≥ 40 barrios** | ✅ Nuevo |
| **Escuelas privadas (IDECOR)** | **≥ 30 barrios** | ✅ Nuevo |
| Columna pct_nbi | ✅ Calculada | OK |
| Centros de salud | ✅ 90 barrios | OK |
| Transporte (GTFS) | ✅ 90 barrios | OK |
| Luminarias | ✅ 323 barrios | OK |
| Tests automáticos | **✅ 22/22 tests OK** | ✅ Nuevo |

---

## 🔗 FUENTES DE DATOS

### Usadas
| Dataset | URL |
|---------|-----|
| Barrios con datos censales | https://gobiernoabierto.cordoba.gob.ar/data/datos-abiertos |
| Escuelas municipales (parcial) | https://gobiernoabierto.cordoba.gob.ar/data/datos-abiertos |
| Barrios KMZ geográfico | https://gobiernoabierto.cordoba.gob.ar/data/datos-abiertos/categoria/territorio |

### Pendientes de explorar (URLs verificadas ✅)
| Dataset | URL | Formato |
|---------|-----|---------|
| Escuelas municipales completo (2024) | https://gobiernoabierto.cordoba.gob.ar/data/datos-abiertos/categoria/escuelas-primarias-municipales/listado-de-escuelas/262 | XLSX |
| Centros de salud / dispensarios municipales | https://gobiernoabierto.cordoba.gob.ar/data/datos-abiertos/categoria/geografia-y-mapas/centros-de-salud/3 | KMZ (descargar desde Google My Maps → tres puntitos → Descargar KML) |
| Paradas de transporte urbano | https://gobiernoabierto.cordoba.gob.ar/data/datos-abiertos/categoria/transporte-urbano/paradas-de-transporte-urbano/3320 | KML (2022) |
| Datos educativos nacionales | https://datos.gob.ar/dataset/educacion-establecimientos-educativos | CSV |

---

## 📝 LOG DE CAMBIOS

| Fecha | Qué hice |
|-------|----------|
| ~Mar 11 | Convertí KMZ de barrios a CSV |
| ~Mar 11 | Limpié dataset geográfico de barrios |
| ~Mar 13 | Agregué datos censales (poblacion, hogares, NBI) |
| ~Mar 13 | Procesé dataset de 37 escuelas municipales |
| ~Mar 13 | Uní escuelas con dataset censal |
| ~Mar 13 | Hice análisis de prioridad por barrio |
| 14/03/2026 00:01 | Creé GUIA_PROYECTO.md con auditoría completa del proyecto |
| **14/03/2026 02:10** | **[CORRECCIÓN ESCUELAS]** Script `mejorar_escuelas.py` — 34 barrios con escuelas, pct_nbi, `dataset_final_v2.csv` |
| **14/03/2026 03:18** | **[v0.6]** Transporte GTFS, luminarias, comisarías, centros vecinales → `dataset_final_v4.csv` (12 cols) |
| **14/03/2026 15:25** | **[v0.7]** WFS IDECOR: 5,471 establecimientos educativos → 3 columnas nuevas → `dataset_final_v5.csv` (15 cols). 22 tests OK. Docs actualizadas. Git push. |
