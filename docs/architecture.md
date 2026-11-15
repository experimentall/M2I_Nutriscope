# Architecture de l'assistant NutriScope

## Schéma de flux

```text
[UTILISATEUR]
      │
      ▼ (Pose une question)
┌─────────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 1 : Garde-fou d'entrée (verifier_requete_medicale)                │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ├──► [Requête médicale détectée] ──► Enregistre dans l'historique
      │                                     └──► Retourne refus immédiat (FIN)
      │
      ▼ [Requête valide]
┌─────────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 2 : Ajout à l'historique & Boucle d'agent (max_tours = 4)         │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 3 : Appel au LLM (OpenAI / Ollama - qwen3:8b)                     │
│  • Paramètres : temperature=0, max_tokens=500, reasoning_effort         │
│  • Contexte : PROMPT_SYSTEME + Historique + SCHEMA_CHERCHER_PRODUIT     │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ├──► [Le LLM répond directement sans outil] ──► Sauvegarde & Retour (FIN)
      │
      ▼ [Le LLM demande l'exécution d'un outil : tool_calls]
┌─────────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 4 : Validation stricte (CatalogueOutils.executer_appel_brut)      │
│  • Vérifie le nom ("chercher_produit") et le format JSON                │
│  • Contrôle les clés autorisées et les types (nom, code, limite, alt.)  │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ├──► [Erreur de validation] ──► Renvoie {"erreur": "..."} au LLM
      │
      ▼ [Arguments valides]
┌─────────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 5 : Recherche & Substitution (CatalogueOutils.chercher_produit)   │
│  • Recherche dans le DataFrame (code exact prioritaire, sinon nom)      │
│  • Détermine le statut : "introuvable" (0), "ok" (1), "ambigu" (>1)     │
│  • Si avec_alternatives=True ──► Appelle suggest_substitutes (top 3)    │
│  • Formate chaque fiche (formater_fiche) & détecte données manquantes   │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 6 : Retour au LLM & Synthèse finale                               │
│  • Injecte le résultat JSON (rôle: "tool") dans l'historique            │
│  • Retourne à l'ÉTAPE 3 pour que le LLM rédige la réponse en français   │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ▼ (Si boucle > 4 tours : message de repli / fallback)
[RÉPONSE FINALE + MÉTRIQUES D'AUDIT] (latence, tokens, trace des outils)
```

## Rôle des composants

### Branchés aujourd'hui
1. **Garde-fou d'entrée (`src/garde_fous.py`)** : Intercepte en amont les requêtes médicales évidentes (ex. *diabète, traitement, maladie, ordonnance*) avant même d'appeler le LLM, complété par une consigne système stricte pour les demandes hors alimentation.
2. **Orchestrateur (`src/assistant.py`)** : Gère l'historique de conversation, injecte la description de l'outil et exécute la boucle d'appel d'outils avec un plafond strict (`max_tours=4`) pour éviter toute boucle infinie.
3. **Validateur d'arguments (`src/outils.py`)** : Traite toute demande du LLM comme une entrée non fiable. Vérifie que le nom de l'outil est autorisé, parse le JSON sans `eval()`, contrôle les types et les bornes (`1 <= limite <= 5`) et rejette tout argument inconnu en renvoyant `{"erreur": "..."}`.
4. **Outil `chercher_produit` (`src/outils.py`)** : Interroge le catalogue réel (normalisation sans casse ni accents), applique la priorité du `code` sur le `nom`, gère les valeurs manquantes (`null` et jamais `0`) et signale les ambiguïtés.

### À venir
- **Outil `suggérer_alternative`** : Branchement du moteur de substitution du TP 16 pour proposer automatiquement des produits équivalents mieux notés.
- **Brique RAG** : Ajout d'une recherche par embeddings sur des documents nutritionnels officiels (PNNS) pour enrichir les explications sans hallucination.
- **API & Application** : Exposition de l'orchestrateur via FastAPI et interface utilisateur web.

*Données produits issues d'Open Food Facts (licence ODbL).*
