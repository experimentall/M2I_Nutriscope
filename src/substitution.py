import math

NUTRIENT_COLS = ["kcal", "lipides", "satures", "sucres", "sel", "fibres", "proteines"]

def compute_scales(enregistrements):
    """
    Calcule l'écart-type de chaque nutriment sur l'ensemble des produits complets.
    Sert de facteur d'échelle pour normaliser la distance euclidienne.
    """
    # Filtrage initial pour ne garder que les lignes sans aucun NaN ou None
    complets = []
    for p in enregistrements:
        est_complet = True
        for col in NUTRIENT_COLS:
            val = p.get(col)
            if val is None or (isinstance(val, float) and math.isnan(val)):
                est_complet = False
                break
        if est_complet:
            complets.append(p)
            
    if not complets:
        return {col: 1.0 for col in NUTRIENT_COLS}
        
    n = len(complets)
    scales = {}
    
    for col in NUTRIENT_COLS:
        valeurs = [p[col] for p in complets]
        moyenne = sum(valeurs) / n
        variance = sum((v - moyenne) ** 2 for v in valeurs) / n
        ecart_type = math.sqrt(variance)
        # Sécurité anti-division par zéro
        scales[col] = ecart_type if ecart_type > 0 else 1.0
        
    return scales


def filter_candidates(produit_scanne, enregistrements):
    """
    Règles de garde de NutriScope : extrait les candidats comparables.
    Filtre : même rayon, même sous-catégorie, données complètes, et exclut le produit scanné.
    """
    candidats = []
    ref_code = produit_scanne.get("code")
    ref_rayon = produit_scanne.get("rayon")
    ref_subcat = produit_scanne.get("sous_categorie")
    
    for p in enregistrements:
        # Écarter le produit d'origine
        if p.get("code") == ref_code:
            continue
        # Même rayon et même sous-catégorie (garantie du même usage culinaire)
        if p.get("rayon") != ref_rayon or p.get("sous_categorie") != ref_subcat:
            continue
            
        # Vérification de l'intégralité des nutriments obligatoires
        est_complet = True
        for col in NUTRIENT_COLS:
            val = p.get(col)
            if val is None or (isinstance(val, float) and math.isnan(val)):
                est_complet = False
                break
        if not est_complet:
            continue
            
        candidats.append(p)
        
    return candidats


def rank_candidates(produit_scanne, candidats, scales, prefer_bio=False):
    """
    Classe les candidats selon l'ordre de priorité métier :
    1. Respect du label bio (si demandé et si le produit d'origine est bio)
    2. Meilleur Nutri-Score (A d'abord, E en dernier)
    3. Distance nutritionnelle la plus faible (le plus proche voisin)
    """
    ref_bio = produit_scanne.get("bio", False)
    mapping_nutri = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4}
    
    def cle_tri(cand):
        # Gestion du critère BIO (Pénalité de 1 si non-bio face à une référence bio)
        critere_bio = 0
        if prefer_bio and ref_bio:
            critere_bio = 0 if cand.get("bio", False) else 1
                
        # Remplacement du Nutri-Score par son rang numérique
        grade = str(cand.get("nutriscore", "")).strip().upper()
        rang_nutri = mapping_nutri.get(grade, 99)
        
        # Distance euclidienne normalisée par l'écart-type
        somme_carres = 0.0
        for col in NUTRIENT_COLS:
            diff = produit_scanne[col] - cand[col]
            somme_carres += (diff / scales[col]) ** 2
        dist = math.sqrt(somme_carres)
        
        return (critere_bio, rang_nutri, dist)
        
    # Tri stable de Python basé sur le tuple de priorités
    candidats_tries = sorted(candidats, key=cle_tri)
    
    # Injection de la distance finale calculée dans l'objet pour l'affichage final
    for c in candidats_tries:
        somme_carres = 0.0
        for col in NUTRIENT_COLS:
            diff = produit_scanne[col] - c[col]
            somme_carres += (diff / scales[col]) ** 2
        c["distance"] = math.sqrt(somme_carres)
        
    return candidats_tries

def filtrer_sucres(code, suggestions, enregistrements, tolerance=0.10):
    """
    Écarte les suggestions plus sucrées que le produit d'origine (+ tolérance).
    """
    index_base = {p["code"]: p for p in enregistrements}
    prod_origine = index_base.get(code)
    if not prod_origine:
        return suggestions
        
    sucres_origine = prod_origine.get("sucres", 0.0)
    if sucres_origine is None or (isinstance(sucres_origine, float) and math.isnan(sucres_origine)):
        sucres_origine = 0.0
        
    seuil_maximal = sucres_origine * (1.0 + tolerance)
    
    suggestions_filtrees = []
    for s in suggestions:
        sucres_cand = s.get("sucres", 0.0)
        if sucres_cand is None or (isinstance(sucres_cand, float) and math.isnan(sucres_cand)):
            sucres_cand = 0.0
            
        # On conserve uniquement si la teneur en sucre respecte la tolérance
        if sucres_cand <= seuil_maximal:
            suggestions_filtrees.append(s)
            
    return suggestions_filtrees

def suggest_substitutes(code_produit, enregistrements, k=3, max_distance=float("inf"), scales=None):
    """
    Trouve le produit, filtre ses candidats, conserve uniquement ceux qui AMÉLIORENT 
    le Nutri-Score et respectent la distance maximale, applique le filtre sur les sucres, 
    puis retourne les k meilleurs.
    """
    # Trouver le produit scanné d'origine
    produit_scanne = next((p for p in enregistrements if p.get("code") == code_produit), None)
    if not produit_scanne:
        return []
        
    # Vérification que le produit scanné possède ses nutriments
    for col in NUTRIENT_COLS:
        val = produit_scanne.get(col)
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return []
            
    if scales is None:
        scales = compute_scales(enregistrements)
        
    # Extraire et classer l'ensemble des candidats valides
    candidats = filter_candidates(produit_scanne, enregistrements)
    candidats_classes = rank_candidates(produit_scanne, candidats, scales, prefer_bio=produit_scanne.get("bio", False))
    
    mapping_nutri = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4}
    grade_ref = str(produit_scanne.get("nutriscore", "")).strip().upper()
    rang_reference = mapping_nutri.get(grade_ref, 99)
    
    suggestions_initiales = []
    
    # Application des filtres de garde de base (Nutri-Score et distance maximale)
    for c in candidats_classes:
        # Exclure si le Nutri-Score n'est pas STRICTEMENT meilleur
        grade_cand = str(c.get("nutriscore", "")).strip().upper()
        if mapping_nutri.get(grade_cand, 99) >= rang_reference:
            continue
            
        # Exclure si le candidat dépasse la barrière de similarité maximale
        if c.get("distance", 0.0) > max_distance:
            continue
            
        suggestions_initiales.append(c)
        
    # Application de la règle métier sur les sucres
    # On passe la liste de toutes les suggestions valides au filtre
    suggestions_valides = filtrer_sucres(code_produit, suggestions_initiales, enregistrements, tolerance=0.10)
        
    # On retourne uniquement les k premiers résultats après filtrage complet
    return suggestions_valides[:k]


# def suggest_substitutes(code_produit, enregistrements, k=3, max_distance=float("inf"), scales=None):
#     """
#     Trouve le produit, filtre ses candidats, conserve uniquement ceux qui AMÉLIORENT 
#     le Nutri-Score et respectent la distance maximale, puis retourne les k meilleurs.
#     """
#     # Trouver le produit scanné d'origine
#     produit_scanne = next((p for p in enregistrements if p.get("code") == code_produit), None)
#     if not produit_scanne:
#         return []
        
#     # Vérification que le produit scanné possède ses nutriments
#     for col in NUTRIENT_COLS:
#         val = produit_scanne.get(col)
#         if val is None or (isinstance(val, float) and math.isnan(val)):
#             return []
            
#     if scales is None:
#         scales = compute_scales(enregistrements)
        
#     # Extraire et classer l'ensemble des candidats valides
#     candidats = filter_candidates(produit_scanne, enregistrements)
#     candidats_classes = rank_candidates(produit_scanne, candidats, scales, prefer_bio=produit_scanne.get("bio", False))
    
#     mapping_nutri = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4}
#     grade_ref = str(produit_scanne.get("nutriscore", "")).strip().upper()
#     rang_reference = mapping_nutri.get(grade_ref, 99)
    
#     suggestions = []
    
#     # Application des filtres de garde finaux
#     for c in candidats_classes:
#         # Exclure si le Nutri-Score n'est pas STRICTEMENT meilleur
#         grade_cand = str(c.get("nutriscore", "")).strip().upper()
#         if mapping_nutri.get(grade_cand, 99) >= rang_reference:
#             continue
            
#         # Exclure si le candidat dépasse la barrière de similarité maximale
#         if c.get("distance", 0.0) > max_distance:
#             continue
            
#         suggestions.append(c)
        
#         # Sortie anticipée dès que la cible de suggestions k est atteinte
#         if len(suggestions) == k:
#             break
            
#     return suggestions
