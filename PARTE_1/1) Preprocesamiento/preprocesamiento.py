"""
Etapa 1: Preprocesamiento de datos, estandarizacion y deteccion de ruido global con DBSCAN.
Materia: Mineria de Datos (2do Parcial).
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score


def localizar_dataset(base_dir):
    """Carga Dataset.csv ubicado directamente en la carpeta de preprocesamiento."""
    ruta_local = os.path.join(base_dir, "Dataset.csv")
    if os.path.exists(ruta_local):
        return os.path.abspath(ruta_local)

    # Rutas de respaldo por si el script se ejecuta desde la raiz u otra carpeta
    rutas_alternativas = [
        os.path.join(os.getcwd(), "PARTE_1", "1) Preprocesamiento", "Dataset.csv"),
        os.path.join(os.getcwd(), "Dataset.csv"),
    ]
    for ruta in rutas_alternativas:
        if os.path.exists(ruta):
            return os.path.abspath(ruta)
    raise FileNotFoundError(f"No se encontro el archivo Dataset.csv en {ruta_local}")


def graficar_antes_despues_estandarizacion(df_original, df_scaled, base_dir):
    """Compara las escalas de 4 variables representativas antes y despues de Z-score."""
    vars_preferidas = ["Area", "Perimeter", "Solidity", "ShapeFactor2"]
    vars_ejemplo = [c for c in vars_preferidas if c in df_original.columns]
    if len(vars_ejemplo) < 4:
        vars_ejemplo = df_original.columns[:4].tolist()
    colores = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd"]

    n_vars = len(vars_ejemplo)
    fig, axes = plt.subplots(2, n_vars, figsize=(4.5 * n_vars, 7.5))

    for i, (col, color) in enumerate(zip(vars_ejemplo, colores)):
        datos_raw = df_original[col].dropna()
        media_raw = datos_raw.mean()
        axes[0, i].hist(datos_raw, bins=35, color=color, alpha=0.72, edgecolor="white", linewidth=0.4)
        axes[0, i].axvline(media_raw, color="#d62728", linestyle="--", linewidth=1.6,
                           label=f"Media: {media_raw:,.4g}")
        axes[0, i].set_title(f"Antes: {col}", fontsize=10.5, fontweight="bold")
        axes[0, i].set_xlabel("Valor original", fontsize=9)
        axes[0, i].set_ylabel("Frecuencia (granos)", fontsize=9)
        axes[0, i].legend(fontsize=8, loc="upper right")
        axes[0, i].grid(True, linestyle="--", alpha=0.35)

        datos_z = df_scaled[col].dropna()
        media_z = datos_z.mean()
        std_z = datos_z.std()
        axes[1, i].hist(datos_z, bins=35, color=color, alpha=0.72, edgecolor="white", linewidth=0.4)
        axes[1, i].axvline(media_z, color="#d62728", linestyle="--", linewidth=1.6,
                           label=f"Media: {media_z:.2f}\nStd: {std_z:.2f}")
        axes[1, i].set_title(f"Después (Z-score): {col}", fontsize=10.5, fontweight="bold")
        axes[1, i].set_xlabel("Valor estandarizado (Z)", fontsize=9)
        axes[1, i].set_ylabel("Frecuencia (granos)", fontsize=9)
        axes[1, i].set_xlim(min(float(datos_z.min()) - 0.5, -4.5), max(float(datos_z.max()) + 0.5, 4.5))
        axes[1, i].legend(fontsize=8, loc="upper right")
        axes[1, i].grid(True, linestyle="--", alpha=0.35)

    plt.suptitle(
        "Efecto de la Estandarización Z-score en Variables de Escalas Muy Distintas",
        fontsize=13,
        fontweight="bold",
        y=1.02,
    )
    plt.tight_layout()
    ruta = os.path.join(base_dir, "1_antes_despues_estandarizacion.png")
    plt.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return ruta


def calcular_k_distancias(X_scaled, min_pts):
    """Calcula las distancias Manhattan ordenadas al vecino #min_pts y sus percentiles del codo."""
    nn = NearestNeighbors(n_neighbors=min_pts, metric="manhattan", n_jobs=-1)
    distancias, _ = nn.fit(X_scaled).kneighbors(X_scaled)
    k_dist = np.sort(distancias[:, -1])
    p85 = float(np.percentile(k_dist, 85))
    p90 = float(np.percentile(k_dist, 90))
    return k_dist, p85, p90


def graficar_curva_k_distancia(k_dist, min_pts, eps_opt, p85, p90, base_dir):
    """Grafica la curva de k-distancias ordenadas para ubicar el codo y el rango de eps."""
    idx_eps = int(np.searchsorted(k_dist, eps_opt))
    pct_debajo = (idx_eps / max(len(k_dist), 1)) * 100.0

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.2))

    axes[0].plot(k_dist, color="#1f77b4", linewidth=1.8)
    axes[0].axhline(eps_opt, color="#d62728", linestyle="--", linewidth=1.8,
                    label=f"eps elegido = {eps_opt:.2f} ({pct_debajo:.1f}% de granos por debajo)")
    axes[0].axhspan(p85, p90, color="#ff7f0e", alpha=0.16,
                    label=f"Zona del codo P85–P90 ({p85:.2f} a {p90:.2f})")
    axes[0].set_title(f"Curva Completa de {min_pts}-Distancias (Todos los Granos)", fontsize=11, fontweight="bold")
    axes[0].set_xlabel("Granos ordenados por cercanía a sus vecinos", fontsize=9.5)
    axes[0].set_ylabel(f"Distancia Manhattan al vecino #{min_pts}", fontsize=9.5)
    axes[0].legend(loc="upper left", fontsize=8.8)
    axes[0].grid(True, linestyle="--", alpha=0.4)

    inicio_zoom = int(len(k_dist) * 0.80)
    x_zoom = np.arange(inicio_zoom, len(k_dist))
    k_zoom = k_dist[inicio_zoom:]
    axes[1].plot(x_zoom, k_zoom, color="#1f77b4", linewidth=2.0)
    axes[1].axhline(eps_opt, color="#d62728", linestyle="--", linewidth=1.8,
                    label=f"eps elegido = {eps_opt:.2f}")
    axes[1].axhline(p85, color="#2ca02c", linestyle=":", linewidth=1.5, label=f"Percentil 85 = {p85:.2f}")
    axes[1].axhline(p90, color="#9467bd", linestyle=":", linewidth=1.5, label=f"Percentil 90 = {p90:.2f}")
    y_min_zoom = max(0.0, float(k_zoom[0]) * 0.85)
    y_max_zoom = float(np.percentile(k_dist, 99.5)) * 1.15
    axes[1].set_ylim(y_min_zoom, y_max_zoom)
    axes[1].set_title("Acercamiento a la Zona del Codo (Último 20% de Granos)", fontsize=11, fontweight="bold")
    axes[1].set_xlabel("Índice del grano ordenado", fontsize=9.5)
    axes[1].set_ylabel(f"Distancia Manhattan al vecino #{min_pts}", fontsize=9.5)
    axes[1].legend(loc="upper left", fontsize=8.8)
    axes[1].grid(True, linestyle="--", alpha=0.4)

    plt.suptitle(
        f"Selección del Rango de Epsilon (eps) con Distancia Manhattan (MinPts = {min_pts})",
        fontsize=12.5,
        fontweight="bold",
        y=1.02,
    )
    plt.tight_layout()
    ruta = os.path.join(base_dir, "2_curva_k_distancia_dbscan.png")
    plt.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return ruta


def graficar_metricas_dbscan(tabla_metricas, eps_opt, min_pts_opt, base_dir):
    """Grafica las 4 metricas de calidad de DBSCAN para todas las configuraciones probadas."""
    etiquetas_x = [f"{r['eps']:.2f}" for r in tabla_metricas]
    x_pos = np.arange(len(etiquetas_x))
    idx_opt = next(i for i, r in enumerate(tabla_metricas) if r["eps"] == eps_opt)

    sils = [r["sil"] for r in tabla_metricas]
    dbis = [r["dbi"] for r in tabla_metricas]
    chis = [r["chi"] for r in tabla_metricas]
    ruidos = [r["pct_ruido"] for r in tabla_metricas]
    clusters = [r["n_clusters"] for r in tabla_metricas]

    fig, axes = plt.subplots(2, 2, figsize=(15, 9.2))

    # 1. Silhouette Score
    rango_sil = max(max(sils) - min(sils), 0.05)
    offset_sil = rango_sil * 0.045
    axes[0, 0].plot(x_pos, sils, marker="o", linewidth=2, color="#1f77b4")
    axes[0, 0].scatter([idx_opt], [sils[idx_opt]], s=120, color="#d62728", zorder=5,
                       label=f"Elegido (eps={eps_opt:.2f})")
    for i, v in enumerate(sils):
        axes[0, 0].text(i, v + offset_sil, f"{v:.4f}", ha="center", va="bottom", fontsize=8.5,
                        fontweight="bold" if i == idx_opt else "normal")
    axes[0, 0].set_title("Silhouette Score (Más cercano a 1 es mejor)", fontsize=11, fontweight="bold")
    axes[0, 0].set_xticks(x_pos)
    axes[0, 0].set_xticklabels(etiquetas_x)
    axes[0, 0].set_xlabel("Valor de eps")
    axes[0, 0].set_ylabel("Silhouette Score")
    axes[0, 0].set_ylim(min(sils) - rango_sil * 0.18, max(sils) + rango_sil * 0.24)
    axes[0, 0].legend(loc="lower right", fontsize=8.8)
    axes[0, 0].grid(True, linestyle="--", alpha=0.4)

    # 2. Davies-Bouldin Index
    rango_dbi = max(max(dbis) - min(dbis), 0.05)
    offset_dbi = rango_dbi * 0.045
    axes[0, 1].plot(x_pos, dbis, marker="s", linewidth=2, color="#2ca02c")
    axes[0, 1].scatter([idx_opt], [dbis[idx_opt]], s=120, color="#d62728", zorder=5,
                       label=f"Elegido (eps={eps_opt:.2f})")
    for i, v in enumerate(dbis):
        axes[0, 1].text(i, v + offset_dbi, f"{v:.4f}", ha="center", va="bottom", fontsize=8.5,
                        fontweight="bold" if i == idx_opt else "normal")
    axes[0, 1].set_title("Davies-Bouldin Index (Menor valor es mejor)", fontsize=11, fontweight="bold")
    axes[0, 1].set_xticks(x_pos)
    axes[0, 1].set_xticklabels(etiquetas_x)
    axes[0, 1].set_xlabel("Valor de eps")
    axes[0, 1].set_ylabel("Davies-Bouldin Index")
    axes[0, 1].set_ylim(min(dbis) - rango_dbi * 0.18, max(dbis) + rango_dbi * 0.24)
    axes[0, 1].legend(loc="upper right", fontsize=8.8)
    axes[0, 1].grid(True, linestyle="--", alpha=0.4)

    # 3. Calinski-Harabasz Index
    rango_chi = max(max(chis) - min(chis), 10.0)
    offset_chi = rango_chi * 0.045
    axes[1, 0].plot(x_pos, chis, marker="^", linewidth=2, color="#9467bd")
    axes[1, 0].scatter([idx_opt], [chis[idx_opt]], s=120, color="#d62728", zorder=5,
                       label=f"Elegido (eps={eps_opt:.2f})")
    for i, v in enumerate(chis):
        axes[1, 0].text(i, v + offset_chi, f"{v:,.0f}", ha="center", va="bottom", fontsize=8.5,
                        fontweight="bold" if i == idx_opt else "normal")
    axes[1, 0].set_title("Calinski-Harabasz Index (Mayor valor es mejor)", fontsize=11, fontweight="bold")
    axes[1, 0].set_xticks(x_pos)
    axes[1, 0].set_xticklabels(etiquetas_x)
    axes[1, 0].set_xlabel("Valor de eps")
    axes[1, 0].set_ylabel("Calinski-Harabasz Index")
    axes[1, 0].set_ylim(min(chis) - rango_chi * 0.18, max(chis) + rango_chi * 0.24)
    axes[1, 0].legend(loc="lower right", fontsize=8.8)
    axes[1, 0].grid(True, linestyle="--", alpha=0.4)

    # 4. Porcentaje de Ruido Global y Numero de Clusters
    max_ruido = max(max(ruidos), 1.0)
    offset_ruido = max_ruido * 0.025
    bar_colors = ["#d62728" if i == idx_opt else "#ff9838" for i in range(len(ruidos))]
    axes[1, 1].bar(x_pos, ruidos, color=bar_colors, alpha=0.88, width=0.58)
    for i, (pct, nc) in enumerate(zip(ruidos, clusters)):
        axes[1, 1].text(i, pct + offset_ruido, f"{pct:.2f}%\n({nc} clusters)", ha="center", va="bottom",
                        fontsize=8.3, fontweight="bold" if i == idx_opt else "normal")
    axes[1, 1].set_title("Porcentaje de Ruido Global y Clusters Detectados", fontsize=11, fontweight="bold")
    axes[1, 1].set_xticks(x_pos)
    axes[1, 1].set_xticklabels(etiquetas_x)
    axes[1, 1].set_xlabel("Valor de eps")
    axes[1, 1].set_ylabel("% de puntos clasificados como ruido")
    axes[1, 1].set_ylim(0, max_ruido * 1.24)
    axes[1, 1].grid(axis="y", linestyle="--", alpha=0.4)

    plt.suptitle(
        f"Evaluación de Métricas de Calidad en DBSCAN — Distancia Manhattan (MinPts = {min_pts_opt}, elegido eps = {eps_opt:.2f})",
        fontsize=12.5,
        fontweight="bold",
        y=1.01,
    )
    plt.tight_layout()
    ruta = os.path.join(base_dir, "3_metricas_calidad_dbscan.png")
    plt.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return ruta


def graficar_comparativa_dbscan(X_pca, var_pc1, var_pc2, etiquetas, eps_opt, min_pts_opt, base_dir):
    """Muestra antes, durante (con ruido global en rojo) y despues de DBSCAN proyectado en PCA 2D."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.6))

    axes[0].scatter(X_pca[:, 0], X_pca[:, 1], s=8, alpha=0.25, color="#3b5998", edgecolors="none")
    axes[0].set_title("1. Datos Estandarizados sin Etiquetas", fontsize=11, fontweight="bold")
    axes[0].set_xlabel(f"PC1 ({var_pc1:.2f}%)")
    axes[0].set_ylabel(f"PC2 ({var_pc2:.2f}%)")
    axes[0].grid(True, linestyle="--", alpha=0.4)

    mascara_ruido = etiquetas == -1
    colores_clusters = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd", "#8c564b", "#e377c2", "#17becf", "#bcbd22"]
    clases_validas = sorted([c for c in set(etiquetas) if c != -1])

    for idx, c in enumerate(clases_validas):
        mask_c = etiquetas == c
        axes[1].scatter(
            X_pca[mask_c, 0],
            X_pca[mask_c, 1],
            s=9,
            alpha=0.45,
            color=colores_clusters[idx % len(colores_clusters)],
            label=f"Cluster {c} (n={np.sum(mask_c):,})",
            edgecolors="none",
        )
    axes[1].scatter(
        X_pca[mascara_ruido, 0],
        X_pca[mascara_ruido, 1],
        s=18,
        alpha=0.85,
        color="#d62728",
        marker="x",
        label=f"Ruido Global (-1) (n={np.sum(mascara_ruido):,})",
    )
    axes[1].set_title(f"2. DBSCAN (eps={eps_opt:.2f}, MinPts={min_pts_opt}): Grupos y Ruido", fontsize=11, fontweight="bold")
    axes[1].set_xlabel(f"PC1 ({var_pc1:.2f}%)")
    axes[1].set_ylabel(f"PC2 ({var_pc2:.2f}%)")
    axes[1].legend(loc="upper right", fontsize=8.5, framealpha=0.92)
    axes[1].grid(True, linestyle="--", alpha=0.4)

    for idx, c in enumerate(clases_validas):
        mask_c = etiquetas == c
        axes[2].scatter(
            X_pca[mask_c, 0],
            X_pca[mask_c, 1],
            s=9,
            alpha=0.45,
            color=colores_clusters[idx % len(colores_clusters)],
            label=f"Clase {c} (n={np.sum(mask_c):,})",
            edgecolors="none",
        )
    axes[2].set_title("3. Dataset Preprocesado Final (Sin Ruido Global)", fontsize=11, fontweight="bold")
    axes[2].set_xlabel(f"PC1 ({var_pc1:.2f}%)")
    axes[2].set_ylabel(f"PC2 ({var_pc2:.2f}%)")
    axes[2].legend(loc="upper right", fontsize=8.5, framealpha=0.92)
    axes[2].grid(True, linestyle="--", alpha=0.4)

    plt.suptitle(
        "Detección de Ruido Global y Agrupamiento con DBSCAN (Vista Proyectada en PCA 2D)",
        fontsize=12.5,
        fontweight="bold",
        y=1.02,
    )
    plt.tight_layout()
    ruta = os.path.join(base_dir, "4_dbscan_clustering_y_ruido.png")
    plt.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return ruta


def graficar_resumen_final(n_inicial, n_sin_dup, df_final, base_dir):
    """Muestra la evolucion del numero de registros y la distribucion de las clases asignadas."""
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.0))

    dup_eliminados = n_inicial - n_sin_dup
    ruido_eliminado = n_sin_dup - len(df_final)
    etapas = [
        "Original\n(Dataset.csv)",
        f"Sin duplicados\n(-{dup_eliminados:,} filas)",
        f"Final sin ruido\n(-{ruido_eliminado:,} filas)",
    ]
    valores = [n_inicial, n_sin_dup, len(df_final)]
    colores_etapas = ["#6c8ebf", "#3b78b8", "#2ca02c"]
    bars1 = axes[0].bar(etapas, valores, color=colores_etapas, width=0.52)
    axes[0].set_title("Evolución del Número de Registros en la Limpieza", fontsize=11, fontweight="bold")
    axes[0].set_ylabel("Cantidad de granos")
    max_inicial = max(n_inicial, 1)
    offset_etapas = max_inicial * 0.016
    axes[0].set_ylim(0, max_inicial * 1.15)
    axes[0].grid(axis="y", linestyle="--", alpha=0.4)
    for bar, val in zip(bars1, valores):
        pct = (val / max_inicial) * 100.0
        axes[0].text(bar.get_x() + bar.get_width() / 2, val + offset_etapas,
                     f"{val:,}\n({pct:.2f}%)", ha="center", va="bottom", fontsize=9.5, fontweight="bold")

    conteo = df_final["Clase"].value_counts().sort_index()
    etiquetas_c = [f"Clase {c}" for c in conteo.index]
    colores_c = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd", "#8c564b", "#e377c2", "#17becf", "#bcbd22"]
    bars2 = axes[1].bar(etiquetas_c, conteo.values, color=colores_c[:len(conteo)], width=0.46)
    axes[1].set_title("Distribución Final de Clases Asignadas por DBSCAN", fontsize=11, fontweight="bold")
    axes[1].set_ylabel("Cantidad de granos")
    max_conteo = max(int(conteo.max()), 1)
    offset_conteo = max_conteo * 0.016
    axes[1].set_ylim(0, max_conteo * 1.16)
    axes[1].grid(axis="y", linestyle="--", alpha=0.4)
    total_final = max(len(df_final), 1)
    for bar, val in zip(bars2, conteo.values):
        pct = (val / total_final) * 100.0
        axes[1].text(bar.get_x() + bar.get_width() / 2, val + offset_conteo,
                     f"{val:,}\n({pct:.2f}%)", ha="center", va="bottom", fontsize=9.5, fontweight="bold")

    plt.suptitle(
        "Resumen Final de la Etapa 1: Limpieza y Clases Listas para Muestreo",
        fontsize=12.5,
        fontweight="bold",
        y=1.02,
    )
    plt.tight_layout()
    ruta = os.path.join(base_dir, "5_resumen_preprocesamiento_y_clases.png")
    plt.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return ruta


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dir_graficas = os.path.join(base_dir, "GRAFICAS")
    os.makedirs(dir_graficas, exist_ok=True)
    ruta_csv = localizar_dataset(base_dir)

    print("ETAPA 1: PREPROCESAMIENTO Y DETECCION DE RUIDO GLOBAL CON DBSCAN\n")

    # 1. Carga y eliminacion de columnas completamente vacias
    df = pd.read_csv(ruta_csv)
    n_inicial = df.shape[0]
    print(f"[1] Carga del dataset original desde: {ruta_csv}")
    print(f"    Dimensiones iniciales: {df.shape[0]} registros, {df.shape[1]} columnas.")

    cols_vacias = [col for col in df.columns if df[col].isnull().all()]
    if cols_vacias:
        print(f"    Columnas 100% vacias eliminadas: {', '.join(cols_vacias)}")
        df = df.drop(columns=cols_vacias)

    nulos_restantes = int(df.isnull().sum().sum())
    print(f"    Valores faltantes en las {df.shape[1]} variables validas: {nulos_restantes}")
    if nulos_restantes > 0:
        df = df.dropna().reset_index(drop=True)

    df = df.select_dtypes(include=[np.number])

    # 2. Eliminacion de duplicados exactos
    num_duplicados = int(df.duplicated().sum())
    df = df.drop_duplicates(keep="first").reset_index(drop=True)
    n_sin_dup = df.shape[0]
    print(f"\n[2] Registros duplicados exactos eliminados: {num_duplicados}")
    print(f"    Registros unicos restantes: {n_sin_dup}")

    # 3. Verificacion de varianza cero
    varianzas = df.var()
    cols_constantes = varianzas[varianzas == 0].index.tolist()
    print(f"\n[3] Columnas con varianza cero (constantes): {len(cols_constantes)}")
    if cols_constantes:
        df = df.drop(columns=cols_constantes)

    # 4. Estandarizacion Z-score
    print("\n[4] Estandarizacion Z-score:")
    col_max_escala = df.mean().idxmax()
    col_min_escala = df.mean().idxmin()
    print(f"    Antes: {col_max_escala} media = {df[col_max_escala].mean():.2f}, {col_min_escala} media = {df[col_min_escala].mean():.5f}")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df)
    df_scaled = pd.DataFrame(X_scaled, columns=df.columns)
    media_global_z = float(df_scaled.mean().mean())
    std_global_z = float(df_scaled.std(ddof=0).mean())
    print(f"    Despues: todas las {df_scaled.shape[1]} variables con media = {media_global_z:.2f} y desviacion estandar = {std_global_z:.2f}.")

    ruta_img1 = graficar_antes_despues_estandarizacion(df, df_scaled, dir_graficas)
    print(f"    Grafica guardada: {ruta_img1}")

    # 5. Ajuste de DBSCAN con distancia Manhattan (MinPts = 2 * D) y curva de k-distancias
    n_dims = df_scaled.shape[1]
    min_pts_opt = 2 * n_dims
    k_dist, p85, p90 = calcular_k_distancias(X_scaled, min_pts_opt)
    eps_candidatos = [2.00, 2.25, 2.50, 3.00, 3.50, 4.00, 4.50]

    print(f"\n[5] Evaluacion de DBSCAN en {n_dims} dimensiones (distancia Manhattan, MinPts = {min_pts_opt}):")
    print(f"    Zona del codo en la curva de {min_pts_opt}-distancias: P85 = {p85:.2f}, P90 = {p90:.2f}\n")
    print(f"    {'eps':>5} | {'MinPts':>6} | {'Clusters':>8} | {'Ruido (#)':>9} | {'Ruido (%)':>9} | {'Silhouette':>10} | {'Davies-B.':>9} | {'Calinski-H.':>11}")

    resultados = {}
    tabla_metricas = []

    for eps in eps_candidatos:
        db = DBSCAN(eps=eps, min_samples=min_pts_opt, metric="manhattan", n_jobs=-1)
        etiquetas = db.fit_predict(X_scaled)

        mascara_validos = etiquetas != -1
        n_clusters = len(set(etiquetas[mascara_validos]))
        n_ruido = int(np.sum(etiquetas == -1))
        pct_ruido = (n_ruido / len(etiquetas)) * 100.0

        if n_clusters >= 2:
            sil = float(silhouette_score(X_scaled[mascara_validos], etiquetas[mascara_validos], metric="manhattan"))
            dbi = float(davies_bouldin_score(X_scaled[mascara_validos], etiquetas[mascara_validos]))
            chi = float(calinski_harabasz_score(X_scaled[mascara_validos], etiquetas[mascara_validos]))
        else:
            sil, dbi, chi = 0.0, float("inf"), 0.0

        resultados[eps] = (etiquetas, n_clusters, n_ruido, pct_ruido, sil, dbi, chi)
        tabla_metricas.append({
            "eps": eps,
            "min_pts": min_pts_opt,
            "n_clusters": n_clusters,
            "n_ruido": n_ruido,
            "pct_ruido": pct_ruido,
            "sil": sil,
            "dbi": dbi,
            "chi": chi,
        })
        print(f"    {eps:5.2f} | {min_pts_opt:6d} | {n_clusters:8d} | {n_ruido:9d} | {pct_ruido:8.2f}% | {sil:10.4f} | {dbi:9.4f} | {chi:11.1f}")

    # Seleccionar eps = 2.50 para separar multiples estratos densos en el espacio 16D
    eps_opt = 2.50

    etiquetas_opt, n_clusters_opt, n_ruido_opt, pct_ruido_opt, sil_opt, dbi_opt, chi_opt = resultados[eps_opt]
    print(f"\n    Configuracion seleccionada: eps = {eps_opt:.2f}, MinPts = {min_pts_opt}")
    print(f"    Clusters = {n_clusters_opt}, Ruido global eliminado = {n_ruido_opt} ({pct_ruido_opt:.2f}%)")
    print(f"    Silhouette = {sil_opt:.4f}, Davies-Bouldin = {dbi_opt:.4f}, Calinski-Harabasz = {chi_opt:.1f}")

    # Proyeccion PCA 2D unicamente para visualizar el resultado
    pca_vis = PCA(n_components=2, random_state=42)
    X_pca = pca_vis.fit_transform(X_scaled)
    var_pc1 = pca_vis.explained_variance_ratio_[0] * 100.0
    var_pc2 = pca_vis.explained_variance_ratio_[1] * 100.0

    ruta_img2 = graficar_curva_k_distancia(k_dist, min_pts_opt, eps_opt, p85, p90, dir_graficas)
    ruta_img3 = graficar_metricas_dbscan(tabla_metricas, eps_opt, min_pts_opt, dir_graficas)
    ruta_img4 = graficar_comparativa_dbscan(X_pca, var_pc1, var_pc2, etiquetas_opt, eps_opt, min_pts_opt, dir_graficas)
    print(f"    Grafica guardada: {ruta_img2}")
    print(f"    Grafica guardada: {ruta_img3}")
    print(f"    Grafica guardada: {ruta_img4}")

    # 6. Eliminacion de ruido global y asignacion de Clase
    mascara_limpia = etiquetas_opt != -1
    df_preprocesado = df_scaled[mascara_limpia].copy().reset_index(drop=True)
    df_preprocesado["Clase"] = etiquetas_opt[mascara_limpia]

    ruta_img5 = graficar_resumen_final(n_inicial, n_sin_dup, df_preprocesado, dir_graficas)
    print(f"    Grafica guardada: {ruta_img5}")

    print("\n[6] Distribucion final de clases asignadas:")
    conteo_clases = df_preprocesado["Clase"].value_counts().sort_index()
    for clase, cantidad in conteo_clases.items():
        porcentaje = (cantidad / len(df_preprocesado)) * 100.0
        print(f"    Clase {clase}: {cantidad:5d} granos ({porcentaje:5.2f}%)")

    ruta_salida = os.path.join(base_dir, "dataset_preprocesado.csv")
    df_preprocesado.to_csv(ruta_salida, index=False)
    print(f"\nDataset preprocesado guardado en: {ruta_salida}")
    print(f"Dimensiones finales: {df_preprocesado.shape[0]} filas x {df_preprocesado.shape[1]} columnas ({n_dims} variables + Clase).")


if __name__ == "__main__":
    main()
