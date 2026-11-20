import json
import math
import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from src.assistant.garde_fous import normaliser_texte
from src.substitution import NUTRIENT_COLS, preparation_donnee, suggest_substitutes, compute_scales
load_dotenv()

CURRENT_PATH = Path(__file__).resolve().parent.parent

def _nettoyer_nombre(val):
    """Convertit NaN/None en None, sinon arrondit à 2 décimales."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    try:
        return round(float(val), 2)
    except (ValueError, TypeError):
        return None

def formater_fiche(ligne: dict) -> dict:
    """Construit une fiche produit conforme au contrat imposé."""
    nutriscore_brut = ligne.get("nutriscore")
    if nutriscore_brut is None or (isinstance(nutriscore_brut, float) and math.isnan(nutriscore_brut)):
        nutriscore = None
    else:
        nutriscore = str(nutriscore_brut).strip().upper()
        if nutriscore not in {"A", "B", "C", "D", "E"}:
            nutriscore = None

    incomplet = nutriscore is None
    nutriments = {}
    for col in NUTRIENT_COLS:
        val = _nettoyer_nombre(ligne.get(col))
        if val is None:
            incomplet = True
        nutriments[col] = val

    nom = str(ligne.get("nom")).strip() if pd.notna(ligne.get("nom")) and str(ligne.get("nom")).strip() != "" else "Produit sans nom"
    return {
        "code": str(ligne.get("code", "")).strip(),
        "nom": nom,
        "nutriscore": nutriscore,
        "nutriments": nutriments,
        "incomplet": incomplet
    }

class CatalogueOutils:
    def __init__(self):
        source = CURRENT_PATH.parent / os.getenv("PARQUET_SOURCE")
        self.df = preparation_donnee(source).copy()

        self.df["code_str"] = self.df["code"].astype(str).str.strip()
        self.df["nom_norm"] = self.df["nom"].astype(str).apply(normaliser_texte)
        self.enregistrements = self.df.to_dict(orient="records")
        self.scales = compute_scales(self.enregistrements)

    def executer_appel_brut(self, nom_outil: str, arguments_json: str) -> dict:
        """Valide strictement la demande du modèle avant d'exécuter quoi que ce soit."""
        if nom_outil not in {"chercher_produit", "suggest_substitutes"}:
            return {"erreur": f"Outil inconnu ou non autorisé : '{nom_outil}'."}
        
        try:
            args = json.loads(arguments_json) if isinstance(arguments_json, str) else arguments_json
        except json.JSONDecodeError as e:
            return {"erreur": f"Arguments JSON illisibles : {e}"}

        if not isinstance(args, dict):
            return {"erreur": "Les arguments doivent former un objet JSON."}

        if nom_outil == "chercher_produit":
            cles_autorisees = {"nom", "code", "limite"}
            cles_inconnues = set(args.keys()) - cles_autorisees
            if cles_inconnues:
                return {"erreur": f"Argument(s) non autorisé(s) : {sorted(cles_inconnues)}"}

            nom = args.get("nom")
            code = args.get("code")
            limite = args.get("limite", 3)

            if nom is None and code is None:
                return {"erreur": "Vous devez fournir au moins 'nom' ou 'code'."}

            if nom is not None and not isinstance(nom, str):
                return {"erreur": "L'argument 'nom' doit être une chaîne de caractères."}
            if code is not None and not isinstance(code, str):
                return {"erreur": "L'argument 'code' doit être une chaîne de caractères."}
            if isinstance(limite, bool) or not isinstance(limite, int) or not (1 <= limite <= 5):
                return {"erreur": "L'argument 'limite' doit être un entier compris entre 1 et 5."}

            return self.chercher_produit(nom=nom, code=code, limite=limite)

        if nom_outil == "suggest_substitutes":
            cles_autorisees = {"code", "k"}
            cles_inconnues = set(args.keys()) - cles_autorisees
            if cles_inconnues:
                return {"erreur": f"Argument(s) non autorisé(s) : {sorted(cles_inconnues)}"}

            code = args.get("code")
            k = args.get("k", 3)

            if code is None or not isinstance(code, str) or code.strip() == "":
                return {"erreur": "Vous devez fournir un 'code' produit valide (chaîne non vide)."}
            if isinstance(k, bool) or not isinstance(k, int) or not (1 <= k <= 5):
                return {"erreur": "L'argument 'k' doit être un entier compris entre 1 et 5."}

            return self.suggest_substitutes(code=code, k=k)

    def chercher_produit(
        self,
        nom: str | None = None,
        code: str | None = None,
        limite: int = 3
    ) -> dict:
        """Implémentation métier conforme au contrat + intégration substitution"""
        if code is not None and code.strip() != "":
            code_clean = code.strip().replace(" ", "")
            resultats = self.df[self.df["code_str"] == code_clean]
        elif nom is not None and nom.strip() != "":
            nom_clean = normaliser_texte(nom.strip())
            resultats = self.df[self.df["nom_norm"].str.contains(nom_clean, regex=False, na=False)]
        else:
            return {"erreur": "Les arguments 'nom' ou 'code' ne peuvent pas être vides."}

        total = len(resultats)
        if total == 0:
            statut = "introuvable"
        elif total == 1:
            statut = "ok"
        else:
            statut = "ambigu"

        fiches = [formater_fiche(row) for _, row in resultats.head(limite).iterrows()]

        return {
            "statut": statut,
            "total": total,
            "produits": fiches
        }

    def suggest_substitutes(self, code: str, k: int = 3) -> dict:
        """Recherche des alternatives plus saines dans le même rayon à partir du code-barres."""
        code_clean = code.strip().replace(" ", "")
        if self.df[self.df["code_str"] == code_clean].empty:
            return {"statut": "introuvable", "alternatives_saines": []}

        alts = suggest_substitutes(
            code_produit=code_clean,
            enregistrements=self.enregistrements,
            k=k,
            scales=self.scales
        )

        alternatives_formatees = [
            {
                "code": str(alt.get("code", "")).strip(),
                "nom": str(alt.get("nom")).strip() if pd.notna(alt.get("nom")) and str(alt.get("nom")).strip() != "" else "Produit sans nom",
                "nutriscore": str(alt.get("nutriscore", "")).strip().upper(),
                "sucres": _nettoyer_nombre(alt.get("sucres")),
                "satures": _nettoyer_nombre(alt.get("satures")),
                "kcal": _nettoyer_nombre(alt.get("kcal"))
            }
            for alt in alts
        ]

        return {
            "statut": "ok",
            "code_initial": code_clean,
            "alternatives_saines": alternatives_formatees
        }