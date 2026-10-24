import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from unittest.mock import patch  
from src.eda import (
    figure,
    resume_univarie,
    profil_par_rayon,
    completude_par_groupe,
    incoherences_metier,
    correlations_nutriscore,
    paires_redondantes,
    comparer_deux_groupes,
    extremes_restants
)

def test_figure_cree_le_fichier_png(monkeypatch):
    """Vérifie que la fonction sauvegarde bien le fichier dans 'figures/' et ferme la figure."""
    nom_test = "graphique_test"

    dossier_cible = Path("tests/figures")
    os.makedirs(dossier_cible, exist_ok=True)
    fichier_attendu = dossier_cible / f"{nom_test}.png"
    
    # On déplace temporairement le répertoire de travail dans './tests'
    monkeypatch.chdir("tests")
    
    plt.switch_backend("Agg")
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
    fignum = fig.number

    # Exécution avec mock de l'affichage pour éviter l'erreur hors-notebook
    with patch("src.eda.display") as mock_display:
        figure(fig, nom_test)
        
        monkeypatch.undo()

        assert fichier_attendu.exists(), "Le fichier PNG n'a pas été généré."
        assert fichier_attendu.stat().st_size > 0, "Le fichier PNG généré est vide."
        assert not plt.fignum_exists(fignum), "La figure Matplotlib n'a pas été fermée."
        mock_display.assert_called_once()
        
    # Nettoyage
    if fichier_attendu.exists():
        os.remove(fichier_attendu)

def test_pipeline_eda():
    # Test de resume_univarie sur une série constante
    serie_constante = pd.Series([10.0, 10.0, 10.0, 10.0, np.nan])
    res_constante = resume_univarie(serie_constante)
    assert res_constante["n"] == 4, "Erreur sur le compte des effectifs"
    assert res_constante["manquants"] == 1, "Erreur sur le compte des manquants"
    assert res_constante["moyenne"] == 10.0, "Erreur de calcul de la moyenne"
    assert res_constante["IQR"] == 0.0, "L'IQR d'une constante doit être nul"
    assert res_constante["ecart_type"] == 0.0, "L'écart-type d'une constante doit être nul"
    print("Test 1 (resume_univarie - constante) : OK")

    # Test de filtrage des petits rayons dans profil_par_rayon
    df_test = pd.DataFrame({
        "pnns_groups_1": ["Rayon_A"] * 40 + ["Rayon_B"] * 15,
        "sugars_100g": np.random.uniform(0, 50, 55)
    })
    res_profil, exclus = profil_par_rayon(df_test, ["sugars_100g"], min_n=30)
    assert "Rayon_A" in res_profil.index, "Le grand rayon aurait dû être conservé"
    assert "Rayon_B" in exclus.index, "Le petit rayon aurait dû être écarté"
    assert exclus["Rayon_B"] == 15, "Mauvais décompte de l'effectif du rayon exclu"
    print("Test 2 (profil_par_rayon - filtrage min_n) : OK")

    # Test de cohérence des indicateurs de forme/position
    serie_asymetrique = pd.Series([1, 2, 3, 4, 100]) # Forte valeur extrême à droite
    res_asym = resume_univarie(serie_asymetrique)
    assert res_asym["asymetrie"] > 0, "La distribution doit présenter une asymétrie positive"
    assert res_asym["moyenne"] > res_asym["mediane"], "La moyenne doit être supérieure à la médiane"
    print("Test 3 (resume_univarie - cohérence asymétrie) : OK")

# test_pipeline_eda()

def test_pipeline_qualite_completude():
    # Données pour tester la complétude
    df_test_comp = pd.DataFrame({
        "brands": ["Marque_A"] * 21 + ["Marque_B"] * 5,
        "sugars_100g": [10.0] * 26,
        "fiber_100g": [5.0] * 20 + [None] * 6, # 1 manquant pour Marque_A, tous pour Marque_B
        "nutriscore_score": [12] * 26
    })
    
    res_comp = completude_par_groupe(df_test_comp, "brands", ["sugars_100g", "fiber_100g"], min_n=20)
    
    # Tests complétude
    assert "Marque_A" in res_comp.index
    assert "Marque_B" not in res_comp.index, "Marque_B a un effectif insuffisant (<20) et doit être filtrée"
    assert res_comp.loc["Marque_A", "n"] == 21
    assert res_comp.loc["Marque_A", "taux_fiches_completes"] == (20/21)*100
    print("Test 1 (completude_par_groupe - taux et filtrage) : OK")

    # Données pour tester les incohérences métier
    df_test_inc = pd.DataFrame({
        "sugars_100g":        [15.0, 5.0,  0.0],
        "carbohydrates_100g": [10.0, 10.0, 0.0], # Cas 1 : sucres > glucides
        "saturated-fat_100g": [2.0,  8.0,  0.0], 
        "fat_100g":           [10.0, 5.0,  0.0], # Cas 2 : saturés > lipides
        "salt_100g":          [0.5,  0.5,  0.0],
        "sodium_100g":        [0.2,  0.1,  0.0], # Cas 2 : sel (0.5) != 2.5 * sodium (0.25)
        "proteins_100g":      [0.0,  0.0,  5.0],
        "fiber_100g":         [0.0,  0.0,  0.0],
        "energy-kcal_100g":   [190,  105,  0.0]  # Cas 3 : énergie nulle mais protéines présentes
    })
    
    res_inc = incoherences_metier(df_test_inc)
    
    # Tests incohérences
    assert res_inc.loc[0, "sucres_gt_glucides"] == True
    assert res_inc.loc[1, "satures_gt_lipides"] == True
    assert res_inc.loc[1, "sel_incoherent_sodium"] == True
    assert res_inc.loc[2, "energie_nulle_macros_presentes"] == True
    print("Test 2 (incoherences_metier - flags d'anomalies) : OK")

def test_pipeline_correlations():
    # Génération de données parfaites : relation linéaire et monotone
    x = np.linspace(1, 100, 50)
    y_linear = 2 * x + 5  # Relation parfaitement linéaire -> Pearson = 1, Spearman = 1
    y_monotone = np.log(x)  # Relation monotone non linéaire -> Pearson < 1, Spearman = 1
    
    df_test_perfect = pd.DataFrame({
        "x": x,
        "y_linear": y_linear,
        "y_monotone": y_monotone,
        "cible": x
    })
    
    # Test des corrélations exactes
    res_linear = correlations_nutriscore(df_test_perfect, ["y_linear"], "cible")
    assert np.isclose(res_linear.loc["y_linear", "pearson"], 1.0), "Pearson doit être égal à 1 sur une droite"
    assert np.isclose(res_linear.loc["y_linear", "spearman"], 1.0), "Spearman doit être égal à 1 sur une droite"
    
    res_monotone = correlations_nutriscore(df_test_perfect, ["y_monotone"], "cible")
    assert res_monotone.loc["y_monotone", "pearson"] < 1.0, "Pearson doit être strictement inférieur à 1 sur une courbe"
    assert np.isclose(res_monotone.loc["y_monotone", "spearman"], 1.0), "Spearman doit être égal à 1 sur une courbe"
    print("Test 1 (Validation mathématique Pearson/Spearman) : OK")

    # Test de détection de la paire redondante Sel / Sodium
    df_test_salt_sodium = pd.DataFrame({
        "salt_100g": [0.25, 0.5, 1.25, 2.5, 0.0],
        "sodium_100g": [0.1, 0.2, 0.5, 1.0, 0.0]  # Relation stricte Sel = 2.5 * Sodium
    })
    
    matrice_spearman = df_test_salt_sodium.corr(method="spearman")
    df_redondances = paires_redondantes(matrice_spearman, seuil=0.8)
    
    assert len(df_redondances) == 1, "La paire redondante Sel/Sodium n'a pas été détectée"
    assert df_redondances.iloc[0]["Var1"] == "salt_100g"
    assert df_redondances.iloc[0]["Var2"] == "sodium_100g"
    assert np.isclose(df_redondances.iloc[0]["Correlation"], 1.0), "La corrélation Sel/Sodium doit être de 1.0"
    print("Test 2 (Détection de la colinéarité Sel / Sodium) : OK")

def test_pipeline_extremes():
    # Test de la détection d'un intrus au sein d'un groupe uniforme
    RAYON = "pnns_groups_1"
    
    df_intrus = pd.DataFrame({
        "code": [f"code_{i}" for i in range(21)],
        "product_name": [f"produit_{i}" for i in range(21)],
        RAYON: ["Rayon_Test"] * 21,
        "sugars_100g": [5.0] * 20 + [95.0]  # 20 valeurs identiques, 1 valeur géante (intrus)
    })
    
    res_intrus = extremes_restants(df_intrus, ["sugars_100g"], seuil=3.5)
    
    assert len(res_intrus) == 1, "L'intrus n'a pas été détecté ou des valeurs normales ont été prises"
    assert res_intrus.iloc[0]["valeur"] == 95.0, "La valeur de l'intrus détecté est incorrecte"
    assert res_intrus.iloc[0]["variable"] == "sugars_100g", "Mauvaise variable assignée"
    print("Test 1 (Détection d'un intrus isolé) : OK")

    # Test d'un résultat vide bien formé (pas d'extrêmes au-delà du seuil)
    df_normal = pd.DataFrame({
        "code": [f"code_{i}" for i in range(10)],
        "product_name": [f"produit_{i}" for i in range(10)],
        RAYON: ["Rayon_Test"] * 10,
        "sugars_100g": [10.0, 11.0, 9.0, 10.5, 9.5, 10.0, 10.2, 9.8, 10.1, 9.9] # Valeurs proches
    })
    
    res_vide = extremes_restants(df_normal, ["sugars_100g"], seuil=3.5)
    
    assert isinstance(res_vide, pd.DataFrame), "Le retour doit être un DataFrame"
    assert len(res_vide) == 0, "Le DataFrame devrait être vide car aucune valeur ne dépasse 3.5 MAD"
    assert list(res_vide.columns) == ["code", "product_name", "rayon", "variable", "valeur", "zscore"], "Structure des colonnes incorrecte pour le retour vide"
    print("Test 2 (Retour vide bien formé) : OK")

def test_pipeline_comparaisons():
    # Test sur deux groupes identiques (différence nulle, p-value attendue à 1.0)
    a = pd.Series([10, 11, 9, 10, 10])
    b = pd.Series([10, 11, 9, 10, 10])
    
    res_identiques = comparer_deux_groupes(a, b)
    assert res_identiques["diff_med"] == 0, "L'écart de médiane devrait être nul"
    assert res_identiques["cohen_d"] == 0, "Le d de Cohen devrait être nul"
    assert res_identiques["p_value"] == 1.0, "La p-value devrait être égale à 1.0 pour des groupes identiques"
    print("Test 1 (Groupes identiques) : OK")

    # Test sur deux groupes manifestement différents (Mann-Whitney significatif)
    grp_bas = pd.Series([1, 2, 1, 3, 2, 2, 1, 3, 2, 2])
    grp_haut = pd.Series([10, 12, 11, 13, 12, 11, 10, 12, 11, 12])
    
    res_diff = comparer_deux_groupes(grp_bas, grp_haut)
    assert res_diff["diff_med"] > 0, "L'écart de médiane doit être positif"
    assert res_diff["cohen_d"] > 1.5, "La taille d'effet doit être très grande"
    assert res_diff["p_value"] < 0.01, "Le test doit être hautement significatif (p < 0.01)"
    print("Test 2 (Groupes distincts) : OK")

