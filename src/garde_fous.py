import re
import unicodedata

MOTS_CLES_MEDICAUX = [
    "diabete", "diabetique", "cholesterol", "hypertension", "cancer",
    "maladie", "pathologie", "traitement", "medicament", "ordonnance",
    "regime therapeutique", "allergie", "intolerance", "grossesse",
    "enceinte", "insuline", "glycemie", "tension arterielle", "medecin",
    "symptome", "guerir", "soigner"
]


def normaliser_texte(texte: str) -> str:
    """Met en minuscules et supprime les accents."""
    if not isinstance(texte, str):
        return ""
    # Gestion des caractères spéciaux
    texte_nfd = unicodedata.normalize("NFD", texte.lower())
    return "".join(c for c in texte_nfd if unicodedata.category(c) != "Mn")

def verifier_requete_medicale(question: str) -> str | None:
    """
    Garde-fou en amont du LLM.
    Retourne un message de refus si une intention médicale est détectée, sinon None.
    """
    q_norm = normaliser_texte(question)
    for mot in MOTS_CLES_MEDICAUX:
        if re.search(rf"\b{re.escape(mot)}\b", q_norm):
            return (
                "Je suis un assistant dédié uniquement à l'information nutritionnelle sur les produits alimentaires. "
                "Je ne peux pas donner de conseil médical ni me prononcer sur une pathologie ou un régime thérapeutique. "
                "Veuillez consulter un médecin ou un professionnel de santé."
            )
    return None
