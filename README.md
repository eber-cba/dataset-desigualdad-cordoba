# 🏙️ Desigualdad Urbana en Barrios de Córdoba

**Dataset integrado de indicadores socioeconómicos y de acceso a servicios públicos para los 494 barrios de la ciudad de Córdoba, Argentina.**

Proyecto de mentoría — [DiploDatos 2026](https://diplodatos.famaf.unc.edu.ar/) — FAMAF, Universidad Nacional de Córdoba.

---

## 📊 Dataset Principal

**Archivo:** [`data/processed/dataset_final_v6.csv`](data/processed/dataset_final_v6.csv)
**Registros:** 494 barrios | **Columnas:** 15

| Variable | Tipo | Descripción | Fuente |
|----------|------|-------------|--------|
| `barrio` | texto | Nombre oficial del barrio | [Datos Abiertos Municipalidad](https://gobiernoabierto.cordoba.gob.ar/data/datos-abiertos/categoria/territorio/barrios/33) |
| `poblacion` | entero | Población total del barrio | [Censo Nacional 2010 — INDEC](https://www.indec.gob.ar/indec/web/Nivel4-Tema-2-41-135) |
| `hogares` | entero | Cantidad de hogares | Censo 2010 |
| `nbi` | entero | Hogares con Necesidades Básicas Insatisfechas | Censo 2010 |
| `pct_nbi` | decimal | % hogares con NBI = `(nbi/hogares)*100` | Calculado |
| `escuelas_municipales` | entero | Escuelas primarias municipales (38 establ.) | [Datos Abiertos Municipalidad — Escuelas](https://gobiernoabierto.cordoba.gob.ar/data/datos-abiertos/categoria/educacion/escuelas-municipales/6) |
| `escuelas_total` | entero | Total establecimientos educativos (todos los niveles) | [IDECOR WFS — Establecimientos Educativos](https://idecor-ws.mapascordoba.gob.ar/geoserver/wfs) |
| `escuelas_estatales` | entero | Establecimientos del sector estatal | IDECOR WFS |
| `escuelas_privadas` | entero | Establecimientos del sector privado | IDECOR WFS |
| `centros_salud` | entero | Centros de salud y hospitales municipales | [Datos Abiertos Municipalidad — Salud](https://gobiernoabierto.cordoba.gob.ar/data/datos-abiertos/categoria/salud) |
| `paradas_colectivo` | entero | Paradas de transporte urbano | [GTFS Córdoba 2023 — Tamse/Municipalidad](https://gobiernoabierto.cordoba.gob.ar/data/datos-abiertos/categoria/transporte) |
| `lineas_colectivo` | entero | Líneas de colectivo distintas que pasan | GTFS Córdoba 2023 |
| `luminarias_reportes` | entero | Reportes de luminarias LED instaladas | [Datos Abiertos Municipalidad — Luminarias](https://gobiernoabierto.cordoba.gob.ar/data/datos-abiertos/categoria/servicios-publicos) |
| `comisarias` | entero | Comisarías de policía | [Datos Abiertos Municipalidad — Seguridad](https://gobiernoabierto.cordoba.gob.ar/data/datos-abiertos/categoria/seguridad) |
| `centros_vecinales` | entero | Centros vecinales y comisiones de vecinos | [Mapa Interactivo Córdoba — Centros Vecinales](https://mapascordoba.gob.ar/) |

### Asignación espacial

Cada servicio se asignó al barrio más cercano usando **KD-tree** con **560 centroides** extraídos del CSV censal original (columnas X/Y por barrio), complementados con centroides de centros de salud.

---

## 📁 Estructura del Proyecto

```
dataset_cordoba/
├── README.md                    # Este archivo
├── CHANGELOG.md                 # Historial detallado de cambios
├── requirements.txt             # Dependencias Python
├── .gitignore
│
├── data/
│   ├── raw/                     # Datos crudos (sin modificar)
│   │   ├── Barrios_de_Córdoba_con_información_censal_afkGL16.csv
│   │   ├── centros_salud_cordoba.csv
│   │   ├── centros_vecinales.csv
│   │   ├── comisarias_2023.csv
│   │   ├── escuelas_cordoba.csv
│   │   ├── escuelas_cordoba_wfs.geojson
│   │   ├── gtfs_cordoba.zip
│   │   ├── luminarias_led.csv
│   │   └── ZONAS_ESCUELAS_MUNICIPALES_Corregido_2.csv
│   │
│   └── processed/               # Datos procesados
│       ├── dataset_final_v6.csv          ← DATASET PRINCIPAL
│       ├── centroides_barrios_completo.csv
│       ├── barrios_cordoba_censal_limpio.csv
│       ├── centros_salud_limpio.csv
│       ├── centros_vecinales_limpio.csv
│       ├── escuelas_idecor_limpio.csv
│       └── paradas_colectivo_limpio.csv
│
├── scripts/                     # Scripts de procesamiento
│   ├── clean_dataset.py         # Limpieza del censal crudo → v1
│   ├── mejorar_escuelas.py      # Normalización de escuelas municipales
│   ├── procesar_salud.py        # Procesamiento centros de salud → v2
│   ├── integrador_dataset.py    # Integración GTFS/luminarias/comisarías → v4
│   ├── descargar_escuelas_wfs.py  # Descarga WFS IDECOR
│   ├── integrar_escuelas_idecor.py # Integración escuelas IDECOR → v5
│   ├── regenerar_dataset_v6.py  # Re-integración con 560 centroides → v6
│   ├── test_dataset.py          # Suite de 25 tests
│   └── archivo/                 # Scripts históricos (no usar)
│
└── notebooks/                   # Análisis para DiploDatos
    ├── 01_exploracion.ipynb      # EDA: distribución NBI, cobertura, correlaciones
    ├── 02_clustering.ipynb       # K-Means, PCA, perfiles de barrio
    └── 03_regresion.ipynb        # Modelos predictivos de NBI
```

---

## 🔄 Reproducir el Dataset

```bash
# Instalar dependencias
pip install -r requirements.txt

# Pipeline completo (ejecutar en orden)
python scripts/clean_dataset.py              # 1. Limpiar censal → v1
python scripts/mejorar_escuelas.py           # 2. Normalizar escuelas municipales
python scripts/procesar_salud.py             # 3. Procesar centros de salud → v2
python scripts/integrador_dataset.py         # 4. GTFS + luminarias + comisarías → v4
python scripts/descargar_escuelas_wfs.py     # 5. Descargar escuelas IDECOR (WFS)
python scripts/integrar_escuelas_idecor.py   # 6. Integrar escuelas IDECOR → v5
python scripts/regenerar_dataset_v6.py       # 7. Re-integrar todo con 560 centroides → v6
```

---

## 🧪 Tests

```bash
python scripts/test_dataset.py               # 25 validaciones
python -m pytest scripts/test_dataset.py -v   # Con output detallado
```

Valida: columnas, tipos, rangos, cobertura (≥100 barrios con escuelas), consistencia, centroides, retrocompatibilidad.

---

## 📓 Notebooks

| Notebook | Qué hace |
|----------|----------|
| [`01_exploracion.ipynb`](notebooks/01_exploracion.ipynb) | Distribución NBI, cobertura de servicios, correlaciones, scatter escuelas vs pobreza |
| [`02_clustering.ipynb`](notebooks/02_clustering.ipynb) | K-Means con método del codo, Silhouette, PCA 2D, perfiles de cluster |
| [`03_regresion.ipynb`](notebooks/03_regresion.ipynb) | Comparativa de 4 modelos (Linear, Ridge, RF, GBR), importancia de variables |

---

## 📋 Fuentes de Datos

| Dataset | Fuente | URL |
|---------|--------|-----|
| Barrios + Censo 2010 | Datos Abiertos Municipalidad de Córdoba | [gobiernoabierto.cordoba.gob.ar](https://gobiernoabierto.cordoba.gob.ar/) |
| Escuelas (5,471 establ.) | IDECOR — Infraestructura de Datos Espaciales de Córdoba | [mapascordoba.gob.ar](https://mapascordoba.gob.ar/viewer/mapa/77) |
| Centros de salud | Datos Abiertos Municipalidad | [gobiernoabierto.cordoba.gob.ar](https://gobiernoabierto.cordoba.gob.ar/) |
| Transporte (GTFS) | Tamse / Municipalidad de Córdoba | [gobiernoabierto.cordoba.gob.ar](https://gobiernoabierto.cordoba.gob.ar/) |
| Luminarias LED | Datos Abiertos Municipalidad | [gobiernoabierto.cordoba.gob.ar](https://gobiernoabierto.cordoba.gob.ar/) |
| Comisarías | Datos Abiertos Municipalidad | [gobiernoabierto.cordoba.gob.ar](https://gobiernoabierto.cordoba.gob.ar/) |
| Centros vecinales (376) | Mapa Interactivo de Córdoba (KMZ) | [mapascordoba.gob.ar](https://mapascordoba.gob.ar/) |

---

## 👤 Autor

**Eber Coronel** — Mentor DiploDatos 2026 — FAMAF/UNC

---

## 📄 Licencia

Datos públicos del Gobierno de la Ciudad de Córdoba e IDECOR. Uso académico.
