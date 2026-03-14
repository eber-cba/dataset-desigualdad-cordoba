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

**Archivo:** `data/processed/dataset_final_v2.csv` *(versión actual)*

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `barrio` | texto | Nombre del barrio oficial de Córdoba |
| `poblacion` | número | Personas residentes (Censo Nacional 2010) |
| `hogares` | número | Cantidad de hogares en el barrio |
| `nbi` | número | Hogares con Necesidades Básicas Insatisfechas |
| `pct_nbi` | decimal | Porcentaje de hogares con NBI = `(nbi/hogares)*100` |
| `escuelas_municipales` | entero | Escuelas primarias municipales en el barrio |

**Registros:** ~494 barrios de la ciudad de Córdoba

---

## 🔍 Fuentes de datos

| Dataset | Fuente | URL |
|---------|--------|-----|
| Barrios con datos censales | Portal Datos Abiertos Córdoba | https://gobiernoabierto.cordoba.gob.ar/data/datos-abiertos |
| Escuelas municipales | Portal Datos Abiertos Córdoba | https://gobiernoabierto.cordoba.gob.ar/data/datos-abiertos/categoria/escuelas-primarias-municipales/listado-de-escuelas/262 |
| Centros de salud | Portal Datos Abiertos Córdoba | https://gobiernoabierto.cordoba.gob.ar/data/datos-abiertos/categoria/geografia-y-mapas/centros-de-salud/3 |

---

## ⚙️ Cómo reproducir el dataset

```bash
# 1. Limpiar dataset censal
python scripts/clean_dataset.py

# 2. Procesar y unir escuelas con matching corregido
python scripts/mejorar_escuelas.py

# 3. (cuando esté listo) Agregar centros de salud
python scripts/procesar_salud.py
```

---

## 📝 Preguntas de investigación (para los alumnos)

1. ¿Qué barrios presentan mayor vulnerabilidad social según NBI?
2. ¿Existe relación entre el nivel de NBI y el acceso a escuelas o centros de salud?
3. ¿Se pueden agrupar barrios con características similares? *(clustering)*
4. ¿Qué variables predicen mejor el nivel de NBI de un barrio?

---

## ✍️ Mentor

**Eber Coronel** — Docente Full Stack con +5 años de experiencia acompañando más de 500 estudiantes en proyectos de tecnología y datos.

---

*Mentoría presentada para DiploDatos 2026 — FAMAF, Universidad Nacional de Córdoba*
