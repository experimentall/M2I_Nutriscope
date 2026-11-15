# ADR 0001 — Utiliser un modèle local (`qwen3:8b` via Ollama) pour l'assistant NutriScope

Date : 2026-11-09  
Statut : Acceptée

## Contexte
NutriScope développe un assistant conversationnel capable d'interroger un catalogue alimentaire (Open Food Facts), d'expliquer le Nutri-Score, de comparer des produits et de refuser les demandes médicales ou hors sujet. Le prototype doit exécuter des appels d'outils (`chercher_produit`) de manière fiable, sans fuite de données et à coût maîtrisé pendant la phase de développement et de démonstration.

## Options
1. **Modèle local (`qwen3:8b` servi via Ollama en Q4)** : exécution sur le GPU local (8 Go de VRAM) via une API compatible OpenAI (`localhost:11434/v1`).
2. **Agrégateur API commerciale (`openai/gpt-oss-20b:floor` via OpenRouter)** : hébergement tiers, facturation au token avec raisonnement obligatoire.
3. **API hébergée en Europe (`mistral-small-latest` via Mistral AI)** : modèle européen hébergé dans l'UE, facturation au token.

## Critères

| Critère | Local (`qwen3:8b` Q4) | OpenRouter (`gpt-oss-20b`) | Mistral AI (`mistral-small`) |
|---|---|---|---|
| **Confidentialité** | Totale (aucune donnée ne sort) | Faible (hébergeurs tiers multiples) | Moyenne/Bonne (hébergement UE, sous contrat) |
| **Coût** | 0,00 $ par appel (matériel amorti) | ~0,018 $ / 0,09 $ par 1M tokens + raisonnement | ~0,15 $ / 0,60 $ par 1M tokens |
| **Latence (mesurée)** | ~0,40 s à 1,50 s par tour (100 % GPU) | ~1,5 s à 3 s (réseau + raisonnement) | ~1,0 s à 2,0 s (réseau) |
| **Appel d'outils** | Natif et fiable (`reasoning_effort="none"`) | Natif, mais verbeux en tokens de pensée | Natif et fiable |

*Mesure relevée sur poste local (GPU 8 Go, `num_ctx=4096`, `temperature=0`, `reasoning_effort="none"`) :*
- Appel simple sans outil : **0,38 s** (48 tokens d'entrée).
- Boucle complète avec 1 appel à `chercher_produit` (2 tours LLM) : **1,42 s** (196 tokens de description d'outil inclus à chaque tour).

## Décision
Nous retenons **l'option 1 : `qwen3:8b` en local via Ollama** avec `temperature=0` et `reasoning_effort="none"`. 
Ce choix garantit la confidentialité totale des requêtes utilisateurs, supprime tout risque de dépassement budgétaire lors des tests itératifs et offre une latence inférieure à 1,5 seconde pour un appel outillé, tout en tenant confortablement dans 8 Go de VRAM (~5,2 Go de poids + contexte). Le client utilise le SDK `openai` standard avec configuration par variables d'environnement (`.env`), permettant de basculer vers Mistral AI en production sans réécrire le code métier.

## Conséquences
- **Positives :** Coût marginal nul, souveraineté des données, reproductibilité locale (`temperature=0`), code agnostique du fournisseur.
- **Négatives :** Nécessite une machine équipée d'un GPU d'au moins 8 Go pour éviter le basculement sur CPU (chute de débit), et impose de surveiller manuellement la fenêtre de contexte (`num_ctx=4096`) car Ollama tronque silencieusement en cas de dépassement.
