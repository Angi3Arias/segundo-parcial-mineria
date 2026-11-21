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
    """Busca Dataset.csv en la carpeta actual o en ASIGNACION."""
    rutas_posibles = [
        os.path.join(base_dir, "Dataset.csv"),
        os.path.join(base_dir, "..", "ASIGNACION", "Dataset.csv"),
        os.path.join(base_dir, "ASIGNACION", "Dataset.csv"),
    ]
    for ruta in rutas_posibles:
        if os.path.exists(ruta):
            return os.path.abspath(ruta)
    raise FileNotFoundError("No se encontro el archivo Dataset.csv")


def detectar_columnas_vacias(df, ruta_csv):
    """Detecta dinamicamente columnas 100% vacias y verifica si provienen de una coma final."""
    with open(ruta_csv, "r", encoding="utf-8-sig") as f:
        primera_linea = f.readline().rstrip("\r\n")
    tiene_coma_final = primera_linea.endswith(",")

    hallazgos = []
    total_cols = len(df.columns)
    for pos, col in enumerate(df.columns, start=1):
        if df[col].isnull().all():
            es_por_coma = tiene_coma_final and pos == total_cols and str(col).startswith("Unnamed:")
            hallazgos.append({"pos": pos, "nombre": col, "por_coma_final": es_por_coma})
    return hallazgos


def graficar_antes_despues_estandarizacion(df_original, df_scaled, base_dir):
    """Compara las escalas de 4 variables representativas antes y despues de Z-score."""
    vars_ejemplo = ["Area", "Perimeter", "Solidity", "ShapeFactor2"]
    colores = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd"]

    fig, axes = plt.subplots(2, 4, figsize=(18, 7.5))

    for i, (col, color) in enumerate(zip(vars_ejemplo, colores)):
        datos_raw = df_original[col]
        axes[0, i].hist(datos_raw, bins=35, color=color, alpha=0.72, edgecolor="white", linewidth=0.4)
        axes[0, i].axvline(datos_raw.mean(), color="#d62728", linestyle="--", linewidth=1.6,
                           label=f"Media: {datos_raw.mean():,.4g}")
        axes[0, i].set_title(f"Antes: {col}", fontsize=10.5, fontweight="bold")
        axes[0, i].set_xlabel("Valor original", fontsize=9)
        axes[0, i].set_ylabel("Frecuencia (granos)", fontsize=9)
        axes[0, i].legend(fontsize=8, loc="upper right")
        axes[0, i].grid(True, linestyle="--", alpha=0.35)

        datos_z = df_scaled[col]
        axes[1, i].hist(datos_z, bins=35, color=color, alpha=0.72, edgecolor="white", linewidth=0.4)
        axes[1, i].axvline(0.0, color="#d62728", linestyle="--", linewidth=1.6,
                           label=f"Media: {datos_z.mean():.2f}\nStd: {datos_z.std():.2f}")
        axes[1, i].set_title(f"Después (Z-score): {col}", fontsize=10.5, fontweight="bold")
        axes[1, i].set_xlabel("Valor estandarizado (Z)", fontsize=9)
        axes[1, i].set_ylabel("Frecuencia (granos)", fontsize=9)
        axes[1, i].set_xlim(-5, 7)
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


def graficar_curva_k_distancia(X_scaled, min_pts, eps_opt, base_dir):
    """Grafica la curva de k-distancias ordenadas para ubicar el codo y el rango de eps."""
    nn = NearestNeighbors(n_neighbors=min_pts, metric="euclidean", n_jobs=-1)
    distancias, _ = nn.fit(X_scaled).kneighbors(X_scaled)
    k_dist = np.sort(distancias[:, -1])

    p90 = float(np.percentile(k_dist, 90))
    p95 = float(np.percentile(k_dist, 95))
    idx_eps = int(np.searchsorted(k_dist, eps_opt))
    pct_debajo = (idx_eps / len(k_dist)) * 100.0

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.2))

    axes[0].plot(k_dist, color="#1f77b4", linewidth=1.8)
    axes[0].axhline(eps_opt, color="#d62728", linestyle="--", linewidth=1.8,
                    label=f"eps elegido = {eps_opt:.2f} ({pct_debajo:.1f}% de granos por debajo)")
    axes[0].axhspan(1.20, 1.80, color="#ff7f0e", alpha=0.14, label="Zona del codo evaluada (1.20 a 1.80)")
    axes[0].set_title(f"Curva Completa de {min_pts}-Distancias (Todos los Granos)", fontsize=11, fontweight="bold")
    axes[0].set_xlabel("Granos ordenados por cercanía a sus vecinos", fontsize=9.5)
    axes[0].set_ylabel(f"Distancia euclidiana al vecino #{min_pts}", fontsize=9.5)
    axes[0].legend(loc="upper left", fontsize=8.8)
    axes[0].grid(True, linestyle="--", alpha=0.4)

    inicio_zoom = int(len(k_dist) * 0.80)
    x_zoom = np.arange(inicio_zoom, len(k_dist))
    axes[1].plot(x_zoom, k_dist[inicio_zoom:], color="#1f77b4", linewidth=2.0)
    axes[1].axhline(eps_opt, color="#d62728", linestyle="--", linewidth=1.8,
                    label=f"eps elegido = {eps_opt:.2f}")
    axes[1].axhline(p90, color="#2ca02c", linestyle=":", linewidth=1.5, label=f"Percentil 90 = {p90:.2f}")
    axes[1].axhline(p95, color="#9467bd", linestyle=":", linewidth=1.5, label=f"Percentil 95 = {p95:.2f}")
    axes[1].set_ylim(0.8, 3.8)
    axes[1].set_title("Acercamiento a la Zona del Codo (Último 20% de Granos)", fontsize=11, fontweight="bold")
    axes[1].set_xlabel("Índice del grano ordenado", fontsize=9.5)
    axes[1].set_ylabel(f"Distancia euclidiana al vecino #{min_pts}", fontsize=9.5)
    axes[1].legend(loc="upper left", fontsize=8.8)
    axes[1].grid(True, linestyle="--", alpha=0.4)

    plt.suptitle(
        f"Selección del Rango de Epsilon (eps) con Gráfica de k-Distancias (MinPts = {min_pts})",
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
    axes[0, 0].plot(x_pos, sils, marker="o", linewidth=2, color="#1f77b4")
    axes[0, 0].scatter([idx_opt], [sils[idx_opt]], s=120, color="#d62728", zorder=5,
                       label=f"Elegido (eps={eps_opt:.2f})")
    for i, v in enumerate(sils):
        axes[0, 0].text(i, v + 0.015, f"{v:.4f}", ha="center", va="bottom", fontsize=8.5,
                        fontweight="bold" if i == idx_opt else "normal")
    axes[0, 0].set_title("Silhouette Score (Más cercano a 1 es mejor)", fontsize=11, fontweight="bold")
    axes[0, 0].set_xticks(x_pos)
    axes[0, 0].set_xticklabels(etiquetas_x)
    axes[0, 0].set_xlabel("Valor de eps")
    axes[0, 0].set_ylabel("Silhouette Score")
    axes[0, 0].set_ylim(0.18, 0.65)
    axes[0, 0].legend(loc="lower right", fontsize=8.8)
    axes[0, 0].grid(True, linestyle="--", alpha=0.4)

    # 2. Davies-Bouldin Index
    axes[0, 1].plot(x_pos, dbis, marker="s", linewidth=2, color="#2ca02c")
    axes[0, 1].scatter([idx_opt], [dbis[idx_opt]], s=120, color="#d62728", zorder=5,
                       label=f"Elegido (eps={eps_opt:.2f})")
    for i, v in enumerate(dbis):
        axes[0, 1].text(i, v + 0.02, f"{v:.4f}", ha="center", va="bottom", fontsize=8.5,
                        fontweight="bold" if i == idx_opt else "normal")
    axes[0, 1].set_title("Davies-Bouldin Index (Menor valor es mejor)", fontsize=11, fontweight="bold")
    axes[0, 1].set_xticks(x_pos)
    axes[0, 1].set_xticklabels(etiquetas_x)
    axes[0, 1].set_xlabel("Valor de eps")
    axes[0, 1].set_ylabel("Davies-Bouldin Index")
    axes[0, 1].set_ylim(0.40, 1.08)
    axes[0, 1].legend(loc="upper right", fontsize=8.8)
    axes[0, 1].grid(True, linestyle="--", alpha=0.4)

    # 3. Calinski-Harabasz Index
    axes[1, 0].plot(x_pos, chis, marker="^", linewidth=2, color="#9467bd")
    axes[1, 0].scatter([idx_opt], [chis[idx_opt]], s=120, color="#d62728", zorder=5,
                       label=f"Elegido (eps={eps_opt:.2f})")
    for i, v in enumerate(chis):
        axes[1, 0].text(i, v + 90, f"{v:,.0f}", ha="center", va="bottom", fontsize=8.5,
                        fontweight="bold" if i == idx_opt else "normal")
    axes[1, 0].set_title("Calinski-Harabasz Index (Mayor valor es mejor)", fontsize=11, fontweight="bold")
    axes[1, 0].set_xticks(x_pos)
    axes[1, 0].set_xticklabels(etiquetas_x)
    axes[1, 0].set_xlabel("Valor de eps")
    axes[1, 0].set_ylabel("Calinski-Harabasz Index")
    axes[1, 0].set_ylim(1800, 4600)
    axes[1, 0].legend(loc="lower right", fontsize=8.8)
    axes[1, 0].grid(True, linestyle="--", alpha=0.4)

    # 4. Porcentaje de Ruido Global y Numero de Clusters
    bar_colors = ["#d62728" if i == idx_opt else "#ff9838" for i in range(len(ruidos))]
    axes[1, 1].bar(x_pos, ruidos, color=bar_colors, alpha=0.88, width=0.58)
    for i, (pct, nc) in enumerate(zip(ruidos, clusters)):
        axes[1, 1].text(i, pct + 0.5, f"{pct:.2f}%\n({nc} clusters)", ha="center", va="bottom",
                        fontsize=8.3, fontweight="bold" if i == idx_opt else "normal")
    axes[1, 1].set_title("Porcentaje de Ruido Global y Clusters Detectados", fontsize=11, fontweight="bold")
    axes[1, 1].set_xticks(x_pos)
    axes[1, 1].set_xticklabels(etiquetas_x)
    axes[1, 1].set_xlabel("Valor de eps")
    axes[1, 1].set_ylabel("% de puntos clasificados como ruido")
    axes[1, 1].set_ylim(0, max(ruidos) * 1.24)
    axes[1, 1].grid(axis="y", linestyle="--", alpha=0.4)

    plt.suptitle(
        f"Evaluación de Métricas de Calidad en DBSCAN (MinPts = {min_pts_opt}, elegido eps = {eps_opt:.2f})",
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
    colores_clusters = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd"]
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

    etapas = ["Original\n(Dataset.csv)", "Sin duplicados\n(-68 filas)", "Final sin ruido\n(-402 filas)"]
    valores = [n_inicial, n_sin_dup, len(df_final)]
    colores_etapas = ["#6c8ebf", "#3b78b8", "#2ca02c"]
    bars1 = axes[0].bar(etapas, valores, color=colores_etapas, width=0.52)
    axes[0].set_title("Evolución del Número de Registros en la Limpieza", fontsize=11, fontweight="bold")
    axes[0].set_ylabel("Cantidad de granos")
    axes[0].set_ylim(0, n_inicial * 1.15)
    axes[0].grid(axis="y", linestyle="--", alpha=0.4)
    for bar, val in zip(bars1, valores):
        pct = (val / n_inicial) * 100.0
        axes[0].text(bar.get_x() + bar.get_width() / 2, val + 220,
                     f"{val:,}\n({pct:.2f}%)", ha="center", va="bottom", fontsize=9.5, fontweight="bold")

    conteo = df_final["Clase"].value_counts().sort_index()
    etiquetas_c = [f"Clase {c}" for c in conteo.index]
    colores_c = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd"]
    bars2 = axes[1].bar(etiquetas_c, conteo.values, color=colores_c[:len(conteo)], width=0.46)
    axes[1].set_title("Distribución Final de Clases Asignadas por DBSCAN", fontsize=11, fontweight="bold")
    axes[1].set_ylabel("Cantidad de granos")
    axes[1].set_ylim(0, conteo.max() * 1.16)
    axes[1].grid(axis="y", linestyle="--", alpha=0.4)
    for bar, val in zip(bars2, conteo.values):
        pct = (val / len(df_final)) * 100.0
        axes[1].text(bar.get_x() + bar.get_width() / 2, val + 220,
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
    ruta_csv = localizar_dataset(base_dir)

    print("ETAPA 1: PREPROCESAMIENTO Y DETECCION DE RUIDO GLOBAL CON DBSCAN\n")

    # 1. Carga y eliminacion de columnas completamente vacias
    df = pd.read_csv(ruta_csv)
    n_inicial = df.shape[0]
    print(f"[1] Carga inicial del dataset: {df.shape[0]} registros, {df.shape[1]} columnas.")

    hallazgos_vacias = detectar_columnas_vacias(df, ruta_csv)
    for h in hallazgos_vacias:
        if h["por_coma_final"]:
            print(f"    Columna {h['pos']} ({h['nombre']}) vacia al 100% por coma final en el CSV: eliminada.")
        else:
            print(f"    Columna {h['pos']} ({h['nombre']}) vacia al 100%: eliminada.")
    if hallazgos_vacias:
        df = df.drop(columns=[h["nombre"] for h in hallazgos_vacias])

    nulos_restantes = int(df.isnull().sum().sum())
    print(f"    Valores faltantes en las {df.shape[1]} variables validas: {nulos_restantes}")
    if nulos_restantes > 0:
        df = df.dropna().reset_index(drop=True)

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
    print(f"    Antes: Area media = {df['Area'].mean():.2f}, ShapeFactor2 media = {df['ShapeFactor2'].mean():.5f}")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df)
    df_scaled = pd.DataFrame(X_scaled, columns=df.columns)
    print(f"    Despues: todas las {df_scaled.shape[1]} variables con media = 0.00 y desviacion estandar = 1.00.")

    ruta_img1 = graficar_antes_despues_estandarizacion(df, df_scaled, base_dir)
    print(f"    Grafica guardada: {ruta_img1}")

    # 5. Ajuste de DBSCAN (MinPts = 2 * D = 32) y curva de k-distancias
    min_pts_opt = 2 * df_scaled.shape[1]
    eps_candidatos = [0.90, 1.20, 1.40, 1.50, 1.60, 1.80, 2.00]
    eps_opt = 1.50

    print(f"\n[5] Evaluacion de DBSCAN en 16 dimensiones (distancia euclidiana, MinPts = {min_pts_opt}):\n")
    print(f"    {'eps':>5} | {'MinPts':>6} | {'Clusters':>8} | {'Ruido (#)':>9} | {'Ruido (%)':>9} | {'Silhouette':>10} | {'Davies-B.':>9} | {'Calinski-H.':>11}")

    resultados = {}
    tabla_metricas = []

    for eps in eps_candidatos:
        db = DBSCAN(eps=eps, min_samples=min_pts_opt, metric="euclidean", n_jobs=-1)
        etiquetas = db.fit_predict(X_scaled)

        mascara_validos = etiquetas != -1
        n_clusters = len(set(etiquetas[mascara_validos]))
        n_ruido = int(np.sum(etiquetas == -1))
        pct_ruido = (n_ruido / len(etiquetas)) * 100.0

        sil = float(silhouette_score(X_scaled[mascara_validos], etiquetas[mascara_validos]))
        dbi = float(davies_bouldin_score(X_scaled[mascara_validos], etiquetas[mascara_validos]))
        chi = float(calinski_harabasz_score(X_scaled[mascara_validos], etiquetas[mascara_validos]))

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

    etiquetas_opt, n_clusters_opt, n_ruido_opt, pct_ruido_opt, sil_opt, dbi_opt, chi_opt = resultados[eps_opt]
    print(f"\n    Configuracion seleccionada: eps = {eps_opt:.2f}, MinPts = {min_pts_opt}")
    print(f"    Clusters = {n_clusters_opt}, Ruido global eliminado = {n_ruido_opt} ({pct_ruido_opt:.2f}%)")
    print(f"    Silhouette = {sil_opt:.4f}, Davies-Bouldin = {dbi_opt:.4f}, Calinski-Harabasz = {chi_opt:.1f}")

    # Proyeccion PCA 2D unicamente para visualizar el resultado de 16D
    pca_vis = PCA(n_components=2, random_state=42)
    X_pca = pca_vis.fit_transform(X_scaled)
    var_pc1 = pca_vis.explained_variance_ratio_[0] * 100.0
    var_pc2 = pca_vis.explained_variance_ratio_[1] * 100.0

    ruta_img2 = graficar_curva_k_distancia(X_scaled, min_pts_opt, eps_opt, base_dir)
    ruta_img3 = graficar_metricas_dbscan(tabla_metricas, eps_opt, min_pts_opt, base_dir)
    ruta_img4 = graficar_comparativa_dbscan(X_pca, var_pc1, var_pc2, etiquetas_opt, eps_opt, min_pts_opt, base_dir)
    print(f"    Grafica guardada: {ruta_img2}")
    print(f"    Grafica guardada: {ruta_img3}")
    print(f"    Grafica guardada: {ruta_img4}")

    # 6. Eliminacion de ruido global y asignacion de Clase
    mascara_limpia = etiquetas_opt != -1
    df_preprocesado = df_scaled[mascara_limpia].copy().reset_index(drop=True)
    df_preprocesado["Clase"] = etiquetas_opt[mascara_limpia]

    ruta_img5 = graficar_resumen_final(n_inicial, n_sin_dup, df_preprocesado, base_dir)
    print(f"    Grafica guardada: {ruta_img5}")

    print("\n[6] Distribucion final de clases asignadas:")
    conteo_clases = df_preprocesado["Clase"].value_counts().sort_index()
    for clase, cantidad in conteo_clases.items():
        porcentaje = (cantidad / len(df_preprocesado)) * 100.0
        print(f"    Clase {clase}: {cantidad:5d} granos ({porcentaje:5.2f}%)")

    ruta_salida = os.path.join(base_dir, "dataset_preprocesado.csv")
    df_preprocesado.to_csv(ruta_salida, index=False)
    print(f"\nDataset preprocesado guardado en: {ruta_salida}")
    print(f"Dimensiones finales: {df_preprocesado.shape[0]} filas x {df_preprocesado.shape[1]} columnas (16 variables + Clase).")


if __name__ == "__main__":
    main()
