# 📖 Diccionario de Datos

Este documento describe el esquema de nuestro archivo entregable principal (`dataset_ml_v19.csv` o similar) con el que van a ejecutar los algoritmos. A continuación el detalle de las variables:

### 🏙️ Identificadores y Jerarquía
* **`barrio`** (`string`): Nombre oficial del barrio de acuerdo a la cartografía de la Municipalidad de Córdoba.
* (Otros posibles IDs espaciales o de radio censal, usados internamente).

### 👥 Datos Demográficos Base
* **`poblacion`** (`integer`): Cantidad total aproximada de habitantes en el barrio.
* **`hogares`** (`integer`): Cantidad de viviendas individuales registradas.

### 📉 Target Predictivo (Variable a Predecir)
* **`nbi` o `pct_nbi`** (`float`): Porcentaje de **Necesidades Básicas Insatisfechas**. Esta es nuestra variable objetivo ("Target") en modelos supervisados. Un valor de `0.15` indica que el 15% de las viviendas de ese barrio tiene privaciones críticas (desde hacinamiento hasta falta de cloacas).

### 🏫 Infraestructura Urbana (Features Espaciales)
*Estas propiedades fueron calculadas mediante intersecciones geométricas. Representan "lo que hay" dentro del barrio o muy cerca de él.*

* **`escuelas_radio_1km`** (`integer`): Establecimientos educativos (públicos/privados) en la cercanía del barrio.
* **`dispensarios`** (`integer`): Centros de atención de salud pública.
* **`paradas_movibus`** (`integer`): Infraestructura de transporte urbano de colectivos (líneas frecuentes).
* **`iluminacion_led` / `densidad_luces`** (`float` o `integer`): Métrica que mide la modernización del alumbrado público en el polígono.

### 🤖 Variables Generadas (Outputs de Machine Learning)
* **`cluster_id`** (`integer`): *Esta columna estará vacía inicialmente*. Va a ser generada dinámicamente por ustedes en el **Práctico 2** al ejecutar algoritmos como K-Means, y agrupará a los barrios en perfiles (valores 0, 1, 2, 3...) según su nivel de vulnerabilidad compartida.
