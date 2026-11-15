import json
import os
import time
from openai import OpenAI
from src.garde_fous import verifier_requete_medicale
from src.outils import CatalogueOutils
from dotenv import load_dotenv
load_dotenv()

SCHEMA_CHERCHER_PRODUIT = [
    {
        "type": "function",
        "function": {
            "name": "chercher_produit",
            "description": (
                "Recherche un ou plusieurs produits alimentaires dans le catalogue NutriScope "
                "par code-barres exact ou par nom. Renvoie le Nutri-Score, les valeurs nutritionnelles pour 100 g "
                "et, si demandé, les alternatives plus saines du même rayon."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "nom": {
                        "type": "string",
                        "description": "Nom ou partie du nom du produit recherché (ex: 'biscuit', 'lait')."
                    },
                    "code": {
                        "type": "string",
                        "description": "Code-barres exact du produit. Prime sur 'nom' si les deux sont fournis."
                    },
                    "limite": {
                        "type": "integer",
                        "description": "Nombre maximal de fiches à renvoyer (entier entre 1 et 5, défaut 3)."
                    },
                    "avec_alternatives": {
                        "type": "boolean",
                        "description": "Mettre à true si l'utilisateur demande une alternative ou un produit plus sain."
                    }
                },
                "required": []
            }
        }
    }
]

PROMPT_SYSTEME = """Tu es NutriScope, l'assistant nutritionnel d'un catalogue de produits alimentaires (données Open Food Facts).

RÈGLES STRICTES :
1. PÉRIMÈTRE : Réponds uniquement aux questions sur les produits alimentaires (Nutri-Score, valeurs nutritionnelles, comparaison, explication d'un score, recommandation d'alternative plus saine dans le catalogue).
2. REFUS : Refuse poliment toute question médicale (maladie, diabète, allergie, régime thérapeutique) en renvoyant vers un professionnel de santé. Refuse toute question hors alimentation.
3. ZÉRO INVENTION : Appelle OBLIGATOIREMENT l'outil `chercher_produit` avant de citer le moindre chiffre ou Nutri-Score. Ne invente JAMAIS une valeur. Si une valeur vaut `null` (`donnees_incompletes: true`), dis explicitement qu'elle est manquante dans le catalogue. Si un produit est `introuvable`, dis-le sans inventer.
4. AMBIGUÏTÉ : Si l'outil renvoie `statut: "ambigu"`, présente les produits trouvés et demande à l'utilisateur de préciser lequel il souhaite.
5. EXPLICATION & RECOMMANDATION : Pour expliquer un Nutri-Score, appuie-toi uniquement sur les nutriments de la fiche (sucres, acides gras saturés, sel, kcal élevés vs fibres, protéines). Pour recommander une alternative plus saine, appelle `chercher_produit` avec `avec_alternatives=true` et présente uniquement les produits listés dans `alternatives_saines` (s'il n'y en a aucun, indique qu'aucune alternative mieux notée n'est disponible dans ce rayon du catalogue).
Réponds en français, de manière claire, structurée et concise."""


class AssistantNutriScope:
    def __init__(self, catalogue_outils: CatalogueOutils, max_tours: int = 4):
        self.outils = catalogue_outils
        self.max_tours = max_tours
        self.base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
        self.api_key = os.getenv("LLM_API_KEY", "ollama")
        self.model = os.getenv("LLM_MODEL", "qwen3:8b")
        self.effort = os.getenv("LLM_EFFORT", "none")
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        self.historique = [{"role": "system", "content": PROMPT_SYSTEME}]
    
    def reinitialiser(self):
        self.historique = [{"role": "system", "content": PROMPT_SYSTEME}]

    def demander(self, question: str) -> dict:
        """
        Traite une question utilisateur et retourne un dictionnaire complet
        (réponse, trace des appels d'outils, latence, tokens) pour audit et démonstration.
        """
        debut = time.perf_counter()
        trace_outils = []
        tokens_entree = 0
        tokens_sortie = 0

        # Garde-fou en entrée
        refus = verifier_requete_medicale(question)
        if refus:
            self.historique.append({"role": "user", "content": question})
            self.historique.append({"role": "assistant", "content": refus})
            return {
                "reponse": refus,
                "modele": self.model,
                "appels_outils": [],
                "latence_s": round(time.perf_counter() - debut, 3),
                "tokens_entree": 0,
                "tokens_sortie": 0,
                "garde_fou_declenche": True
            }

        self.historique.append({"role": "user", "content": question})

        # Boucle d'appel d'outils
        for _ in range(self.max_tours):
            # probabilité la plus élevée
            # évite les réponses trop longues / boucle / budget
            options = {"temperature": 0, "max_tokens": 500}
            if self.effort:
                # Mode direct / reduction latence
                options["reasoning_effort"] = self.effort

            rep = self.client.chat.completions.create(
                model=self.model,
                messages=self.historique,
                tools=SCHEMA_CHERCHER_PRODUIT,
                **options
            )

            if rep.usage:
                tokens_entree += rep.usage.prompt_tokens or 0
                tokens_sortie += rep.usage.completion_tokens or 0

            message = rep.choices[0].message

            # Si le modèle rend du texte sans appel d'outil, la boucle se termine
            if not message.tool_calls:
                texte_final = (message.content or "").strip()
                self.historique.append({"role": "assistant", "content": texte_final})
                return {
                    "reponse": texte_final,
                    "modele": self.model,
                    "appels_outils": trace_outils,
                    "latence_s": round(time.perf_counter() - debut, 3),
                    "tokens_entree": tokens_entree,
                    "tokens_sortie": tokens_sortie,
                    "garde_fou_declenche": False
                }

            # Sinon, on ajoute la demande du modèle et on exécute chaque outil validé
            self.historique.append(message)
            for appel in message.tool_calls:
                resultat = self.outils.executer_appel_brut(
                    appel.function.name,
                    appel.function.arguments
                )
                trace_outils.append({
                    "outil": appel.function.name,
                    "arguments": appel.function.arguments,
                    "resultat": resultat
                })
                self.historique.append({
                    "role": "tool",
                    "tool_call_id": appel.id,
                    "content": json.dumps(resultat, ensure_ascii=False)
                })

        # Sécurité si max_tours est atteint
        fallback = "Je n'ai pas pu finaliser la recherche dans le catalogue dans la limite d'étapes autorisée."
        self.historique.append({"role": "assistant", "content": fallback})
        return {
            "reponse": fallback,
            "modele": self.model,
            "appels_outils": trace_outils,
            "latence_s": round(time.perf_counter() - debut, 3),
            "tokens_entree": tokens_entree,
            "tokens_sortie": tokens_sortie,
            "garde_fou_declenche": False
        }
