import json
import math
import os
from pathlib import Path
from dotenv import load_dotenv
from src.garde_fous import normaliser_texte
from src.substitution import preparation_donnee, suggest_substitutes, compute_scales

load_dotenv()

CURRENT_PATH = Path(__file__).resolve().parent
NUTRIENT_COLS = ["kcal", "lipides", "satures", "sucres", "sel", "fibres", "proteines"]


def _nettoyer_nombre(val):
    """Convertit NaN/None en None, sinon arrondit à 2 décimales."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    try:
        return round(float(val), 2)
    except (ValueError, TypeError):
        return None

def formater_fiche(ligne: dict, alternatives: list[dict] | None = None) -> dict:
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

    fiche = {
        "code": str(ligne.get("code", "")).strip(),
        "nom": str(ligne.get("nom", "")).strip(),
        "nutriscore": nutriscore,
        "nutriments": nutriments,
        "incomplet": incomplet
    }

    if alternatives is not None:
        fiche["alternatives_saines"] = [
            {
                "code": str(alt.get("code", "")).strip(),
                "nom": str(alt.get("nom", "")).strip(),
                "nutriscore": str(alt.get("nutriscore", "")).strip().upper(),
                "sucres": _nettoyer_nombre(alt.get("sucres")),
                "satures": _nettoyer_nombre(alt.get("satures")),
                "kcal": _nettoyer_nombre(alt.get("kcal"))
            }
            for alt in alternatives
        ]
    return fiche


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
        if nom_outil != "chercher_produit":
            return {"erreur": f"Outil inconnu ou non autorisé : '{nom_outil}'."}

        try:
            args = json.loads(arguments_json) if isinstance(arguments_json, str) else arguments_json
        except json.JSONDecodeError as e:
            return {"erreur": f"Arguments JSON illisibles : {e}"}

        if not isinstance(args, dict):
            return {"erreur": "Les arguments doivent former un objet JSON."}

        cles_autorisees = {"nom", "code", "limite", "avec_alternatives"}
        cles_inconnues = set(args.keys()) - cles_autorisees
        if cles_inconnues:
            return {"erreur": f"Argument(s) non autorisé(s) : {sorted(cles_inconnues)}"}

        nom = args.get("nom")
        code = args.get("code")
        limite = args.get("limite", 3)
        avec_alternatives = args.get("avec_alternatives", False)

        if nom is None and code is None:
            return {"erreur": "Vous devez fournir au moins 'nom' ou 'code'."}

        if nom is not None and not isinstance(nom, str):
            return {"erreur": "L'argument 'nom' doit être une chaîne de caractères."}
        if code is not None and not isinstance(code, str):
            return {"erreur": "L'argument 'code' doit être une chaîne de caractères."}
        if isinstance(limite, bool) or not isinstance(limite, int) or not (1 <= limite <= 5):
            return {"erreur": "L'argument 'limite' doit être un entier compris entre 1 et 5."}
        if not isinstance(avec_alternatives, bool):
            return {"erreur": "L'argument 'avec_alternatives' doit être un booléen."}

        return self.chercher_produit(
            nom=nom,
            code=code,
            limite=limite,
            avec_alternatives=avec_alternatives
        )

    def chercher_produit(
        self,
        nom: str | None = None,
        code: str | None = None,
        limite: int = 3,
        avec_alternatives: bool = False
    ) -> dict:
        """Implémentation métier conforme au contrat + intégration substitution"""
        if code is not None and code.strip() != "":
            code_clean = code.strip()
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

        fiches = []
        for _, row in resultats.head(limite).iterrows():
            alts = None
            if avec_alternatives:
                alts = suggest_substitutes(
                    code_produit=str(row["code"]).strip(),
                    enregistrements=self.enregistrements,
                    k=3,
                    scales=self.scales
                )
            fiches.append(formater_fiche(row, alternatives=alts))

        return {
            "statut": statut,
            "total": total,
            "produits": fiches
        }