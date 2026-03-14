# 🏙️ Dataset: Desigualdad Urbana en Barrios de Córdoba
### Proyecto de Mentoría — DiploDatos 2026 (FAMAF / UNC)

---

## ¿De qué trata este proyecto?

Este repositorio contiene el dataset y los scripts para construir un conjunto de datos sobre **desigualdad urbana** en los barrios de la ciudad de Córdoba, Argentina.

El objetivo es que estudiantes de la Diplomatura en Ciencia de Datos puedan:
- Explorar patrones de desigualdad entre barrios
- Construir indicadores de vulnerabilidad urbana
- Aplicar clustering (aprendizaje no supervisado)
- Construir modelos predictivos sobre acceso a servicios

---

## 📂 Estructura del repositorio

```
dataset_cordoba/
├── data/
│   ├── raw/           → Archivos originales descargados tal cual de las fuentes
│   └── processed/     → Archivos procesados y listos para usar
├── scripts/           → Scripts Python para procesar los datos
├── README.md          → Este archivo
├── CHANGELOG.md       → Historial de cambios con fecha/hora/pedido/decisión
├── SCRIPTS_GUIA.md    → Guía detallada de qué hace cada script y por qué
└── GUIA_PROYECTO.md   → Guía de estado del proyecto, variables y pendientes
```

---

## 📊 Dataset principal

**Archivo:** `data/processed/dataset_final_v5.csv` *(versión actual)*
**Registros:** 494 barrios de la ciudad de Córdoba

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `barrio` | texto | Nombre del barrio oficial de Córdoba |
| `poblacion` | número | Personas residentes (Censo Nacional 2010) |
| `hogares` | número | Cantidad de hogares en el barrio |
| `nbi` | número | Hogares con Necesidades Básicas Insatisfechas |
| `pct_nbi` | decimal | % hogares con NBI = `(nbi/hogares)*100` |
| `escuelas_total` | entero | **NUEVO** — Total de establecimientos educativos asignados al barrio (todos los niveles, estatal + privado). Fuente: IDECOR WFS 2026 |
| `escuelas_estatales` | entero | **NUEVO** — Solo establecimientos del sector estatal (públicos) |
| `escuelas_privadas` | entero | **NUEVO** — Solo establecimientos del sector privado |
| `escuelas_municipales` | entero | Escuelas primarias municipales históricas (38 establecimientos, fuente original) |
| `centros_salud` | entero | Centros de salud y hospitales municipales |
| `paradas_colectivo` | entero | Paradas de transporte urbano (GTFS 2023) |
| `lineas_colectivo` | entero | Líneas de colectivo distintas por barrio |
| `luminarias_reportes` | entero | Reportes de luminarias LED (proxy de cobertura eléctrica) |
| `comisarias` | entero | Comisarías, subcomisarías y unidades judiciales |
| `centros_vecinales` | entero | Centros vecinales (pendiente de mejorar) |

---

## 🔍 Fuentes de datos

| Dataset | Fuente | Detalle |
|---------|--------|---------|
| Barrios con datos censales | Portal Datos Abiertos Córdoba | Censo 2010, nivel barrio |
| Escuelas municipales | Portal Datos Abiertos Córdoba | 38 escuelas primarias municipales |
| **Establecimientos educativos** | **IDECOR — MapasCórdoba WFS** | **5,471 establecimientos. Endpoint: `idecor-ws.mapascordoba.gob.ar`. Mapa: https://mapascordoba.gob.ar/viewer/mapa/77** |
| Centros de salud | Portal Datos Abiertos Córdoba | Centros de salud y hospitales municipales |
| Transporte urbano | GTFS Córdoba 2023 | Paradas y líneas de colectivo |
| Luminarias LED | Datos abiertos municipales | Reportes de luminarias en la ciudad |
| Comisarías 2023 | Datos abiertos provinciales | Comisarías, subcomisarías, UJ |

---

## ⚙️ Cómo reproducir el dataset

```bash
# 1. Limpiar dataset censal
python scripts/clean_dataset.py

# 2. Procesar escuelas municipales históricas → v2
python scripts/mejorar_escuelas.py

# 3. Agregar centros de salud → v3
python scripts/procesar_salud.py

# 4. Agregar transporte, luminarias, comisarías → v4
python scripts/integrador_dataset.py

# 5. Descargar establecimientos educativos IDECOR vía WFS
python scripts/descargar_escuelas_wfs.py

# 6. Integrar establecimientos IDECOR → v5  ← VERSIÓN ACTUAL
python scripts/integrar_escuelas_idecor.py
```

---

## 🧪 Tests automáticos

```bash
# Correr suite completa (22 validaciones)
python scripts/test_dataset.py

# Con pytest para output detallado
python -m pytest scripts/test_dataset.py -v
```

Los tests validan: columnas requeridas, tipos, rango de `pct_nbi`, cobertura de escuelas, consistencia entre columnas, sin valores negativos y retrocompatibilidad con v4.

---

## 📝 Preguntas de investigación (para los alumnos)

1. ¿Qué barrios presentan mayor vulnerabilidad social según NBI?
2. ¿Existe relación entre el nivel de NBI y el acceso a escuelas o centros de salud?
3. ¿Se pueden agrupar barrios con características similares? *(clustering)*
4. ¿Qué variables predicen mejor el nivel de NBI de un barrio?
5. ¿Hay diferencias en el acceso a establecimientos **públicos vs privados** entre barrios de distinto nivel socioeconómico?

---

## ✍️ Mentor

**Eber Coronel** — Docente Full Stack con +5 años de experiencia acompañando más de 500 estudiantes en proyectos de tecnología y datos.

---

*Mentoría presentada para DiploDatos 2026 — FAMAF, Universidad Nacional de Córdoba*
