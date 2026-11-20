import json
import os
import time
from openai import OpenAI
from src.assistant.garde_fous import verifier_requete_medicale
from src.assistant.outils import CatalogueOutils
from dotenv import load_dotenv
load_dotenv()

TEMPERATURE = 0
MAX_TOKENS = 1000 # environ 750 mots

SCHEMA_OUTILS = [
    {
        "type": "function",
        "function": {
            "name": "chercher_produit",
            "description": (
                "Recherche un ou plusieurs produits alimentaires dans le catalogue NutriScope "
                "par code-barres exact ou par nom. Renvoie le Nutri-Score et les valeurs nutritionnelles pour 100 g."
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
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_substitutes",
            "description": (
                "Recherche des alternatives plus saines du même rayon à partir du code-barres exact d'un produit. "
                "À appeler UNIQUEMENT si l'utilisateur demande explicitement une alternative ou un produit plus sain, "
                "après avoir identifié le code-barres du produit initial avec 'chercher_produit'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code-barres exact du produit de référence."
                    },
                    "k": {
                        "type": "integer",
                        "description": "Nombre maximal d'alternatives à renvoyer (entier entre 1 et 5, défaut 3)."
                    }
                },
                "required": ["code"]
            }
        }
    }
]

PROMPT_SYSTEME = """Tu es NutriScope, un assistant strictement limité au catalogue alimentaire Open Food Facts.

SUIS CET ALGORITHME DANS L'ORDRE À CHAQUE QUESTION :

ÉTAPE 1 : FILTRAGE DU PÉRIMÈTRE
- SI la question porte sur la santé, une maladie (diabète, cholestérol...), une allergie ou un régime médical : REFUSE et renvoie vers un professionnel de santé.
- SI la question ne concerne pas un produit alimentaire du catalogue : REFUSE poliment.

ÉTAPE 2 : APPEL D'OUTIL OBLIGATOIRE
- Tu n'as AUCUNE connaissance propre. Appelle TOUJOURS `chercher_produit` avant de répondre (un appel par produit en cas de comparaison).

ÉTAPE 3 : ANALYSE DU RÉSULTAT JSON DE L'OUTIL
- SI `statut == "introuvable"` : dis uniquement que le produit est absent du catalogue. N'invente rien.
- SI `statut == "ambigu"` : STOP. Ne donne AUCUNE valeur nutritionnelle, AUCUN Nutri-Score et AUCUNE explication. Liste uniquement les noms et codes-barres des produits trouvés et demande à l'utilisateur de choisir.
- SI `statut == "ok"` :
  * Désigne toujours les produits par leur nom exact tel qu'il apparaît dans le JSON.
  * Pour CHAQUE produit présenté, commence OBLIGATOIREMENT par cette ligne exacte AVANT la liste des nutriments :
    **NOM DU PRODUIT** (code-barres : CODE) — Nutri-Score : SCORE
  * Affiche OBLIGATOIREMENT l'intégralité des 7 nutriments pour 100 g présents dans le JSON (kcal, lipides, acides gras saturés, sucres, sel, fibres, protéines) sous forme de liste à puces, même si la question ne porte que sur certains nutriments. Si une valeur est `null` (`incomplet: true`), écris "donnée manquante". N'invente aucun chiffre.
  * Pour expliquer le Nutri-Score, cite uniquement les nutriments de la fiche (sucres, acides gras saturés, sel, kcal élevés vs fibres, protéines), sans conseil médical.
  * SI la question est une comparaison entre plusieurs produits : conclus en 2 phrases courtes et simples maximum. Compare directement les valeurs demandées et le Nutri-Score en vérifiant le sens de comparaison (un chiffre plus grand signifie "plus", un chiffre plus petit signifie "moins").
  * SI l'utilisateur a demandé une alternative : cite UNIQUEMENT la liste `alternatives_saines` du JSON. Pour chaque alternative, affiche son Nutri-Score et ses valeurs, puis cite UNIQUEMENT les critères où elle est réellement meilleure que le produit initial (meilleur Nutri-Score, ou valeur strictement inférieure en sucres, saturés ou kcal). Ne dis jamais qu'une valeur est inférieure si le chiffre est plus élevé. Si la liste est vide, écris "Aucune alternative plus saine n'est disponible dans ce rayon". N'affiche pas d'alternatives si l'utilisateur n'en a pas demandé.

FORMAT : Réponds en français, de manière brève et factuelle."""


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
            options = {"temperature": TEMPERATURE, "max_tokens": MAX_TOKENS}
            if self.effort:
                # Mode direct / reduction latence
                options["reasoning_effort"] = self.effort

            rep = self.client.chat.completions.create(
                model=self.model,
                messages=self.historique,
                tools=SCHEMA_OUTILS,
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
