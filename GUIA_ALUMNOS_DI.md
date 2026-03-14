# 🎓 Guía Didáctica: Proyecto Desigualdad Urbana en Córdoba

¡Bienvenidos y bienvenidas al proyecto del **Dataset de Desigualdad Urbana en Córdoba**! 

Si estás leyendo esto, es porque vas a trabajar con este repositorio durante la **DiploDatos**. Como futuros profesionales de los datos, es clave entender no solo *cómo* se corre el código, sino **el porqué detrás de cada decisión** que tomamos para armar estos datos.

Esta guía está diseñada para que entiendan la arquitectura del proyecto, qué hace cada script y qué historias podemos contar ("mostrar") usando este dataset.

---

## 🏗️ 1. Arquitectura y Filosofía del Proyecto

### ¿Qué problema intentamos resolver?
El problema principal era que los datos públicos de Córdoba estaban **dispersos**. Teníamos el Censo de 2010 por un lado (NBI, población), los lugares donde se instalaron luminarias LED por otro, la educación en IDECOR y los colectivos en un formato técnico de Google (GTFS). 

### ¿Cuál fue la solución?
Construir un **Pipeline de Datos Modular**. En lugar de armar el dataset a mano en Excel o tener un único script caótico de 2000 líneas de código, creamos **scripts independientes**. Cada script tiene un único trabajo (ej. bajar los datos de educación) y un script final (`regenerar_dataset_v6.py`) actúa de "pegamento" reuniendo todo usando análisis geoespacial.

Esto se hizo por tres razones:
1. **Reproducibilidad:** Cualquiera de ustedes puede bajar el código y llegar a los mismos datos.
2. **Mantenibilidad:** Si mañana la Municipalidad actualiza el archivo de comisarías, solo reemplazan ese `.csv` en la carpeta `data/raw/` y vuelven a correr el pipeline.
3. **Escalabilidad:** Si quieren agregar centros deportivos, solo escriben un script extra; no necesitan alterar el resto.

---

## ⚙️ 2. ¿Qué hace cada script y por qué lo hace?

El flujo de trabajo empieza siempre en la carpeta `data/raw/` (los datos puros bajados de internet) y termina en `data/processed/` (los datos listos para el modelo de Machine Learning).

### A. Limpieza Base
- `clean_dataset.py`: Toma el Censo en bruto, elimina columnas espaciales basura que no se van a usar (como el polígono del barrio) y deja una base limpia de 495 barrios con Población, Hogares y el NBI (Necesidades Básicas Insatisfechas).

### B. Procesadores Específicos
- `mejorar_escuelas.py`: Limpia los nombres de las escuelas municipales (que a veces venían con errores de tipeo).
- `procesar_salud.py`: Carga latitud/longitud de hospitales y centros de salud municipales.
- `descargar_escuelas_wfs.py`: Se conecta a un servidor de mapas real (IDECOR) para descargar el polígono completo de *todas* las escuelas de Córdoba (estatales y privadas).
- `integrar_escuelas_idecor.py`: Filtra esas escuelas bajadas para quedarse solo con las de Córdoba Capital en un formato tabular limpio.

### C. El Integrador Final: La Joya de la Corona
- **`regenerar_dataset_v6.py`**: Este script es el corazón del proyecto. Hace lo que se conoce como **"Spatial Join" por KD-Tree**.
  * **¿Qué es eso?** El Censo nos da 560 "puntos" (centroides) en el mapa que representan los 494 barrios. El transporte, las clínicas, etc., vienen como puntos sueltos en un mapa (GPS). El script usa un algoritmo complejo (KD-Tree de la librería Scipy) para medir la distancia de cada escuela, cada parada de colectivo y cada luminaria contra esos 560 centroides, y dice *"Ah, esta parada de colectivo está a 10 metros del centroide del Barrio Alberdi. Se la sumo a Alberdi"*.
  * Finalmente, exporta el archivo `dataset_final_v6.csv`, que es el que ustedes van a consumir.

### D. Tests: Asegurando la Calidad
- `test_dataset.py`: Son 25 pruebas automatizadas usando `unittest`. **¿Por qué esto es vital en un proyecto real?** Imaginen que corren el pipeline y por un error humano borran a la mitad de los barrios de Córdoba. Estos tests validan automáticamente, en milisegundos, que los 495 barrios estén, que la columna `pct_nbi` sea de tipo número y no texto, y que no haya duplicados.

---

## 📊 3. ¿Qué podemos MOSTRAR con este dataset?

El repositorio incluye la carpeta `/notebooks` con 3 libretas Jupyter. Estos son los "productos" o conclusiones de nuestro trabajo de ingeniería de datos. Ustedes pueden mostrar tres narrativas muy fuertes:

### A. Exploración Urbana (`01_exploracion.ipynb`)
- **Lo que muestra:** Muestra los "básicos". Pueden crear un gráfico que revele la distribución matemática de la pobreza (NBI) en Córdoba y su correlación con la falta de servicios. 
- **La historia:** ¿Los barrios con más pobreza son, estadísticamente, los mismos barrios donde hay menos iluminación LED o menos escuelas cerca? El *heatmap* (mapa de calor) de correlación responde eso matemáticamente.

### B. Segmentación / Clustering (`02_clustering.ipynb`)
- **Lo que muestra:** Aplica Machine Learning No Supervisado (K-Means) para agrupar los 495 barrios en 5 "Perfiles Socioeconómicos". Usa PCA para comprimir los datos y mostrarlos en un gráfico 2D.
- **La historia:** Pueden mostrarle al público que Córdoba no se divide geográficamente norte/sur de manera simple, sino que hay "Clústers" estadísticos (ej. el Clúster de zonas acomodadas con acceso pleno vs. el Clúster de barrios periféricos sin escuelas o transporte). 

### C. Predicción de Privaciones (`03_regresion.ipynb`)
- **Lo que muestra:** Compara algoritmos avanzados (Random Forest, Gradient Boosting) y algoritmos básicos (Linear Regression) para intentar predecir el impacto en el NBI de un barrio. Muestra una gráfica de "Importancia de Variables" (Feature Importance).
- **La historia:** Este es el gráfico más valioso para políticas públicas. Le pueden decir al público: *"Nuestro modelo de Machine Learning determinó que la falta de escuelas totales en un radio cercano es el factor número uno asociado a un alto índice NBI, seguido por la desconexión del transporte público (GTFS)"*.

---

¡Exitos en su análisis! El código duro de limpiar la basura ya está hecho; su trabajo ahora es hacer que estos datos hablen.
