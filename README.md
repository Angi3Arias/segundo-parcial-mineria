# Segundo Parcial — Minería de Datos (BUAP - FCC)

Proyecto para construir un modelo de clasificación basado en una Red Neuronal Artificial (RNA) que modele el comportamiento de los clusters identificados con **DBSCAN** a partir de la base de datos de granos (`Dataset.csv`).

---

## Organización del Proyecto

```text
.
├── PARTE_1/
│   ├── Analisis/
│   │   ├── analisis_datos.py            # Script de análisis exploratorio (sin modificar datos)
│   │   ├── RESUMEN_ANALISIS.md          # Hallazgos del análisis y plan de limpieza
│   │   └── GRAFICAS/                    # Gráficas exploratorias (calidad, histogramas, correlación, dispersión y PCA)
│   └── 1) Preprocesamiento/
│       ├── Dataset.csv                  # Dataset original (13,611 filas x 17 columnas)
│       ├── preprocesamiento.py          # Script del Inciso 1 (limpieza, Z-score y DBSCAN)
│       ├── dataset_preprocesado.csv     # Dataset limpio con columna Clase (13,094 filas x 17 columnas)
│       ├── RESUMEN_PREPROCESAMIENTO.md  # Explicación paso a paso del preprocesamiento y métricas
│       └── GRAFICAS/                    # Gráficas de estandarización, k-distancias, métricas, DBSCAN y clases
│
└── Examen_Documento/                    # Desarrollo del reporte formal en LaTeX (compatible con Overleaf)
    ├── main.tex                         # Documento principal en LaTeX
    ├── Escudos/                         # Escudos institucionales (BUAP y FCC)
    └── Inciso_1/                        # Gráficas usadas en la redacción del Inciso 1
```

---

## Resumen de cada Carpeta

### 1. `PARTE_1/Analisis/` (Análisis Exploratorio)
Revisa `Dataset.csv` sin modificar ningún valor para diagnosticar los problemas antes de limpiar:
- Detecta la columna vacía `Unnamed: 16` (`100%` nulos) y `68` filas duplicadas exactas.
- Identifica diferencias extremas de escala (`Area` hasta `254,616` vs `ShapeFactor2` en `0.0017`).
- Muestra la estructura de **5 nubes con distintas densidades** y puntos aislados en las orillas (ruido global).

### 2. `PARTE_1/1) Preprocesamiento/` (Inciso 1 del Examen)
Implementa en `preprocesamiento.py` la limpieza y el agrupamiento solicitado en la Etapa 1:
1. **Limpieza:** elimina `Unnamed: 16`, quita `68` duplicados (`13,543` granos únicos) y verifica varianza $> 0$.
2. **Estandarización Z-score:** centra las `16` variables numéricas en media `0.00` y desviación estándar `1.00`.
3. **DBSCAN Multinivel (distancia Manhattan, `MinPts = 32`):** calcula los niveles de `eps` desde los percentiles de la curva de 32-distancias (`P20 = 1.60`, `P50 = 2.25`, `P90 = 4.00`), filtra **`449` puntos de ruido global (`3.32%`)** y separa las **5 clases naturales**.
4. **Métricas de calidad:** `Silhouette Score = 0.3943`, `Calinski-Harabasz = 8,709.6`, `5` clases y `3.32%` de ruido.
5. **Salida:** guarda `dataset_preprocesado.csv` (`13,094` filas × `17` columnas: `16` variables + `Clase` de `0` a `4`), listo para la Etapa 2 (Muestreo).

### 3. `Examen_Documento/` (Reporte en LaTeX)
Contiene el desarrollo del reporte entregable en **LaTeX** (`main.tex`), junto con los escudos institucionales (`Escudos/`) y las gráficas integradas por inciso (`Inciso_1/`), listo para compilar en Overleaf o en local.

---

## ¿Cómo ejecutar el código?

1. **Análisis exploratorio:**
   ```bash
   python PARTE_1/Analisis/analisis_datos.py
   ```

2. **Preprocesamiento (Inciso 1):**
   ```bash
   python "PARTE_1/1) Preprocesamiento/preprocesamiento.py"
   ```
