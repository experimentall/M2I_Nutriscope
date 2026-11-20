import base64
import time
from pathlib import Path
from openai import OpenAI
from io import BytesIO
from PIL import Image
import json
from src.assistant.outils import CatalogueOutils
from src.assistant.assistant import AssistantNutriScope
import os
from dotenv import load_dotenv
load_dotenv()

CURRENT_PATH = Path(__file__).resolve().parent

NBRE_DE_LECTURE = 3

prompt_texte = """Recopie les informations de ce produit au format JSON strict.
Réponds uniquement avec l'objet JSON valide, sans texte avant ni après, et sans balises markdown (```json).

Structure attendue :
{
  "produit": {
    "nom": "texte ou null",
    "marque": "texte ou null",
    "code_barres": "texte ou null"
  },
  "base": "100 g" ou "100 ml" ou null,
  "nutriments": {
    "kj": nombre ou null,
    "kcal": nombre ou null,
    "lipides": nombre ou null,
    "satures": nombre ou null,
    "glucides": nombre ou null,
    "sucres": nombre ou null,
    "fibres": nombre ou null,
    "proteines": nombre ou null,
    "sel": nombre ou null
  },
  "inferieur_a": ["liste des clés de nutriments lues avec '<'"],
  "ingredients": ["ingredient 1", "ingredient 2"] ou null
}

Règles d'extraction :
- Utilise le point comme séparateur décimal pour les nombres (ex: 4.5).
- Si une valeur est précédée de '<' (ex: "< 0,5 g"), inscris la valeur numérique (0.5) dans "nutriments" et ajoute le nom de la clé dans "inferieur_a".
- Si une information est absente de l'image, mets null.
"""

# {
#   "statut": "verifie" | "non_verifie" | "illisible",
#   "produit": {"nom": <texte> | null, "marque": <texte> | null, "code_barres": <texte> | null},
#   "base": "100 g" | "100 ml" | null,
#   "nutriments": {"kj", "kcal", "lipides", "satures", "glucides", "sucres", "fibres", "proteines", "sel"} : nombre ou null,
#   "inferieur_a": [<clés de nutriments lues avec « < »>],
#   "ingredients": [<texte>, ...] | null,
#   "fiche_catalogue": <fiche renvoyée par chercher_produit> | null,
#   "ecarts": [{"champ": <clé>, "etiquette": nombre | null, "catalogue": nombre | null}, ...],
#   "alertes": [<texte>, ...],
#   "mesures": {"appels_modele": <entier>, "latence_s": <nombre>, "tokens_entree": <entier>, "tokens_sortie": <entier>}
# }
# ollama run qwen3-vl:4b-instruct "Recopie le tableau nutritionnel : ./data/photos/10_3608580065340_etiquette.jpg"
# ollama run qwen3-vl:8b-instruct "Recopie le tableau nutritionnel : ./data/photos/10_3608580065340_etiquette.jpg"
def scanner_etiquette(image: str) -> dict:
    client = OpenAI(base_url=f"{os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")}", api_key=f"{os.getenv("LLM_API_KEY", "ollama")}")
    model = "qwen3-vl:8b-instruct"
    # model = "qwen/qwen3-vl-30b-a3b-instruct" # Identique à votre modèle Ollama, rapide et économique pour de l'OCR simple.
    # model = "qwen/qwen3-vl-8b-instruct" # Architecture MoE (3B actifs), plus précis sur les étiquettes complexes ou froissées tout en restant rapide.

    image_b64 = prepare_image(image)

    # l'adresse data: (le type doit correspondre au format du fichier)
    url_image = f"data:image/jpeg;base64,{image_b64}"

    # un message en deux morceaux, texte puis image
    messages = [{"role": "user", "content": [
        {"type": "text", "text": prompt_texte},
        {"type": "image_url", "image_url": {"url": url_image}},
    ]}]

    debut = time.perf_counter()
    reponse = client.chat.completions.create(
        model=model, messages=messages, temperature=0
    )

    reponse_json = reponse.choices[0].message.content
    # print(reponse_json)

    try:
        jsont_to_dict = json.loads(reponse_json) if isinstance(reponse_json, str) else reponse_json
    except json.JSONDecodeError as e:
        return {"erreur": f"Arguments JSON illisibles : {e}"}

    items = list(jsont_to_dict.items())
    items.insert(0, ("statut", "non_verifie"))
    items.insert(6, ("fiche_catalogue", "null"))
    items.insert(7, ("ecarts", []))
    items.insert(8, ("alertes", []))

    tokens_entree = reponse.usage.prompt_tokens
    tokens_sortie = reponse.usage.completion_tokens
    items.insert(9, ('mesures', {
        'appels_modele': 0,
        'latence_s': f"{time.perf_counter() - debut:.1f} s,",
        'tokens_entree': tokens_entree,
        'tokens_sortie': tokens_sortie
    }))

    jsont_to_dict = dict(items)
    # print(json.dumps(jsont_to_dict, indent=2, ensure_ascii=False))

    print(f"{time.perf_counter() - debut:.1f} s,",
        reponse.usage.prompt_tokens, "tokens en entrée,",
        reponse.usage.completion_tokens, "en sortie")
    
    return jsont_to_dict

# Sans thumbnail : 12.8 s, 1058 tokens en entrée, 181 en sortie
# Avec thumbnail : 12.6 s, 1058 tokens en entrée, 180 en sortie
def prepare_image(image):
    source = CURRENT_PATH.parent / image
    photo = Path(source)

    # Ouvrir l'image avec Pillow
    with Image.open(photo) as img:
        # Convertir en RGB si nécessaire (par exemple pour les images PNG avec transparence ou palette)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Réduire l'image (conserve le ratio d'aspect, max 800x800)
        img.thumbnail((800, 800))

        # Enregistrer l'image dans un tampon mémoire en format JPEG
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85)  # quality est optionnel (défaut 75)

        # Encoder le contenu du tampon en Base64
        image_b64 = base64.b64encode(buffer.getvalue()).decode("ascii")

    return image_b64

def chercher_produit(image: str) -> dict:
    reponse_json = scanner_etiquette(image)

    produit = reponse_json.get("produit") or {}
    nom = produit.get("nom", "")
    code = produit.get("code_barres", "")

    nom_ou_code = ''
    if code is not None:
        nom_ou_code = code
    elif nom is not None:
        nom_ou_code = nom

    outils = CatalogueOutils()
    assistant = AssistantNutriScope(outils)

    assistant.reinitialiser()
    question = f"Donne-moi le Nutri-Score et les valeurs nutritionnelles de '{nom_ou_code}', et explique ce qui pèse sur son score."
    return assistant.demander(question)

if __name__ == '__main__':
    # scanner_etiquette('./data/photos/10_3608580065340_etiquette.jpg')

    # - 01 Nutella : pas de ligne « fibres » sur l'étiquette ;
    # scanner_etiquette('./data/photos/01_3017620422003_face.jpg')
    # scanner_etiquette('./data/photos/01_3017620422003_etiquette.jpg')

    # - 02 Prince : un tableau ordinaire, envoyé une fois en chemin, une fois en octets ;
    print(scanner_etiquette('./data/photos/02_7622210449283_etiquette.jpg'))

    # - 03 Skyr : des valeurs « < 0,5 g » ;
    # scanner_etiquette('./data/photos/03_3329770077003_etiquette.jpg')

    # - 08 Alpro : une boisson, valeurs pour 100 ml ;
    # scanner_etiquette('./data/photos/08_5411188112709_etiquette.jpg')

    # - 21 Madeleines : la « photo du tableau » ne montre aucun tableau.
    # scanner_etiquette('./data/photos/21_3178530410105_etiquette.jpg')