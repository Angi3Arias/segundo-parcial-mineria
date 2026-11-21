"""
Analisis exploratorio completo del dataset original (Dataset.csv)
antes de aplicar transformaciones o eliminacion de ruido.
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


def localizar_dataset(base_dir):
    """Busca Dataset.csv en la carpeta de preprocesamiento o en la raiz del proyecto."""
    rutas_posibles = [
        os.path.join(base_dir, "..", "1) Preprocesamiento", "Dataset.csv"),
        os.path.join(os.getcwd(), "PARTE_1", "1) Preprocesamiento", "Dataset.csv"),
        os.path.join(base_dir, "Dataset.csv"),
    ]
    for ruta in rutas_posibles:
        if os.path.exists(ruta):
            return os.path.abspath(ruta)
    raise FileNotFoundError("No se encontro el archivo Dataset.csv en PARTE_1/1) Preprocesamiento/")


def graficar_calidad_datos(df_raw, df_valid, base_dir):
    """Grafica valores faltantes por columna y proporcion de registros duplicados."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.2))

    nulos = df_raw.isnull().sum()
    total_raw = max(len(df_raw), 1)
    max_nulos = max(int(nulos.max()), 1)
    offset_x = max_nulos * 0.015
    colores_nulos = ["#d62728" if v > 0 else "#2ca02c" for v in nulos.values]
    axes[0].barh(nulos.index, nulos.values, color=colores_nulos, alpha=0.85)
    axes[0].set_title("Valores Faltantes por Columna (Dataset Original)", fontsize=11, fontweight="bold")
    axes[0].set_xlabel("Cantidad de valores nulos")
    axes[0].set_xlim(0, max_nulos * 1.18)
    axes[0].invert_yaxis()
    axes[0].grid(True, axis="x", linestyle="--", alpha=0.4)
    for i, v in enumerate(nulos.values):
        if v > 0:
            pct = (v / total_raw) * 100.0
            axes[0].text(v + offset_x, i, f"{v} ({pct:.2f}%)", va="center", fontsize=9, fontweight="bold", color="#d62728")

    duplicados = int(df_valid.duplicated().sum())
    unicos = len(df_valid) - duplicados
    total_valid = max(len(df_valid), 1)
    max_y = max(unicos, duplicados, 1)
    offset_y = max_y * 0.015
    etiquetas = [f"Registros únicos\n({unicos})", f"Duplicados exactos\n({duplicados})"]
    axes[1].bar(etiquetas, [unicos, duplicados], color=["#1f77b4", "#ff7f0e"], width=0.5)
    axes[1].set_title("Filas Únicas y Duplicadas", fontsize=11, fontweight="bold")
    axes[1].set_ylabel("Número de registros")
    axes[1].set_ylim(0, max_y * 1.12)
    axes[1].grid(True, axis="y", linestyle="--", alpha=0.4)
    axes[1].text(0, unicos + offset_y, f"{unicos / total_valid * 100:.2f}%", ha="center", fontweight="bold")
    axes[1].text(1, duplicados + offset_y, f"{duplicados / total_valid * 100:.2f}%", ha="center", fontweight="bold")

    plt.suptitle("Valores Nulos o Duplicados en el Dataset", fontsize=12.5, fontweight="bold", y=1.02)
    plt.tight_layout()
    ruta = os.path.join(base_dir, "1_calidad_y_nulos.png")
    plt.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return ruta


def formatear_valor(val):
    """Formatea un numero segun su magnitud para mostrarlo limpio en las graficas."""
    if abs(val) >= 100:
        return f"{val:,.1f}"
    if abs(val) < 0.05:
        return f"{val:.5f}"
    return f"{val:.4f}"


def graficar_histogramas(df, base_dir):
    """Grafica histogramas de las variables numericas en su escala original mostrando media, mediana, minimo y maximo."""
    cols = df.columns.tolist()
    n_vars = len(cols)
    n_cols = 4
    n_rows = int(np.ceil(n_vars / n_cols))
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 3.5 * n_rows))
    axes = np.atleast_1d(axes).flatten()

    for idx, col in enumerate(cols):
        serie = df[col].dropna()
        media = serie.mean()
        mediana = serie.median()
        minimo = serie.min()
        maximo = serie.max()

        axes[idx].hist(serie, bins=40, color="#74add1", alpha=0.85, edgecolor="#2c7bb6", linewidth=0.4)
        axes[idx].axvline(
            media,
            color="#e31a1c",
            linestyle="--",
            linewidth=2.2,
            label=f"Media: {formatear_valor(media)}",
        )
        axes[idx].axvline(
            mediana,
            color="#009e2f",
            linestyle="-",
            linewidth=2.2,
            label=f"Mediana: {formatear_valor(mediana)}",
        )
        axes[idx].plot([], [], linestyle="none", label=f"Mín: {formatear_valor(minimo)}")
        axes[idx].plot([], [], linestyle="none", label=f"Máx: {formatear_valor(maximo)}")
        axes[idx].set_title(col, fontsize=10.5, fontweight="bold")
        axes[idx].set_xlabel(f"{col} (valor)", fontsize=9)
        axes[idx].set_ylabel("Frecuencia (n.º de granos)", fontsize=9)
        margen = (maximo - minimo) * 0.04
        if margen == 0:
            margen = 0.5
        axes[idx].set_xlim(minimo - margen, maximo + margen)
        axes[idx].grid(True, linestyle="--", alpha=0.35)
        axes[idx].tick_params(labelsize=8)
        axes[idx].legend(loc="best", fontsize=7.5, framealpha=0.92, edgecolor="#cccccc", handlelength=1.8)

    for j in range(n_vars, len(axes)):
        axes[j].set_visible(False)

    plt.suptitle(
        f"Histogramas de las {n_vars} Variables (Media, Mediana, Mínimo y Máximo)",
        fontsize=13.5,
        fontweight="bold",
        y=1.01,
    )
    plt.tight_layout(h_pad=2.2, w_pad=1.8)
    ruta = os.path.join(base_dir, "2_distribuciones_histogramas.png")
    plt.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return ruta


def graficar_matriz_correlacion(df, base_dir):
    """Grafica el mapa de calor de la matriz de correlacion de Pearson."""
    corr = df.corr()
    fig, ax = plt.subplots(figsize=(14, 11.5))
    im = ax.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1)

    cols = corr.columns.tolist()
    ax.set_xticks(np.arange(len(cols)))
    ax.set_yticks(np.arange(len(cols)))
    ax.set_xticklabels(cols, rotation=45, ha="right", fontsize=9)
    ax.set_yticklabels(cols, fontsize=9)

    for i in range(len(cols)):
        for j in range(len(cols)):
            val = corr.values[i, j]
            color_txt = "white" if abs(val) > 0.65 else "black"
            ax.text(j, i, f"{val:.4f}", ha="center", va="center", color=color_txt, fontsize=6.2)

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Correlación de Pearson (r)")
    ax.set_title(f"Matriz de Correlación de Pearson entre las {len(cols)} Variables", fontsize=12, fontweight="bold", pad=12)
    plt.tight_layout()
    ruta = os.path.join(base_dir, "3_matriz_correlacion.png")
    plt.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return ruta


def graficar_dispersion_original(df, base_dir):
    """Grafica diagramas de dispersion en escala original para explorar grupos y anomalias."""
    pares_geometria = [
        ("Area", "Perimeter", "Tamaño y Contorno (Area vs Perimeter)"),
        ("MajorAxisLength", "MinorAxisLength", "Ejes Geométricos (Major vs Minor Axis)"),
        ("Area", "Compactness", "Tamaño vs Compacidad (Area vs Compactness)"),
        ("Area", "roundness", "Tamaño vs Redondez (Area vs roundness)"),
        ("ShapeFactor1", "ShapeFactor2", "Factores de Forma (ShapeFactor1 vs ShapeFactor2)"),
        ("Solidity", "roundness", "Regularidad del Grano (Solidity vs roundness)"),
    ]
    pares_validos = [(cx, cy, t) for cx, cy, t in pares_geometria if cx in df.columns and cy in df.columns]
    if not pares_validos and len(df.columns) >= 2:
        cols_disp = df.columns.tolist()
        pares_validos = [
            (cols_disp[i], cols_disp[i + 1], f"{cols_disp[i]} vs {cols_disp[i + 1]}")
            for i in range(0, min(len(cols_disp) - 1, 12), 2)
        ]

    n_pares = len(pares_validos)
    n_cols = 3
    n_rows = max(int(np.ceil(n_pares / n_cols)), 1)
    fig1, axes1 = plt.subplots(n_rows, n_cols, figsize=(18, 5.25 * n_rows))
    axes1 = np.atleast_1d(axes1).flatten()
    for idx, (col_x, col_y, titulo) in enumerate(pares_validos):
        r = df[col_x].corr(df[col_y])
        axes1[idx].scatter(df[col_x], df[col_y], s=8, alpha=0.35, color="#1f77b4", edgecolors="none")
        axes1[idx].set_title(f"{titulo} (r = {r:.4f})", fontsize=10.5, fontweight="bold")
        axes1[idx].set_xlabel(col_x, fontsize=9.5)
        axes1[idx].set_ylabel(col_y, fontsize=9.5)
        axes1[idx].grid(True, linestyle="--", alpha=0.4)

    for j in range(n_pares, len(axes1)):
        axes1[j].set_visible(False)

    plt.suptitle(
        "Diagramas de Dispersión: Tamaño, Forma y Regularidad",
        fontsize=13,
        fontweight="bold",
        y=1.01,
    )
    plt.tight_layout()
    ruta1 = os.path.join(base_dir, "4_dispersion_variables_originales.png")
    plt.savefig(ruta1, dpi=200, bbox_inches="tight")
    plt.close(fig1)
    return ruta1


def graficar_pca_densidad(df, base_dir):
    """
    Proyecta las variables numericas a 2D con PCA sin colores de clase:
    Panel izquierdo: dispersion monocroma con alpha bajo para ver la forma de la nube.
    Panel derecho: mapa de densidad hexbin en escala de grises para ver donde se acumulan los puntos.
    """
    X_clean = df.dropna()
    X_norm = StandardScaler().fit_transform(X_clean)
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_norm)
    var_pc1 = pca.explained_variance_ratio_[0] * 100.0
    var_pc2 = pca.explained_variance_ratio_[1] * 100.0
    var_total = var_pc1 + var_pc2

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    axes[0].scatter(X_pca[:, 0], X_pca[:, 1], s=7, alpha=0.12, color="#111111", edgecolors="none")
    axes[0].set_title("PCA 2D con Alpha Bajo (Forma de la Nube)", fontsize=11, fontweight="bold")
    axes[0].set_xlabel(f"PC1 ({var_pc1:.2f}% de varianza)", fontsize=10)
    axes[0].set_ylabel(f"PC2 ({var_pc2:.2f}% de varianza)", fontsize=10)
    axes[0].grid(True, linestyle="--", alpha=0.35)

    hb = axes[1].hexbin(X_pca[:, 0], X_pca[:, 1], gridsize=55, cmap="Greys", mincnt=1, bins="log")
    axes[1].set_title("PCA 2D con Hexbin (Acumulación / Densidad de Puntos)", fontsize=11, fontweight="bold")
    axes[1].set_xlabel(f"PC1 ({var_pc1:.2f}% de varianza)", fontsize=10)
    axes[1].set_ylabel(f"PC2 ({var_pc2:.2f}% de varianza)", fontsize=10)
    axes[1].grid(True, linestyle="--", alpha=0.35)
    cb = fig.colorbar(hb, ax=axes[1])
    cb.set_label("Densidad log10(cantidad de puntos por hexágono)", fontsize=9)

    plt.suptitle(
        f"Proyección PCA 2D sin Etiquetas (Varianza explicada total: {var_total:.2f}%)",
        fontsize=12.5,
        fontweight="bold",
        y=1.02,
    )
    plt.tight_layout()
    ruta = os.path.join(base_dir, "6_pca_2d_densidad.png")
    plt.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return ruta


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dir_graficas = os.path.join(base_dir, "GRAFICAS")
    os.makedirs(dir_graficas, exist_ok=True)
    ruta_csv = localizar_dataset(base_dir)

    print("ANALISIS EXPLORATORIO DEL DATASET ORIGINAL (SIN MODIFICAR DATOS)\n")

    # 1. Carga original y revision de columnas/nulos
    df_raw = pd.read_csv(ruta_csv)
    print(f"[1] Dimensiones originales: {df_raw.shape[0]} filas x {df_raw.shape[1]} columnas.")
    cols_vacias = [col for col in df_raw.columns if df_raw[col].isnull().all()]
    if cols_vacias:
        print(f"    Aviso: Columnas 100% vacias detectadas: {', '.join(cols_vacias)} (se ignoraran en calculos y se eliminaran en el preprocesamiento).")
    print("    Tipos de datos detectados:")
    for col, dtype in df_raw.dtypes.items():
        nulos = int(df_raw[col].isnull().sum())
        print(f"    {col:<18} | tipo: {str(dtype):<8} | nulos: {nulos}")

    # Separar vista solo con columnas no vacias para analizar estadisticas (sin alterar el archivo original)
    df_valid = df_raw.dropna(axis=1, how="all")
    num_duplicados = int(df_valid.duplicated().sum())
    print(f"\n[2] Calidad de registros (sobre las {df_valid.shape[1]} columnas no vacias):")
    print(f"    Registros totales:   {len(df_valid)}")
    print(f"    Registros unicos:    {len(df_valid) - num_duplicados}")
    print(f"    Duplicados exactos:  {num_duplicados}")

    df_num = df_valid.select_dtypes(include=[np.number])
    cols_no_num = [col for col in df_valid.columns if col not in df_num.columns]
    if cols_no_num:
        print(f"    Columnas no numericas excluidas del analisis estadistico: {', '.join(cols_no_num)}")

    # 3. Estadisticas descriptivas en escala original
    print("\n[3] Estadisticas descriptivas en escala original:")
    resumen = pd.DataFrame({
        "Min": df_num.min(),
        "Mediana": df_num.median(),
        "Media": df_num.mean(),
        "Max": df_num.max(),
        "Std": df_num.std(),
        "Varianza": df_num.var(),
        "Extremos_|Z|>3": ((df_num - df_num.mean()).abs() > 3 * df_num.std()).sum(),
    })
    print(resumen.round(4).to_string())

    cols_var_cero = df_num.columns[df_num.var() == 0].tolist()
    if cols_var_cero:
        print(f"    Aviso: Variables con varianza cero: {', '.join(cols_var_cero)}")
    else:
        print("    Verificacion de varianza: ninguna variable tiene varianza cero.")

    # 4. Pares con correlacion muy alta (|r| > 0.95)
    print("\n[4] Pares de variables con correlacion lineal muy alta (|r| > 0.95):")
    corr = df_num.corr()
    cols = corr.columns.tolist()
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            r = corr.iloc[i, j]
            if abs(r) > 0.95:
                print(f"    {cols[i]} y {cols[j]}: r = {r:.4f}")

    # 5. Generacion de graficas de analisis
    print("\n[5] Generando graficas de analisis exploratorio:")
    rutas = [
        graficar_calidad_datos(df_raw, df_valid, dir_graficas),
        graficar_histogramas(df_num, dir_graficas),
        graficar_matriz_correlacion(df_num, dir_graficas),
        graficar_dispersion_original(df_num, dir_graficas),
        graficar_pca_densidad(df_num, dir_graficas),
    ]
    for r in rutas:
        print(f"    Guardada: {r}")


if __name__ == "__main__":
    main()
