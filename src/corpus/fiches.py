import json
import math
import os
from pathlib import Path
import argparse
from dotenv import load_dotenv
from src.substitution import NUTRIENT_COLS, preparation_donnee

load_dotenv()

RACINE_PROJET = Path(__file__).resolve().parents[2]
DOSSIER_SORTIE = RACINE_PROJET / "data" / "corpus" / "fiches"

def _formater_valeur(val, unite: str = "") -> str:
    """Remplace NaN/None/vide par 'non renseigné', sinon formate proprement."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "non renseigné"
    texte = str(val).strip()
    if texte == "" or texte.lower() in {"nan", "none", "null"}:
        return "non renseigné"
    return f"{texte}{unite}"


def _nettoyer_nom_fichier(code: str) -> str:
    """Sécurise le code-barres pour en faire un nom de fichier valide."""
    return "".join(c for c in code if c.isalnum() or c in {"-", "_"})

def nettoyer_dossier_sortie() -> None:
    """Supprime les anciennes fiches .txt et le fichier metadonnees.jsonl existants."""
    if not DOSSIER_SORTIE.exists():
        return

    nb_supprimes = 0
    for fichier in DOSSIER_SORTIE.glob("*.txt"):
        fichier.unlink()
        nb_supprimes += 1

    chemin_meta = DOSSIER_SORTIE / "metadonnees.jsonl"
    if chemin_meta.exists():
        chemin_meta.unlink()

    if nb_supprimes > 0:
        print(f"Nettoyage : {nb_supprimes} anciennes fiches supprimées.")

def generer_corpus_fiches(limite: int | None) -> None:
    source_parquet = RACINE_PROJET / os.getenv("PARQUET_SOURCE")
    df = preparation_donnee(source_parquet).copy()

    DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)
    chemin_meta = DOSSIER_SORTIE / "metadonnees.jsonl"

    compteur = 0
    with open(chemin_meta, "w", encoding="utf-8") as f_meta:
        for _, row in df.iterrows():
            if limite is not None and compteur >= limite:
                break

            code = _formater_valeur(row.get("code"))
            if code == "non renseigné":
                continue

            nom = _formater_valeur(row.get("nom"))
            marque = _formater_valeur(row.get("marque"))
            rayon = _formater_valeur(row.get("rayon"))
            
            nutriscore_brut = _formater_valeur(row.get("nutriscore")).upper()
            nutriscore = nutriscore_brut if nutriscore_brut in {"A", "B", "C", "D", "E"} else "non renseigné"

            # Détection des valeurs manquantes
            manquants = [
                col for col in NUTRIENT_COLS
                if _formater_valeur(row.get(col)) == "non renseigné"
            ]
            if nutriscore == "non renseigné":
                manquants.insert(0, "Nutri-Score")

            # Construction du contenu textuel de la fiche
            lignes = [
                f"Produit : {nom}",
                f"Code-barres : {code}",
                f"Rayon : {rayon}",
                f"Marque : {marque}",
                f"Nutri-Score : {nutriscore}",
                "Données incomplètes : " + (f"oui ({', '.join(manquants)})" if manquants else "non"),
                "Valeurs nutritionnelles pour 100 g :", # A REVOIR : 100 ml
            ]

            unites = {
                "kcal": " kcal",
                "lipides": " g",
                "satures": " g",
                "sucres": " g",
                "sel": " g",
                "fibres": " g",
                "proteines": " g"
            }

            for col in NUTRIENT_COLS:
                val_formatee = _formater_valeur(row.get(col), unite=unites.get(col, ""))
                lignes.append(f"- {col} : {val_formatee}")

            contenu_txt = "\n".join(lignes) + "\n"
            nom_fichier = f"{_nettoyer_nom_fichier(code)}.txt"
            chemin_fiche = DOSSIER_SORTIE / nom_fichier

            chemin_fiche.write_text(contenu_txt, encoding="utf-8")

            # Écriture de l'entrée dans metadonnees.jsonl
            entree_meta = {
                "source": "Open Food Facts",
                "code": code,
                "nom": nom,
                "marque": marque,
                "rayon": rayon,
                "nutriscore": nutriscore,
                "licence": "ODbL",
            }
            f_meta.write(json.dumps(entree_meta, ensure_ascii=False) + "\n")
            compteur += 1

    print(f"Terminé : {compteur} fiches générées dans {DOSSIER_SORTIE}")
    print(f"Métadonnées enregistrées dans {chemin_meta}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Créer les fiches produits pour le corpus.")
    parser.add_argument("--limite", type=int, default=None, help="Nombre de fiches à générer")
    args = parser.parse_args()

    nettoyer_dossier_sortie()

    generer_corpus_fiches(args.limite)
