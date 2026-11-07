import math
import pytest
from src.substitution import (
    compute_scales,
    filter_candidates,
    rank_candidates,
    suggest_substitutes,
    filtrer_sucres,
)

# --- JEU DE DONNÉES SYNTHÉTIQUE DE TEST (MOCK) ---
PRODUIT_BASE = {
    "code": "111", "nom": "Soda Référence Mauvaise", "rayon": "beverages", "sous_categorie": "soda",
    "nutriscore": "E", "bio": False,
    "kcal": 150.0, "lipides": 10.0, "satures": 5.0, "sucres": 30.0, "sel": 0.5, "fibres": 0.0, "proteines": 1.0
}

PRODUIT_MEILLEUR = {
    "code": "222", "nom": "Soda Substitut Idéal", "rayon": "beverages", "sous_categorie": "soda",
    "nutriscore": "B", "bio": False,
    "kcal": 40.0, "lipides": 0.0, "satures": 0.0, "sucres": 5.0, "sel": 0.1, "fibres": 0.0, "proteines": 0.5
}

PRODUIT_BIO = {
    "code": "333", "nom": "Soda Substitut Bio", "rayon": "beverages", "sous_categorie": "soda",
    "nutriscore": "B", "bio": True,
    "kcal": 45.0, "lipides": 0.0, "satures": 0.0, "sucres": 6.0, "sel": 0.1, "fibres": 0.0, "proteines": 0.5
}

PRODUIT_INCOMPLET = {
    "code": "444", "nom": "Soda Données Incomplètes", "rayon": "beverages", "sous_categorie": "soda",
    "nutriscore": "C", "bio": False,
    "kcal": 80.0, "lipides": None, "satures": 2.0, "sucres": 15.0, "sel": 0.2, "fibres": float("nan"), "proteines": 0.8
}

PRODUIT_AUTRE_RAYON = {
    "code": "555", "nom": "Biscuit Hors Périmètre", "rayon": "snacks", "sous_categorie": "biscuits",
    "nutriscore": "A", "bio": False,
    "kcal": 350.0, "lipides": 12.0, "satures": 4.0, "sucres": 20.0, "sel": 0.6, "fibres": 5.0, "proteines": 7.0
}

CATALOGUE_MOCK = [PRODUIT_BASE, PRODUIT_MEILLEUR, PRODUIT_BIO, PRODUIT_INCOMPLET, PRODUIT_AUTRE_RAYON]
SCALES_MOCK = {"kcal": 50.0, "lipides": 5.0, "satures": 2.0, "sucres": 10.0, "sel": 0.2, "fibres": 2.0, "proteines": 3.0}


# --- SUITE DE VALIDATION UNITAIRE ---

def test_compute_scales():
    """Vérifie le calcul correct des facteurs d'échelle (écarts-types) et la gestion des NaN."""
    scales = compute_scales(CATALOGUE_MOCK)
    assert isinstance(scales, dict)
    assert "kcal" in scales
    assert scales["kcal"] > 0
    # Sécurité : la fonction doit ignorer PRODUIT_INCOMPLET pour éviter d'avoir un écart-type égal à NaN
    assert not math.isnan(scales["fibres"])


def test_filter_candidates():
    """Valide les règles de garde pour extraire uniquement les candidats comparables."""
    candidats = filter_candidates(PRODUIT_BASE, CATALOGUE_MOCK)
    codes = [c["code"] for c in candidats]
    
    # Doit contenir les substituts valides de la même sous-catégorie
    assert "222" in codes
    assert "333" in codes
    # RÈGLES DE GARDE : Ne doit contenir ni lui-même (111), ni l'incomplet (444), ni l'autre rayon (555)
    assert "111" not in codes
    assert "444" not in codes
    assert "555" not in codes


def test_rank_candidates():
    """Valide la logique de classement stable et l'injection de la variable de distance."""
    candidats = filter_candidates(PRODUIT_BASE, CATALOGUE_MOCK)
    
    # 1. Test de classement standard sans préférence de label
    classes = rank_candidates(PRODUIT_BASE, candidats, SCALES_MOCK, prefer_bio=False)
    assert len(classes) == 2
    assert "distance" in classes[0]
    assert classes[0]["distance"] > 0

    # 2. Test de classement avec préférence Bio actif et référence scannée Bio
    produit_scanne_bio = PRODUIT_BASE.copy()
    produit_scanne_bio["bio"] = True
    classes_bio = rank_candidates(produit_scanne_bio, candidats, SCALES_MOCK, prefer_bio=True)
    # Le produit porteur du label Bio (333) doit être priorisé et passer devant (222) à Nutri-Score égal
    assert classes_bio[0]["code"] == "333"


def test_suggest_substitutes():
    """Contrôle le filtrage final et l'application de la barrière de distance maximale."""
    # Cas 1 : Recherche de substitution fonctionnelle (Doit trouver des alternatives mieux notées)
    suggestions = suggest_substitutes("111", CATALOGUE_MOCK, k=2, max_distance=15.0, scales=SCALES_MOCK)
    assert len(suggestions) <= 2
    assert suggestions[0]["code"] in ["222", "333"]
    
    # Cas 2 : Test du garde-fou avec une distance maximale volontairement trop restrictive
    suggestions_bloquees = suggest_substitutes("111", CATALOGUE_MOCK, k=2, max_distance=0.001, scales=SCALES_MOCK)
    assert len(suggestions_bloquees) == 0

def test_filtrer_sucres():
    """Vérifie que la règle métier élimine les substituts trop sucrés."""
    produit_ref = {
        "code": "A1", "nom": "Riz Coco Base", "sucres": 5.0,
        "kcal": 150, "lipides": 2.0, "satures": 1.0, "sel": 0.1, "fibres": 1.0, "proteines": 3.0
    }
    substitut_correct = {
        "code": "A2", "nom": "Riz Coco Léger", "sucres": 5.2, # +4% -> Dans la tolérance de 10%
        "kcal": 140, "lipides": 1.0, "satures": 0.5, "sel": 0.1, "fibres": 1.0, "proteines": 3.0
    }
    substitut_trop_sucre = {
        "code": "A3", "nom": "Riz Coco Sucré", "sucres": 6.0, # +20% -> Doit être rejeté
        "kcal": 160, "lipides": 1.5, "satures": 0.5, "sel": 0.1, "fibres": 1.0, "proteines": 3.0
    }
    
    base_locale = [produit_ref, substitut_correct, substitut_trop_sucre]
    suggestions_initiales = [substitut_correct, substitut_trop_sucre]
    
    # Exécution du filtre avec la tolérance par défaut de 10%
    suggestions_valides = filtrer_sucres("A1", suggestions_initiales, base_locale)
    
    codes_restants = [s["code"] for s in suggestions_valides]
    
    assert len(suggestions_valides) == 1
    assert "A2" in codes_restants
    assert "A3" not in codes_restants # Le produit trop sucré a bien été exclu
