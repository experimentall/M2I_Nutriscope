"""Pipeline d'ingestion rejouable : fiches produits + documents officiels -> ChromaDB."""

import json
import os
from pathlib import Path
import chromadb
from dotenv import load_dotenv
from openai import OpenAI
import argparse

load_dotenv()

RACINE = Path(__file__).resolve().parents[2]
DOSSIER_FICHES = RACINE / "data" / "corpus" / "fiches"
DOSSIER_DOCS = RACINE / "data" / "corpus" / "documents"
DOSSIER_CHROMA = RACINE / "data" / "chroma_db"
CLES = ("code", "nom", "marque", "rayon", "nutriscore", "source", "licence")

MODELE_EMBED = os.environ.get("LLM_EMBEDDINGS", "qwen3-embedding:0.6b")
client_openai = OpenAI(
    base_url=os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.environ.get("LLM_API_KEY", "ollama"),
)


def embed_lot(textes: list[str], taille_lot: int = 32) -> list[list[float]]:
    """Vectorise une liste de textes sans préfixe (format document pour qwen3-embedding)."""    
    vecteurs = []
    for i in range(0, len(textes), taille_lot):
        lot = textes[i : i + taille_lot]
        rep = client_openai.embeddings.create(model=MODELE_EMBED, input=lot)
        vecteurs.extend([d.embedding for d in rep.data])
    return vecteurs


def decouper_texte(texte: str, taille: int = 800, chevauchement: int = 150) -> list[str]:
    """Découpe un texte long en chunks avec chevauchement sur les paragraphes/espaces."""
    texte = texte.strip()
    if len(texte) <= taille:
        return [texte]

    chunks = []
    debut = 0
    while debut < len(texte):
        fin = min(debut + taille, len(texte))
        if fin < len(texte):
            # Cherche une coupure propre (saut de ligne ou espace)
            coupure = texte.rfind("\n", debut + taille // 2, fin)
            if coupure == -1:
                coupure = texte.rfind(" ", debut + taille // 2, fin)
            if coupure != -1:
                fin = coupure

        morceau = texte[debut:fin].strip()
        if morceau:
            chunks.append(morceau)
        if fin == len(texte):
            break
        debut = max(debut + 1, fin - chevauchement)
    return chunks

def preparer_metadonnees(meta: dict[str, str]) -> dict[str, str]:
    resultat = {}
    for cle in CLES:
        val = meta.get(cle)
        # Ne pas ajouter la clé dans le dictionnaire si la valeur est vide
        if val is None:
            continue

        val_str = str(val).strip()
        if val_str and val_str.lower() not in {"none", "nan", "non renseigné"}:
            resultat[cle] = val_str

    return resultat

def preparer_chunks() -> tuple[list[str], list[str], list[dict]]:
    """Charge les fiches et les documents et renvoie (ids, textes, metadonnees)."""
    ids, textes, metadonnees = [], [], []

    # Fiches produits (1 fiche = 1 chunk)
    meta_fiches_path = DOSSIER_FICHES / "metadonnees.jsonl"
    if meta_fiches_path.exists():
        for ligne in meta_fiches_path.read_text(encoding="utf-8").splitlines():
            info = json.loads(ligne)
            chemin_txt = DOSSIER_FICHES / f"{info['code']}.txt"
            if chemin_txt.exists():
                ids.append(f"fiche_{info['code']}")
                textes.append(chemin_txt.read_text(encoding="utf-8").strip())
                metadonnees.append(preparer_metadonnees(info) | {"type": "fiche_produit"})

    # Documents officiels (découpage avec chevauchement)
    manifeste_path = DOSSIER_DOCS / "manifeste.jsonl"
    if manifeste_path.exists():
        # Dédoublonnage par id au cas où telecharger.py a été lancé plusieurs fois
        sources_uniques = {}
        for ligne in manifeste_path.read_text(encoding="utf-8").splitlines():
            info = json.loads(ligne)
            sources_uniques[info["id"]] = info

        for doc_id, info in sources_uniques.items():
            chemin_txt = DOSSIER_DOCS / f"{doc_id}.txt"
            if chemin_txt.exists():
                contenu = chemin_txt.read_text(encoding="utf-8")
                # Séparation de l'en-tête ajouté par telecharger.py et du corps
                parties = contenu.split("\n\n", 1)
                entete = parties[0]
                corps = parties[1] if len(parties) > 1 else contenu
                titre_source = entete.splitlines()[0].replace("Source : ", "")

                for idx, chunk in enumerate(decouper_texte(corps)):
                    ids.append(f"doc_{doc_id}_chunk_{idx}")
                    # textes.append(chunk)
                    textes.append(f"{titre_source}\n{chunk}")
                    metadonnees.append({
                        "type": "document_officiel",
                        "source": titre_source,
                        "url": info["url"],
                        "licence": info["licence"],
                    })

    return ids, textes, metadonnees


def indexer() -> None:
    print("Préparation des chunks...")
    ids, textes, metadonnees = preparer_chunks()
    if not ids:
        print("Aucun document trouvé.")
        return

    print(f"Vectorisation de {len(ids)} chunks avec {MODELE_EMBED}...")
    vecteurs = embed_lot(textes)

    client_chroma = chromadb.PersistentClient(path=str(DOSSIER_CHROMA))

    collection = client_chroma.get_or_create_collection(
        name="fiche",
        configuration={"hnsw": {"space": "cosine"}},
        embedding_function=None,  # aucun modèle caché : on fournit nos vecteurs
    )

    # Upsert par lots pour garantir l'idempotence (pipeline rejouable)
    taille_lot = 100
    for i in range(0, len(ids), taille_lot):
        collection.upsert(
            ids=ids[i : i + taille_lot],
            embeddings=vecteurs[i : i + taille_lot],
            documents=textes[i : i + taille_lot],
            metadatas=metadonnees[i : i + taille_lot],
        )

    print(f"Indexation terminée : {collection.count()} chunks disponibles dans {DOSSIER_CHROMA}.")


if __name__ == "__main__":
    indexer()
