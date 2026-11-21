# Segundo Parcial - Minería de Datos (BUAP)

Proyecto para modelar mediante una Red Neuronal Artificial (RNA) los grupos obtenidos a partir de la base de datos de granos (`Dataset.csv`).

---

## Estructura del Proyecto

* **`ANALISIS/`**: Código y carpeta `GRAFICAS/` del análisis exploratorio inicial.
* **`1) Preprocesamiento/`**: Dataset original (`Dataset.csv`), código del **Inciso 1** (limpieza de datos, agrupamiento con DBSCAN), `dataset_preprocesado.csv` y carpeta `GRAFICAS/`.
* **`Examen_Documento/`**: Redacción formal del examen en LaTeX (compatible con Overleaf) e imágenes en `Inciso_1/`.

---

## 1. Carpeta `ANALISIS/` (Exploración y Plan de Limpieza)

Contiene el script **`analisis_datos.py`** y las gráficas generadas en **`ANALISIS/GRAFICAS/`** para revisar los datos originales:

* **¿Qué se hizo?** Se generaron gráficas de calidad de datos, histogramas de distribución, matriz de correlación, dispersión en 2D y proyección PCA 2D.
* **¿Para qué sirvió?** Para ver cómo venían los datos y definir el plan de limpieza:
  1. Se detectó una columna vacía al final (`Unnamed: 16`) y 68 filas duplicadas.
  2. Se identificó una gran diferencia de escalas (por ejemplo, `Area` supera los 200,000 mientras que los factores de forma son menores a 0.01), lo que hizo indispensable estandarizar.
  3. Se confirmó la presencia de puntos aislados en las orillas que debían tratarse como ruido global.

---

## 2. Carpeta `1) Preprocesamiento/` (Inciso 1 del Examen)

Contiene el script **`preprocesamiento.py`** y las gráficas generadas en **`1) Preprocesamiento/GRAFICAS/`**, donde se implementa el plan definido en el análisis cumpliendo con la **Etapa 1**:

1. **Limpieza:** Se eliminó la columna vacía residual y las filas duplicadas.
2. **Estandarización:** Se aplicó Z-score (`StandardScaler`) a las 16 variables numéricas para que todas tengan el mismo peso.
3. **Detección de Ruido con DBSCAN:**
   - Se ajustaron los parámetros con la curva de distancias ($\text{MinPts} = 32$, $\varepsilon = 1.50$).
   - Se evaluó la calidad con métricas internas (*Silhouette*, *Davies-Bouldin* y *Calinski-Harabasz*).
   - Se detectó y eliminó el **ruido global** (402 puntos marcados con `-1`).
4. **Asignación de Clases:** Se asignó la columna **`Clase`** a los clusters encontrados (`Clase 0` y `Clase 1`).
5. **Archivo Resultante:** Se generó **`dataset_preprocesado.csv`**, listo para la etapa de muestreo.

---

## ¿Cómo ejecutar el código?

1. **Ejecutar el análisis exploratorio:**
   ```bash
   python ANALISIS/analisis_datos.py
   ```

2. **Ejecutar el preprocesamiento (Inciso 1):**
   ```bash
   python "1) Preprocesamiento/preprocesamiento.py"
   ```
