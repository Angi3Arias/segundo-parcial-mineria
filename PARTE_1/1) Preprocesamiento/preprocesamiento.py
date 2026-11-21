"""
Etapa 1: Preprocesamiento de datos y deteccion de ruido global con DBSCAN.
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
from sklearn.metrics import silhouette_score, calinski_harabasz_score


def localizar_dataset(base_dir):
    """Busca Dataset.csv en la carpeta actual o en carpetas de respaldo."""
    rutas = [
        os.path.join(base_dir, "Dataset.csv"),
        os.path.join(os.getcwd(), "PARTE_1", "1) Preprocesamiento", "Dataset.csv"),
        os.path.join(os.getcwd(), "Dataset.csv"),
    ]
    for ruta in rutas:
        if os.path.exists(ruta):
            return os.path.abspath(ruta)
    raise FileNotFoundError(f"No se encontro Dataset.csv en {base_dir}")


def graficar_estandarizacion(df_raw, df_z, dir_graficas):
    """Compara 4 variables de escalas distintas antes y despues de Z-score calculando sus estadisticas reales."""
    vars_ej = [c for c in ["Area", "Perimeter", "Solidity", "ShapeFactor2"] if c in df_raw.columns]
    if len(vars_ej) < 4:
        vars_ej = df_raw.columns[:4].tolist()
    colores = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd"]

    fig, axes = plt.subplots(2, len(vars_ej), figsize=(16, 6.8))
    for i, (col, color) in enumerate(zip(vars_ej, colores)):
        s_raw = df_raw[col]
        media_raw = float(s_raw.mean())
        std_raw = float(s_raw.std(ddof=0))
        axes[0, i].hist(s_raw, bins=35, color=color, alpha=0.75, edgecolor="white", linewidth=0.4)
        axes[0, i].axvline(media_raw, color="#d62728", linestyle="--", linewidth=1.5,
                           label=f"Media: {media_raw:,.4g}\nStd: {std_raw:,.4g}")
        axes[0, i].set_title(f"Antes: {col}", fontsize=10.5, fontweight="bold")
        axes[0, i].set_xlabel("Valor original", fontsize=9)
        axes[0, i].set_ylabel("Granos", fontsize=9)
        axes[0, i].legend(fontsize=8, loc="upper right")
        axes[0, i].grid(True, linestyle="--", alpha=0.35)

        s_z = df_z[col]
        media_z = float(s_z.mean())
        std_z = float(s_z.std(ddof=0))
        axes[1, i].hist(s_z, bins=35, color=color, alpha=0.75, edgecolor="white", linewidth=0.4)
        axes[1, i].axvline(media_z, color="#d62728", linestyle="--", linewidth=1.5,
                           label=f"Media: {media_z:.2f}\nStd: {std_z:.2f}")
        axes[1, i].set_title(f"Después (Z-score): {col}", fontsize=10.5, fontweight="bold")
        axes[1, i].set_xlabel("Valor Z-score", fontsize=9)
        axes[1, i].set_ylabel("Granos", fontsize=9)
        axes[1, i].set_xlim(float(s_z.min()) - 0.5, float(s_z.max()) + 0.5)
        axes[1, i].legend(fontsize=8, loc="upper right")
        axes[1, i].grid(True, linestyle="--", alpha=0.35)

    plt.suptitle("Estandarización Z-score: Antes vs Después", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    ruta = os.path.join(dir_graficas, "1_antes_despues_estandarizacion.png")
    plt.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return ruta


def graficar_k_distancia(k_dist, min_pts, percentiles, niveles_eps, dir_graficas):
    """Grafica la curva de k-distancias Manhattan calculando los valores de eps desde sus percentiles."""
    fig, ax = plt.subplots(figsize=(10.5, 5.0))
    ax.plot(k_dist, color="#1f77b4", linewidth=2.0)

    colores = ["#2ca02c", "#d62728", "#ff7f0e"]
    estilos = [":", "--", "-."]
    for idx, (q, eps_val, color, estilo) in enumerate(zip(percentiles, niveles_eps, colores, estilos), start=1):
        ax.axhline(eps_val, color=color, linestyle=estilo, linewidth=1.8,
                   label=f"Nivel {idx} (P{q}): eps = {eps_val:.2f}")

    ax.set_ylim(0, float(np.percentile(k_dist, 99.2)) * 1.15)
    ax.set_title(f"Curva de {min_pts}-Distancias Manhattan", fontsize=12, fontweight="bold")
    ax.set_xlabel("Granos ordenados de menor a mayor distancia", fontsize=10)
    ax.set_ylabel(f"Distancia Manhattan al vecino #{min_pts}", fontsize=10)
    ax.legend(loc="upper left", fontsize=9, framealpha=0.95)
    ax.grid(True, linestyle="--", alpha=0.4)

    plt.tight_layout()
    ruta = os.path.join(dir_graficas, "2_curva_k_distancia_dbscan.png")
    plt.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return ruta


def graficar_metricas(tabla, min_pts, dir_graficas):
    """Grafica Silhouette Score, Calinski-Harabasz, % de ruido y numero de clases para cada corrida."""
    etiquetas = [r["label"] for r in tabla]
    sils = [r["sil"] for r in tabla]
    chis = [r["chi"] for r in tabla]
    ruidos = [r["pct_ruido"] for r in tabla]
    clusters = [r["n_clusters"] for r in tabla]
    x = np.arange(len(etiquetas))
    idx_final = len(etiquetas) - 1

    fig, axes = plt.subplots(1, 3, figsize=(17.5, 4.8))

    colores_sil = ["#1f77b4"] * idx_final + ["#d62728"]
    bars1 = axes[0].bar(x, sils, color=colores_sil, width=0.52, alpha=0.88)
    for i, (bar, v) in enumerate(zip(bars1, sils)):
        axes[0].text(bar.get_x() + bar.get_width() / 2, v + max(sils) * 0.025, f"{v:.4f}",
                     ha="center", va="bottom", fontsize=9.2, fontweight="bold" if i == idx_final else "normal")
    axes[0].set_title("Silhouette Score (Más cercano a 1 es mejor)", fontsize=10.5, fontweight="bold")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(etiquetas, fontsize=8.8)
    axes[0].set_ylabel("Silhouette Score")
    axes[0].set_ylim(0, max(sils) * 1.22)
    axes[0].grid(axis="y", linestyle="--", alpha=0.4)

    colores_chi = ["#9467bd"] * idx_final + ["#d62728"]
    bars2 = axes[1].bar(x, chis, color=colores_chi, width=0.52, alpha=0.88)
    for i, (bar, v) in enumerate(zip(bars2, chis)):
        axes[1].text(bar.get_x() + bar.get_width() / 2, v + max(chis) * 0.025, f"{v:,.0f}",
                     ha="center", va="bottom", fontsize=9.2, fontweight="bold" if i == idx_final else "normal")
    axes[1].set_title("Calinski-Harabasz Index (Mayor es mejor)", fontsize=10.5, fontweight="bold")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(etiquetas, fontsize=8.8)
    axes[1].set_ylabel("Calinski-Harabasz Index")
    axes[1].set_ylim(0, max(chis) * 1.22)
    axes[1].grid(axis="y", linestyle="--", alpha=0.4)

    colores_r = ["#ff9838"] * idx_final + ["#d62728"]
    bars3 = axes[2].bar(x, ruidos, color=colores_r, width=0.52, alpha=0.88)
    for i, (bar, pct, nc) in enumerate(zip(bars3, ruidos, clusters)):
        axes[2].text(bar.get_x() + bar.get_width() / 2, pct + max(ruidos) * 0.025, f"{pct:.2f}%\n({nc} clases)",
                     ha="center", va="bottom", fontsize=8.8, fontweight="bold" if i == idx_final else "normal")
    axes[2].set_title("Porcentaje de Ruido Global y Clases", fontsize=10.5, fontweight="bold")
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(etiquetas, fontsize=8.8)
    axes[2].set_ylabel("% de ruido global")
    axes[2].set_ylim(0, max(ruidos) * 1.26)
    axes[2].grid(axis="y", linestyle="--", alpha=0.4)

    plt.suptitle(f"Métricas de Calidad en DBSCAN — Distancia Manhattan (MinPts = {min_pts})",
                 fontsize=12.5, fontweight="bold", y=1.02)
    plt.tight_layout()
    ruta = os.path.join(dir_graficas, "3_metricas_calidad_dbscan.png")
    plt.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return ruta


def graficar_clusters_dbscan(X_pca, var_pc1, var_pc2, etiquetas, dir_graficas):
    """Muestra antes, durante y despues de eliminar el ruido global calculando las clases detectadas."""
    colores = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd", "#17becf", "#e377c2", "#8c564b", "#bcbd22"]
    clases = sorted([c for c in set(etiquetas) if c != -1])
    mascara_ruido = etiquetas == -1

    fig, axes = plt.subplots(1, 3, figsize=(17.5, 5.4))

    axes[0].scatter(X_pca[:, 0], X_pca[:, 1], s=8, alpha=0.25, color="#3b5998", edgecolors="none")
    axes[0].set_title("1. Datos sin Etiquetas", fontsize=11, fontweight="bold")

    for idx, c in enumerate(clases):
        mask = etiquetas == c
        axes[1].scatter(X_pca[mask, 0], X_pca[mask, 1], s=9, alpha=0.5, color=colores[idx % len(colores)],
                        label=f"Clase {c} ({int(np.sum(mask)):,})", edgecolors="none")
    axes[1].scatter(X_pca[mascara_ruido, 0], X_pca[mascara_ruido, 1], s=14, alpha=0.75,
                    color="#d62728", marker="x", label=f"Ruido ({int(np.sum(mascara_ruido)):,})")
    axes[1].set_title(f"2. DBSCAN: {len(clases)} Clases y Ruido Global", fontsize=11, fontweight="bold")
    axes[1].legend(loc="upper left", fontsize=8.5, framealpha=0.92)

    for idx, c in enumerate(clases):
        mask = etiquetas == c
        axes[2].scatter(X_pca[mask, 0], X_pca[mask, 1], s=9, alpha=0.5, color=colores[idx % len(colores)],
                        label=f"Clase {c} ({int(np.sum(mask)):,})", edgecolors="none")
    axes[2].set_title("3. Dataset Final (Sin Ruido)", fontsize=11, fontweight="bold")
    axes[2].legend(loc="upper left", fontsize=8.5, framealpha=0.92)

    for ax in axes:
        ax.set_xlabel(f"PC1 ({var_pc1:.2f}%)")
        ax.set_ylabel(f"PC2 ({var_pc2:.2f}%)")
        ax.grid(True, linestyle="--", alpha=0.4)

    plt.suptitle("Agrupamiento con DBSCAN y Eliminación de Ruido Global (Vista PCA 2D)",
                 fontsize=12.5, fontweight="bold", y=1.02)
    plt.tight_layout()
    ruta = os.path.join(dir_graficas, "4_dbscan_clustering_y_ruido.png")
    plt.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return ruta


def graficar_resumen_clases(n_inicial, n_sin_dup, df_final, dir_graficas):
    """Muestra la evolucion de filas en la limpieza y la distribucion de las clases detectadas."""
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.8))

    etapas = [
        "Original",
        f"Sin duplicados\n(-{n_inicial - n_sin_dup:,})",
        f"Sin ruido global\n(-{n_sin_dup - len(df_final):,})",
    ]
    valores = [n_inicial, n_sin_dup, len(df_final)]
    bars1 = axes[0].bar(etapas, valores, color=["#6c8ebf", "#3b78b8", "#2ca02c"], width=0.5)
    axes[0].set_title("Registros tras la Limpieza", fontsize=11, fontweight="bold")
    axes[0].set_ylabel("Cantidad de granos")
    axes[0].set_ylim(0, n_inicial * 1.16)
    axes[0].grid(axis="y", linestyle="--", alpha=0.4)
    for bar, val in zip(bars1, valores):
        axes[0].text(bar.get_x() + bar.get_width() / 2, val + n_inicial * 0.016,
                     f"{val:,}\n({val / n_inicial * 100:.2f}%)", ha="center", va="bottom", fontsize=9.2, fontweight="bold")

    conteo = df_final["Clase"].value_counts().sort_index()
    colores = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd", "#17becf", "#e377c2", "#8c564b", "#bcbd22"]
    bars2 = axes[1].bar([f"Clase {c}" for c in conteo.index], conteo.values, color=colores[:len(conteo)], width=0.52)
    axes[1].set_title("Distribución Final de Clases", fontsize=11, fontweight="bold")
    axes[1].set_ylabel("Cantidad de granos")
    axes[1].set_ylim(0, conteo.max() * 1.18)
    axes[1].grid(axis="y", linestyle="--", alpha=0.4)
    for bar, val in zip(bars2, conteo.values):
        axes[1].text(bar.get_x() + bar.get_width() / 2, val + conteo.max() * 0.018,
                     f"{val:,}\n({val / len(df_final) * 100:.2f}%)", ha="center", va="bottom", fontsize=9.2, fontweight="bold")

    plt.suptitle("Resumen Final del Preprocesamiento", fontsize=12.5, fontweight="bold", y=1.02)
    plt.tight_layout()
    ruta = os.path.join(dir_graficas, "5_resumen_preprocesamiento_y_clases.png")
    plt.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return ruta


def dbscan_multinivel(X_scaled, niveles_eps, min_pts):
    """
    Ejecuta DBSCAN en 3 niveles de eps (P20, P50 y P90):
    1) P90 (nivel de menor densidad) separa el ruido global real (-1) de las regiones validas.
    2) P20 y P50 identifican los nucleos densos internos dentro de las regiones validas.
    3) Cada punto valido de P90 se asigna a su nucleo interno mas cercano (sin perder datos validos como ruido).
    """
    corridas = [
        DBSCAN(eps=e, min_samples=min_pts, metric="manhattan", n_jobs=-1).fit_predict(X_scaled)
        for e in niveles_eps
    ]
    l_alta, l_media, l_baja = corridas

    # Identificar los nucleos internos densos con P20 y P50
    nucleos = np.full(len(X_scaled), -1, dtype=int)
    nid = 0
    for c in sorted(set(l_media) - {-1}):
        mc = l_media == c
        sub = sorted(set(l_alta[mc]) - {-1})
        if len(sub) >= 2:
            for s in sub:
                nucleos[mc & (l_alta == s)] = nid
                nid += 1
        else:
            nucleos[mc] = nid
            nid += 1

    # En cada region valida de P90 (libre de ruido global), asignar cada punto a su nucleo interno
    etiquetas = np.full(len(X_scaled), -1, dtype=int)
    nueva_clase = 0
    for c in sorted(set(l_baja) - {-1}):
        mc = l_baja == c
        nucs = sorted(set(nucleos[mc]) - {-1})
        if len(nucs) >= 2:
            mn = mc & (nucleos != -1)
            _, idx = NearestNeighbors(n_neighbors=1, metric="manhattan", n_jobs=-1).fit(X_scaled[mn]).kneighbors(X_scaled[mc])
            asignados = nucleos[mn][idx[:, 0]]
            for n_id in sorted(set(asignados)):
                etiquetas[np.where(mc)[0][asignados == n_id]] = nueva_clase
                nueva_clase += 1
        else:
            etiquetas[mc] = nueva_clase
            nueva_clase += 1

    return corridas, etiquetas


def evaluar_etiquetas(X_scaled, etiquetas, label, min_pts):
    """Calcula numero de clusters, ruido, Silhouette Score (Manhattan) y Calinski-Harabasz."""
    validos = etiquetas != -1
    n_clusters = len(set(etiquetas[validos]))
    n_ruido = int(np.sum(etiquetas == -1))
    pct_ruido = (n_ruido / len(etiquetas)) * 100.0
    if n_clusters >= 2:
        sil = float(silhouette_score(X_scaled[validos], etiquetas[validos], metric="manhattan"))
        chi = float(calinski_harabasz_score(X_scaled[validos], etiquetas[validos]))
    else:
        sil, chi = 0.0, 0.0
    return {
        "label": label,
        "min_pts": min_pts,
        "n_clusters": n_clusters,
        "n_ruido": n_ruido,
        "pct_ruido": pct_ruido,
        "sil": sil,
        "chi": chi,
    }


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dir_graficas = os.path.join(base_dir, "GRAFICAS")
    os.makedirs(dir_graficas, exist_ok=True)
    ruta_csv = localizar_dataset(base_dir)

    print("ETAPA 1: PREPROCESAMIENTO Y DETECCION DE RUIDO GLOBAL CON DBSCAN\n")

    # 1. Cargar datos y quitar columnas vacias, filas con nulos, duplicados y columnas constantes
    df = pd.read_csv(ruta_csv)
    n_inicial, cols_inicial = df.shape
    cols_vacias = [c for c in df.columns if df[c].isnull().all()]
    df = df.drop(columns=cols_vacias).dropna()

    n_duplicados = int(df.duplicated().sum())
    df = df.drop_duplicates(keep="first").reset_index(drop=True)
    n_sin_dup = df.shape[0]

    varianzas = df.var()
    cols_constantes = varianzas[varianzas == 0].index.tolist()
    if cols_constantes:
        df = df.drop(columns=cols_constantes)

    print(f"[1] Limpieza inicial: {n_inicial} filas x {cols_inicial} columnas.")
    print(f"    Columnas vacias eliminadas: {', '.join(cols_vacias) if cols_vacias else 'ninguna'}")
    print(f"    Duplicados eliminados: {n_duplicados} (quedan {n_sin_dup} filas unicas y {df.shape[1]} variables).")
    print(f"    Columnas con varianza cero: {len(cols_constantes)}")

    # 2. Estandarizacion Z-score
    X_scaled = StandardScaler().fit_transform(df)
    df_scaled = pd.DataFrame(X_scaled, columns=df.columns)
    graficar_estandarizacion(df, df_scaled, dir_graficas)
    media_z = float(df_scaled.mean().mean())
    std_z = float(df_scaled.std(ddof=0).mean())
    print(f"\n[2] Estandarizacion Z-score aplicada (media = {media_z:.2f}, desviacion estandar = {std_z:.2f}).")

    # 3. Curva de k-distancias Manhattan (MinPts = 2 * D) y DBSCAN multinivel
    min_pts = 2 * df_scaled.shape[1]
    distancias, _ = NearestNeighbors(n_neighbors=min_pts, metric="manhattan", n_jobs=-1).fit(X_scaled).kneighbors(X_scaled)
    k_dist = np.sort(distancias[:, -1])

    percentiles = (20, 50, 90)
    niveles_eps = [round(float(np.percentile(k_dist, q)) * 20) / 20 for q in percentiles]
    graficar_k_distancia(k_dist, min_pts, percentiles, niveles_eps, dir_graficas)

    corridas, etiquetas_final = dbscan_multinivel(X_scaled, niveles_eps, min_pts)

    # 4. Evaluar metricas de calidad (Silhouette Score, clases y % de ruido)
    tabla = [
        evaluar_etiquetas(X_scaled, etiquetas_nivel, f"P{q} (eps={e:.2f})", min_pts)
        for q, e, etiquetas_nivel in zip(percentiles, niveles_eps, corridas)
    ]
    tabla.append(evaluar_etiquetas(X_scaled, etiquetas_final, "Multinivel", min_pts))

    print(f"\n[3] Evaluacion de DBSCAN (distancia Manhattan, MinPts = {min_pts}):\n")
    print(f"    {'Configuracion':>14} | {'Clases':>6} | {'Ruido (#)':>9} | {'Ruido (%)':>9} | {'Silhouette':>10} | {'Calinski-H.':>11}")
    for r in tabla:
        print(f"    {r['label']:>14} | {r['n_clusters']:6d} | {r['n_ruido']:9d} | {r['pct_ruido']:8.2f}% | {r['sil']:10.4f} | {r['chi']:11.1f}")

    # 5. Generar graficas de metricas, clusters y resumen
    pca_vis = PCA(n_components=2, random_state=42)
    X_pca = pca_vis.fit_transform(X_scaled)
    var_pc1, var_pc2 = pca_vis.explained_variance_ratio_ * 100.0

    graficar_metricas(tabla, min_pts, dir_graficas)
    graficar_clusters_dbscan(X_pca, var_pc1, var_pc2, etiquetas_final, dir_graficas)

    # 6. Eliminar ruido global, asignar Clase y guardar CSV
    df_final = df_scaled[etiquetas_final != -1].copy().reset_index(drop=True)
    df_final["Clase"] = etiquetas_final[etiquetas_final != -1]
    graficar_resumen_clases(n_inicial, n_sin_dup, df_final, dir_graficas)

    ruta_salida = os.path.join(base_dir, "dataset_preprocesado.csv")
    df_final.to_csv(ruta_salida, index=False)

    print("\n[4] Clases asignadas en el dataset final:")
    for clase, cantidad in df_final["Clase"].value_counts().sort_index().items():
        print(f"    Clase {clase}: {cantidad:5d} granos ({cantidad / len(df_final) * 100:5.2f}%)")
    print(f"\nGuardado: {ruta_salida} ({df_final.shape[0]} filas x {df_final.shape[1]} columnas).")


if __name__ == "__main__":
    main()
