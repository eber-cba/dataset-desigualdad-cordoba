import json
import os

base_dir = r"c:\Users\eberc\.gemini\antigravity\scratch\dataset_cordoba\notebooks_alumnos"
os.makedirs(base_dir, exist_ok=True)

def create_nb(filename, title, description, tasks):
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                f"# {title}\n",
                "\n",
                f"{description}\n",
                "\n",
                "## 📋 Tareas del Sprint:\n"
            ] + [f"- [ ] {t}\n" for t in tasks]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import pandas as pd\n",
                "import numpy as np\n",
                "import matplotlib.pyplot as plt\n",
                "\n",
                "# TODO: Escribe tu código aquí abajo 👇\n"
            ]
        }
    ]
    
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.9.7"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }
    
    path = os.path.join(base_dir, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)

create_nb(
    '01_exploracion_plantilla.ipynb', 
    'Práctico 1: Análisis y Visualización Exploratoria (EDA)', 
    'En este notebook vamos a cargar nuestro dataset final y explorarlo estadísticamente para entender qué variables contiene e intentar renderizar las primeras gráficas y mapas.',
    [
        'Cargar el csv final del repositorio local usando Pandas (`pd.read_csv`).', 
        'Revisar los tipos de datos y descubrir nulos usando `.info()` y `.isnull().sum()`.', 
        'Limpiar o imputar datos faltantes mediante lógica matemática (ej: medias).',
        'Armar un histograma de la distribución del NBI en Córdoba usando matplotlib.', 
        'Investigación libre: armar un mapa o gráfico cruzando la Pobreza (NBI) vs Accesibilidad a Hospitales/Educación.'
    ]
)

create_nb(
    '02_clustering_plantilla.ipynb',
    'Práctico 2: Aprendizaje No Supervisado (Clustering Geodemográfico)',
    'Acá usaremos algoritmos para buscar "perfiles socio-urbanos" en los barrios de la ciudad. El algoritmo KMeans agrupará a los barrios en diferentes categorías (clusters) midiendo automáticamente las distancias matemáticas entre sus variables.',
    [
        'Filtrar la tabla base para quedarnos sólo con las columnas numéricas clave (NBI, escuelas cerca, luminarias, etc).', 
        'Escalar los datos usando la clase `StandardScaler` de scikit-learn (Esto es vital para no romper el algoritmo geométrico).', 
        'Aplicar el algoritmo `KMeans` pidiéndole que extraiga *K* perfiles socio-urbanos (ej: k=4 o 5).', 
        'Concatenar el número de cluster resultante a una nueva columna (ej: `df["cluster_id"]`).',
        'Estimar los centros: ¿Qué características diferencian en la realidad al Grupo 0 frente al Grupo 2?'
    ]
)

create_nb(
    '03_regresion_plantilla.ipynb',
    'Práctico 3: Aprendizaje Supervisado (Predicción y Entendimiento)',
    'En esta etapa pasamos de visualizar los datos a predecir resultados. Le daremos la infraestructura de la ciudad por barrio y el modelo intentará aprender por su cuenta a diagnosticar la vulnerabilidad socioeconómica de ese grupo urbano.',
    [
        'Desvincular el Target: Separar el Dataset en "Features" / X (la infraestructura de la ciudad) y la predicción (Variable Y = `nbi`).', 
        'Realizar un Data Split separando el 80% como array de Training y el 20% como Testing (datos ciegos para validación).', 
        'Importar y entrenar (`.fit()`) un modelo potente como `RandomForestRegressor`.', 
        'Evaluar la divergencia (Error MAE o RMSE) comprobando si el modelo predijo el nivel socioeconómico correctamente del subconjunto de testing.', 
        'Recuperar la **Feature Importance** de Scikit-Learn: ¿El modelo dice matemáticamente que afecta más no tener escuelas cerca o no tener parada de colectivos?'
    ]
)

print("Plantillas de Notebooks para los alumnos generadas correctamente!")
