# Segundo Parcial - Minería de Datos (BUAP - FCC)

Este repositorio contiene el desarrollo del proyecto correspondiente al **Segundo Parcial de Minería de Datos** de la Facultad de Ciencias de la Computación (BUAP).

El objetivo general es construir un modelo de clasificación basado en una **Red Neuronal Artificial (RNA / MLP)** que modele el comportamiento de los clusters identificados a partir del algoritmo **DBSCAN** sobre el conjunto de datos de granos (`Dataset.csv`).

---

## Estructura del Proyecto

```text
├── ANALISIS/
│   ├── analisis_datos.py                         # Código del análisis exploratorio visual
│   ├── RESUMEN_ANALISIS.md                       # Documentación detallada del análisis
│   ├── 1_calidad_y_nulos.png                     # Diagnóstico de nulos y duplicados
│   ├── 2_distribuciones_histogramas.png          # Histogramas de las 16 variables
│   ├── 3_matriz_correlacion.png                  # Correlación de Pearson
│   ├── 4_dispersion_variables_originales.png     # Dispersión bivariada
│   ├── 6_pca_2d_densidad.png                     # Proyección 2D inicial por PCA
│   └── ilustracion_de_los_atributos.png          # Referencia visual de los atributos
│
├── Preprocesamiento/
│   ├── preprocesamiento.py                       # Implementación del Inciso 1 (limpieza y DBSCAN)
│   ├── RESUMEN_PREPROCESAMIENTO.md               # Documentación y justificación técnica
│   ├── dataset_preprocesado.csv                  # Dataset final limpio y con etiquetas de Clase
│   ├── 1_antes_despues_estandarizacion.png       # Efecto del escalado Z-score
│   ├── 2_curva_k_distancia_dbscan.png            # Curva k-distancias para selección de epsilon
│   ├── 3_metricas_calidad_dbscan.png             # Evaluación de métricas de calidad de clusters
│   ├── 4_dbscan_clustering_y_ruido.png           # Identificación visual de ruido global y clusters
│   └── 5_resumen_preprocesamiento_y_clases.png   # Balance final y distribución de clases
│
├── ASIGNACION/
│   ├── 2o parcial.pdf                            # Requisitos oficiales del examen
│   ├── Dataset.csv                               # Dataset original con 13,611 registros
│   ├── Dataset.txt                               # Descripción de variables y atributos
│   └── datos.rar                                 # Archivo comprimido original
│
├── .gitignore                                    # Exclusión de PDF_TEMAS/ y carpetas pycache/
└── README.md                                     # Descripción y guía del repositorio
```

---

## 1. Carpeta `ANALISIS/`: Diagnóstico Exploratorio y Plan de Acción

En esta carpeta se encuentra el script **[`analisis_datos.py`](ANALISIS/analisis_datos.py)**, el cual realiza una inspección visual y estadística exhaustiva sobre los datos sin modificar ni borrar ningún registro del archivo original.

### Propósito
Generar una serie de gráficos diagnósticos para entender el estado real de los datos, identificar anomalías y fundamentar el plan de limpieza antes de ejecutar cualquier transformación:

1. **Revisión de Nulos y Duplicados (`1_calidad_y_nulos.png`):**
   - Confirmó que las 16 variables reales del grano no tienen valores faltantes (`0` nulos).
   - Detectó una columna espuria al final (`Unnamed: 16`) generada por una coma terminal en el CSV con 100% de datos vacíos.
   - Detectó 68 filas duplicadas exactas (0.50%).

2. **Inspección de Distribuciones y Escalas (`2_distribuciones_histogramas.png`):**
   - Evidenció una disparidad severa de magnitudes: variables de tamaño como `Area` superan los `250,000`, mientras que factores de forma como `ShapeFactor2` se encuentran en el orden de `0.001`.
   - Justificó la necesidad indispensable de estandarización previa al cálculo de distancias.

3. **Matriz de Correlación (`3_matriz_correlacion.png`):**
   - Identificó fuertes redundancias entre medidas de tamaño (`Area`, `ConvexArea`, `Perimeter`, `EquivDiameter`) y variables de forma (`Compactness`, `ShapeFactor3`).

4. **Diagramas de Dispersión y Proyecciones PCA (`4_dispersion_variables_originales.png` y `6_pca_2d_densidad.png`):**
   - Mostró la formación de grupos densos naturales y la existencia de puntos periféricos aislados (candidatos a ruido global).

Para un desglose detallado de las interpretaciones, consulta [RESUMEN_ANALISIS.md](ANALISIS/RESUMEN_ANALISIS.md).

---

## 2. Carpeta `Preprocesamiento/`: Implementación del Inciso 1

En esta carpeta se implementa lo requerido formalmente en el **Inciso 1** del examen mediante el script **[`preprocesamiento.py`](Preprocesamiento/preprocesamiento.py)**:

> *"Realizar e implementar una etapa de preprocesamiento a la base de datos propuesta, de tal forma que se eliminen diferentes tipos de problemas del dataset, como ruido, desviaciones, etc. Se deberá de usar un algoritmo de agrupamiento (DBSCAN), para la detección de ruido tipo global, ajustándolo de acuerdo a los requerimientos del dataset (se deberá de elegir las métricas para medir la calidad de los estratos generados). Se debe documentar cómo se ha aplicado el algoritmo al problema. Se deberá generar un archivo denominado 'preprocesamiento.py'. A los grupos generados por esta etapa, asignarles un valor de clase."*

### Pasos Implementados en `preprocesamiento.py`:

1. **Depuración Inicial:**
   - Eliminación de la columna residual vacía `Unnamed: 16`.
   - Eliminación de los 68 registros duplicados exactos para evitar densidades artificiales, dejando 13,543 instancias únicas.
   - Verificación de no-constancia en todas las variables (varianza > 0).

2. **Estandarización Z-score (`StandardScaler`):**
   - Se escalaron las 16 variables numéricas para que tengan media 0 y varianza unitaria, asegurando que ninguna variable domine el cálculo de distancias euclidianas.

3. **Ajuste y Aplicación de DBSCAN en 16 Dimensiones:**
   - **`MinPts = 32`:** Establecido bajo el criterio multidimensional estándar ($\text{MinPts} = 2 \times D = 2 \times 16$).
   - **Curva de $k$-distancias (`2_curva_k_distancia_dbscan.png`):** Identificación visual del codo en la distancia al 32-ésimo vecino para definir el rango de $\varepsilon$.
   - **Evaluación de Métricas de Calidad (`3_metricas_calidad_dbscan.png`):** Comparación de configuraciones con métricas internas de validación no supervisada:
     - *Silhouette Score* ($\uparrow$)
     - *Davies-Bouldin Index* ($\downarrow$)
     - *Calinski-Harabasz Index* ($\uparrow$)
   - **Parámetros Seleccionados:** $\varepsilon = 1.50$ y $\text{MinPts} = 32$. Se logró aislar y remover **402 instancias de ruido global (2.97%)**, conservando intactos los estratos representativos de los granos.

4. **Asignación de Clases y Generación del Dataset Preprocesado:**
   - A cada grupo generado se le asignó su correspondiente valor en la columna **`Clase`** (`Cluster 0` y `Cluster 1`).
   - Se exportó el archivo limpio resultante: **[`dataset_preprocesado.csv`](Preprocesamiento/dataset_preprocesado.csv)** (13,141 registros listos para la etapa de muestreo).

Para más detalles técnicos y tablas comparativas, consulta [RESUMEN_PREPROCESAMIENTO.md](Preprocesamiento/RESUMEN_PREPROCESAMIENTO.md).

---

## Ejecución de los Scripts

### Requisitos
- Python 3.10+
- Bibliotecas necesarias:
  ```bash
  pip install pandas numpy matplotlib seaborn scikit-learn
  ```

### Ejecutar el Análisis Exploratorio:
```bash
python ANALISIS/analisis_datos.py
```

### Ejecutar el Preprocesamiento (Inciso 1):
```bash
python Preprocesamiento/preprocesamiento.py
```
