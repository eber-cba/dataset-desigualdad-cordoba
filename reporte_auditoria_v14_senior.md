# 📊 Informe Técnico de Auditoría: Urban Data Science Pipeline

**Fecha:** 14/03/2026
**Auditor:** Senior Data Scientist & GIS Specialist  
**Evaluación Base:** Pipeline V14

---

## 1. 🚨 Errores Críticos Detectados (Data Logic Flaws)

Durante la inspección algorítmica y de los reportes V14, se detectaron brechas metodológicas que comprometen la pureza estadística del dataset:

1. **Destrucción de Referencia Espacial (Clipping Ciego):**
   - **El Error:** El iterador de Data Quality realiza un `clip(lower=0)` general sobre todas las variables numéricas que presentan valores negativos.
   - **El Efecto:** Las columnas `centroide_lat` y `centroide_lon` albergan coordenadas en Argentina (Típicamente `-31` y `-64`). Al aplicar el clipping genérico, estas coordenadas se reescriben a `0` (Golfo de Guinea, cerca de África), quebrando por defecto la compatibilidad estricta con GIS.

2. **Multicolinealidad y Double-Dipping en K-Means (Data Leakage):**
   - **El Error:** Se está inyectando a la matriz del algoritmo K-Means las variables `infraestructura_score`, junto con `escuelas_por_1000_hab` y `paradas_por_1000_hab`.
   - **El Efecto:** Puesto que `infraestructura_score` es un índice compuesto que ya modela matemáticamente a escuelas y paradas de colectivo, el algoritmo K-Means penaliza/premia doblemente a los barrios de forma artificial (redundancia). 

3. **Inconsistencias Lógicas Terminales (Población Base):**
   - **El Error:** Existe el truncamiento si `hogares > poblacion`, pero omite el caso donde algún barrio censado pudiese tener una población nula pero valores residuales de hogares distintos de cero.

4. **Sesgo por Imputación de Mediana (Median Bias):**
   - **El Error:** La imputación masiva por Mediana sobre variables faltantes reduce artificialmente la varianza, empaquetando muchos barrios en agrupamientos falsos en el espacio Z. 

---

## 2. 🛠️ Soluciones y Correcciones Recomendadas

Para erigir el **Pipeline V15 (Nivel 10/10 Académico e Industrial)**, ejecutaré las siguientes correciones:

1. **Sanity Check Geográfico (Bounding Box):**
   - Se excluirán dinámicamente las variables que contengan `_lat`, `_lon` o `geometry` del loop de imputación/capping general.
   - Se aplicará un filtro de coherencia "Bounding Box" exclusivo para la Provincia de Córdoba:  
     - `Latitud válida: -32.5 a -31.0`  
     - `Longitud válida: -64.5 a -63.5`
   - Si un coordenada recae fuera, se reporta y se imputa por Mediana Espacial o se excluye si es Outlier severo.

2. **Supresión de Redundancias en Clustering:**
   - Para el K-Means se usará un Feature Set ortogonal: `['poblacion_log', 'pct_nbi', 'infraestructura_score', 'densidad_poblacional']`. Esto previene que la "infraestructura" dicte el modelo 2 veces.

3. **Control Denominador de Densidad:**
   - La densidad solo se computará si `area_barrio_km2 > 0`. Si el área es 0 o NaN, se mantendrá en `NaN` en lugar de disparar Infs para luego imputarlo. La imputación sobre la densidad se hará con el `median()` poblacional, cuidando de reportar el % imputado.

---

## 3. 🚀 Evolución a Arquitectura V15 (Nivel Profesional 10/10)

Para dejar el pipeline impecable, el nuevo script V15 implementará:
- **Exclusión Consciente de Variables Contextuales:** El Data Quality loop preguntará por metadatos (ej. si la variable indica espacio, omitir recortes).
- **Interpretador PCA / Silhoutte:** Documentación automática de si la colinealidad fue suprimida.
- **Data Dictionary Extendido:** Marcando explícitamente qué variables son "Features Derivadas" (Targets de ML) versus "Features Primitivas".

El script Python será sobreescrito como `regenerar_dataset_v15.py` e integrado al proyecto.
