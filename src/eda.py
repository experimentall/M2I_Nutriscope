import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from IPython.display import Image, display

def figure(fig: plt.Figure, nom: str) -> None:
    """sauvegarde dans figures/ puis affiche l'image."""

    output_file = os.path.join("figures", f"{nom}.png")

    fig.savefig(output_file, bbox_inches="tight", dpi=150)

    plt.close(fig)

    display(Image(filename=output_file))

def resume_univarie(s: pd.Series) -> pd.Series:
    """
    Calcule les statistiques descriptives.
    """
    x = s.dropna()
    if len(x) == 0:
        return pd.Series(dtype=float)
    
    q1, med, q3 = x.quantile([0.25, 0.5, 0.75])
    return pd.Series({
        "n": len(x),
        "manquants": s.isna().sum(),
        "moyenne": x.mean(),
        "mediane": med,
        "ecart_type": x.std(),
        "IQR": q3 - q1,
        "MAD": stats.median_abs_deviation(x),
        "CV": x.std() / x.mean() if x.mean() != 0 else np.nan,
        "asymetrie": x.skew(),
        "aplatissement": x.kurt(),
        "min": x.min(),
        "max": x.max()
    })

def profil_par_rayon(df: pd.DataFrame, colonnes: list, min_n: int = 30):
    """
    Calcule les statistiques descriptives par rayon pour une liste de nutriments.
    Écarte et liste les rayons possédant moins de min_n produits.
    """
    # Calcul des effectifs par rayon
    g = df.groupby("pnns_groups_1", observed=True)
    effectifs = g.size()
    
    # Séparation des rayons selon le seuil de taille minimale
    rayons_ok = effectifs[effectifs >= min_n].index
    petits = effectifs[effectifs < min_n]
    
    # Définition des fonctions d'agrégation personnalisées pour les quartiles
    def q25(x): return x.quantile(0.25)
    def q75(x): return x.quantile(0.75)
    
    # Agrégation des statistiques demandées
    resultat = (df[df["pnns_groups_1"].isin(rayons_ok)]
                .groupby("pnns_groups_1", observed=True)[colonnes]
                .agg(["median", q25, q75, "mean", "count"]))
    
    return resultat, petits

def cramers_v(contingency_table: pd.DataFrame) -> float:
    """
    Calcule le coefficient V de Cramér pour mesurer l'association entre deux variables.
    """
    chi2 = stats.chi2_contingency(contingency_table)[0]
    n = contingency_table.sum().sum()
    k = min(contingency_table.shape)
    if n == 0 or k <= 1:
        return 0.0
    return np.sqrt(chi2 / (n * (k - 1)))

def completude_par_groupe(df: pd.DataFrame, groupe: str, colonnes: list, min_n: int = 20) -> pd.DataFrame:
    """
    Calcule le taux de présence de chaque nutriment clé, le taux de fiches complètes,
    et la présence du Nutri-Score par groupe d'une variable catégorielle (rayon ou marque).
    Filtre les groupes pour ne garder que ceux ayant au moins min_n observations.
    """
    # Filtrage des groupes par taille minimale de l'effectif
    counts = df[groupe].value_counts()
    groupes_valides = counts[counts >= min_n].index
    df_filtré = df[df[groupe].isin(groupes_valides)].copy()
    
    if len(df_filtré) == 0:
        return pd.DataFrame()
    
    # Calcul des indicateurs de complétude sous forme booléenne
    df_filtré['fiches_completes'] = df_filtré[colonnes].notna().all(axis=1)
    df_filtré['presence_score'] = df_filtré['nutriscore_score'].notna()
    
    # Préparation du dictionnaire d'agrégation (taux en %)
    agg_dict = {col: lambda x: x.notna().mean() * 100 for col in colonnes}
    agg_dict['fiches_completes'] = lambda x: x.mean() * 100
    agg_dict['presence_score'] = lambda x: x.mean() * 100
    
    # Agrégation par groupe
    grouped = df_filtré.groupby(groupe, observed=True)
    resultat = grouped.agg(agg_dict)
    resultat['n'] = grouped.size()
    
    # Renommage des colonnes pour plus de clarté
    nom_colonnes = {col: f"taux_{col}" for col in colonnes}
    nom_colonnes['fiches_completes'] = 'taux_fiches_completes'
    nom_colonnes['presence_score'] = 'taux_presence_score'
    resultat = resultat.rename(columns=nom_colonnes)
    
    # Réorganisation des colonnes avec l'effectif 'n' en premier position
    ordre_colonnes = ['n'] + [c for c in resultat.columns if c != 'n']
    return resultat[ordre_colonnes]


def incoherences_metier(df: pd.DataFrame) -> pd.DataFrame:
    """
    Détecte les incohérences pour chaque produit.
    Retourne un DataFrame de drapeaux booléens (True si incohérence détectée).
    """
    inc_df = pd.DataFrame(index=df.index)
    
    # Sucres supérieurs aux glucides totaux
    inc_df['sucres_gt_glucides'] = (df['sugars_100g'] > df['carbohydrates_100g']).fillna(False)
    
    # Acides gras saturés supérieurs aux lipides totaux
    inc_df['satures_gt_lipides'] = (df['saturated-fat_100g'] > df['fat_100g']).fillna(False)
    
    # Écart sur la relation stricte Sel = 2.5 * Sodium (tolérance de 0.05g due aux arrondis)
    écart_sel_sodium = (df['salt_100g'] - 2.5 * df['sodium_100g']).abs()
    inc_df['sel_incoherent_sodium'] = (df['salt_100g'].notna() & df['sodium_100g'].notna() & (écart_sel_sodium > 0.05))
    
    # Énergie déclarée incohérente avec l'énergie théorique calculée (Seuil > 150 kcal)
    # Formule de conversion Atwater classique : 9*Lipides + 4*Glucides + 4*Protéines + 2*Fibres
    fibres_nettoyees = df['fiber_100g'].fillna(0)
    energie_calculée = (9 * df['fat_100g'] + 
                        4 * df['carbohydrates_100g'] + 
                        4 * df['proteins_100g'] + 
                        2 * fibres_nettoyees)
    écart_energie = (df['energy-kcal_100g'] - energie_calculée).abs()
    inc_df['energie_incoherente'] = (df['energy-kcal_100g'].notna() & df['fat_100g'].notna() & 
                                     df['carbohydrates_100g'].notna() & df['proteins_100g'].notna() & 
                                     (écart_energie > 150))
    
    # Énergie déclarée nulle alors que des macronutriments énergétiques sont présents
    somme_macros = df[['fat_100g', 'carbohydrates_100g', 'proteins_100g']].sum(axis=1)
    inc_df['energie_nulle_macros_presentes'] = (df['energy-kcal_100g'] == 0) & (somme_macros > 1.0)
    
    return inc_df

def correlations_nutriscore(df: pd.DataFrame, colonnes: list, cible: str, min_n: int = 30) -> pd.DataFrame:
    """
    Calcule les corrélations de Pearson et Spearman entre une liste de nutriments et une cible.
    Filtre par effectif minimal et trie par la valeur absolue du coefficient de Spearman.
    """
    lignes = []
    for col in colonnes:
        # Élimination des valeurs manquantes par paire pour un calcul propre
        paire_valide = df[[col, cible]].dropna()
        n_paires = len(paire_valide)
        
        if n_paires >= min_n:
            r_pearson = paire_valide[col].corr(paire_valide[cible], method="pearson")
            rho_spearman = paire_valide[col].corr(paire_valide[cible], method="spearman")
            lignes.append({
                "variable": col,
                "n": n_paires,
                "pearson": r_pearson,
                "spearman": rho_spearman,
                "abs_spearman": abs(rho_spearman)
            })
            
    if not lignes:
        return pd.DataFrame()
        
    res_df = pd.DataFrame(lignes).set_index("variable")
    res_df = res_df.sort_values(by="abs_spearman", ascending=False)
    return res_df.drop(columns=["abs_spearman"])

def paires_redondantes(matrice: pd.DataFrame, seuil: float = 0.8) -> pd.DataFrame:
    """
    Identifie les paires de variables dont la corrélation (en valeur absolue) 
    dépasse le seuil spécifié, en évitant les doublons (miroir et diagonale).
    """
    lignes = []
    colonnes = matrice.columns
    for i in range(len(colonnes)):
        for j in range(i + 1, len(colonnes)):
            valeur = matrice.iloc[i, j]
            if abs(valeur) >= seuil:
                lignes.append({
                    "Var1": colonnes[i],
                    "Var2": colonnes[j],
                    "Correlation": valeur
                })
    return pd.DataFrame(lignes)

def correlations_par_rayon(df: pd.DataFrame, colonne: str, cible: str) -> pd.DataFrame:
    """
    Calcule la corrélation de Pearson et Spearman pour un nutriment donné et une cible,
    stratifiée pour chaque rayon (pnns_groups_1) ayant au moins 30 paires valides.
    """
    lignes = []
    # pnns_groups_1 est géré via la constante globale RAYON du projet
    for rayon, sous_df in df.groupby("pnns_groups_1", observed=True):
        paire_valide = sous_df[[colonne, cible]].dropna()
        n_paires = len(paire_valide)
        
        if n_paires >= 30:
            r_pearson = paire_valide[colonne].corr(paire_valide[cible], method="pearson")
            rho_spearman = paire_valide[colonne].corr(paire_valide[cible], method="spearman")
            lignes.append({
                "rayon": rayon,
                "n": n_paires,
                "pearson": r_pearson,
                "spearman": rho_spearman
            })
            
    return pd.DataFrame(lignes).set_index("rayon")

def zscore_robuste(s: pd.Series) -> pd.Series:
    """
    Calcule le Z-score robuste d'une série en utilisant la médiane 
    et la MAD (scale='normal' applique le coefficient multiplicateur 1.4826).
    """
    x = s.dropna()
    if len(x) == 0:
        return pd.Series(np.nan, index=s.index)
    
    med = x.median()
    mad = stats.median_abs_deviation(x, scale="normal")
    
    if mad == 0:
        # Si la MAD est nulle, on initialise une série de NaN
        res = pd.Series(np.nan, index=s.index)
        # Les valeurs égales à la médiane ont un score de 0.0
        res[s == med] = 0.0
        # Les intrus (valides et différents de la med) prennent +inf ou -inf selon leur sens
        intrus = s.notna() & (s != med)
        res[intrus] = np.sign(s[intrus] - med) * np.inf
        return res
        
    return (s - med) / mad

def extremes_restants(df: pd.DataFrame, colonnes: list, seuil: float = 3.5) -> pd.DataFrame:
    """
    Identifie les valeurs aberrantes à plus de 'seuil' MAD de la médiane de leur rayon.
    Retourne les résultats au format long, triés par z décroissant.
    """
    RAYON = "pnns_groups_1"
    records = []
    
    # Calcul des Z-scores robustes de manière stratifiée par rayon
    for rayon, group in df.groupby(RAYON, observed=True):
        for col in colonnes:
            s_col = group[col]
            z = zscore_robuste(s_col)
            
            # Isolement des index dépassant le seuil en valeur absolue
            idx_extremes = z[z.abs() > seuil].index
            
            for idx in idx_extremes:
                records.append({
                    "code": df.loc[idx, "code"],
                    "product_name": df.loc[idx, "product_name"],
                    "rayon": rayon,
                    "variable": col,
                    "valeur": df.loc[idx, col],
                    "zscore": z.loc[idx],
                    "abs_zscore": abs(z.loc[idx])
                })
                
    if not records:
        return pd.DataFrame(columns=["code", "product_name", "rayon", "variable", "valeur", "zscore"])
        
    res_df = pd.DataFrame(records)
    res_df = res_df.sort_values(by="abs_zscore", ascending=False)
    return res_df.drop(columns=["abs_zscore"])

def comparer_deux_groupes(a: pd.Series, b: pd.Series) -> dict:
    """
    Compare deux groupes quantitatifs indépendants.
    Retourne un dictionnaire de statistiques et de p-value.
    """
    a_clean = a.dropna().to_numpy()
    b_clean = b.dropna().to_numpy()
    
    n_a, n_b = len(a_clean), len(b_clean)
    
    # Sécurité : si un des groupes est vide, on renvoie des valeurs nulles
    if n_a == 0 or n_b == 0:
        return {
            "n_a": n_a, "n_b": n_b, "med_a": np.nan, "med_b": np.nan,
            "diff_med": np.nan, "cohen_d": np.nan, "p_value": np.nan
        }
        
    med_a = np.median(a_clean)
    med_b = np.median(b_clean)
    
    # Calcul du d de Cohen
    var_a = np.var(a_clean, ddof=1) if n_a > 1 else 0.0
    var_b = np.var(b_clean, ddof=1) if n_b > 1 else 0.0
    
    if n_a + n_b > 2 and (var_a > 0 or var_b > 0):
        pooled_std = np.sqrt(((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2))
        cohen_d = (np.mean(b_clean) - np.mean(a_clean)) / pooled_std if pooled_std != 0 else 0.0
    else:
        cohen_d = 0.0
        
    # Test de Mann-Whitney U sécurisé
    try:
        _, p_value = stats.mannwhitneyu(a_clean, b_clean, alternative="two-sided")
    except ValueError:
        p_value = 1.0
        
    return {
        "n_a": n_a,
        "n_b": n_b,
        "med_a": med_a,
        "med_b": med_b,
        "diff_med": med_b - med_a,
        "cohen_d": cohen_d,
        "p_value": p_value
    }
