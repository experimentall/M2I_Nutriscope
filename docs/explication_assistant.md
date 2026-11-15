# Architecture et Flux d'Exécution — Assistant NutriScope

Ce document détaille le cycle de vie d'une requête au sein de l'assistant **NutriScope**, depuis la validation de sécurité initiale jusqu'à la génération de la réponse auditée.

---

## Phase 0 : Initialisation du système (Démarrage)

Avant tout échange avec l'utilisateur, deux composants préparent l'environnement :

* **Préparation du catalogue (`CatalogueOutils.__init__`)** : 
  * Charge le fichier source au format Parquet défini par `PARQUET_SOURCE`.
  * Nettoie les données via `preparation_donnee()` et génère deux colonnes indexables : `code_str` (code-barres nettoyé) et `nom_norm` (nom normalisé sans accents/casse).
  * Précalcule les échelles de comparaison nutritionnelle (`compute_scales`) sur l'ensemble des enregistrements pour optimiser le moteur de substitution.
* **Configuration de l'agent (`AssistantNutriScope.__init__`)** : 
  * Initialise le client compatible OpenAI (par défaut sur Ollama en local avec le modèle `qwen3:8b`).
  * Initialise `self.historique` avec le `PROMPT_SYSTEME` contenant les règles strictes de périmètre, de non-invention et de formatage.

---

## Étape 1 : Filtrage de sécurité en entrée (Garde-fou)

* Dès l'appel de la méthode `demander(question)`, le texte est analysé par `verifier_requete_medicale(question)`.
* **Si une thématique médicale est détectée** (diabète, allergie, pathologie, régime thérapeutique) :
  * Le système court-circuite l'appel au LLM.
  * La question et le message de refus sont ajoutés à l'historique.
  * La fonction retourne immédiatement le résultat avec `garde_fou_declenche: True` et `0` token consommé.

---

## Étape 2 : Initialisation de la boucle de raisonnement

* Si la question est autorisée, elle est ajoutée à `self.historique` avec le rôle `"user"`.
* L'assistant démarre une boucle bornée par `max_tours` (`4` itérations par défaut) afin de prévenir toute boucle infinie d'appels d'outils.

---

## Étape 3 : Appel au modèle de langage (LLM)

* L'historique complet et la définition JSON de l'outil (`SCHEMA_CHERCHER_PRODUIT`) sont transmis au modèle.
* Les paramètres d'inférence suivants sont appliqués :
  * `temperature: 0` pour garantir des réponses déterministes et factuelles.
  * `max_tokens: 500` pour limiter la longueur des réponses.
  * `reasoning_effort` (configurable via `LLM_EFFORT`) pour contrôler la latence de réflexion.
* **Deux issues possibles** :
  1. **Réponse directe** : Le modèle n'appelle aucun outil (ex. : salutation ou refus hors-périmètre alimentaire). La réponse est sauvegardée et retournée à l'utilisateur.
  2. **Appel d'outil (`tool_calls`)** : Le modèle demande l'exécution de `chercher_produit` avec des arguments extraits de la question.

---

## Étape 4 : Validation stricte des arguments (Pare-feu technique)

Avant d'interroger les données, la demande brute du modèle passe par `CatalogueOutils.executer_appel_brut()` :

* **Contrôle du nom et du format** : Vérifie que l'outil est bien `chercher_produit` et que les arguments forment un objet JSON valide.
* **Contrôle des clés** : Rejette toute clé non autorisée (seules `nom`, `code`, `limite` et `avec_alternatives` sont acceptées).
* **Contrôle des types et contraintes** :
  * Au moins `nom` ou `code` doit être renseigné (chaînes de caractères).
  * `limite` doit être un entier strictement compris entre `1` et `5` (défaut : `3`).
  * `avec_alternatives` doit être un booléen (défaut : `False`).
* En cas d'anomalie, un dictionnaire `{"erreur": "..."}` est renvoyé au LLM pour qu'il puisse corriger son appel au tour suivant.

---

## Étape 5 : Recherche métier et substitution (`chercher_produit`)

Une fois les paramètres validés, le traitement métier s'exécute sur le DataFrame en mémoire :

1. **Filtrage** : Recherche exacte sur `code_str` en priorité. À défaut, recherche de sous-chaîne sur `nom_norm`.
2. **Qualification du statut** :
   * `0` résultat $\rightarrow$ `statut: "introuvable"`.
   * `1` résultat $\rightarrow$ `statut: "ok"`.
   * `> 1` résultat $\rightarrow$ `statut: "ambigu"`.
3. **Calcul des alternatives** : Si `avec_alternatives=True`, `suggest_substitutes()` identifie jusqu'à `3` produits plus sains dans la même catégorie en utilisant les échelles précalculées.
4. **Formatage de la fiche (`formater_fiche`)** :
   * Convertit les valeurs manquantes (`NaN`) en `None` (`null` en JSON).
   * Passe le drapeau `incomplet` à `True` si le Nutri-Score ou l'un des 7 nutriments clés (`kcal`, `lipides`, `satures`, `sucres`, `sel`, `fibres`, `proteines`) est manquant.

---

## Étape 6 : Synthèse finale et métriques d'audit

* Le résultat JSON est injecté dans `self.historique` avec le rôle `"tool"`, et la boucle retourne à l'**Étape 3**.
* Le LLM rédige sa réponse finale en français en s'appuyant uniquement sur les données reçues (mention des valeurs manquantes, demande de précision si `ambigu`, ou présentation des `alternatives_saines`).
* Si `max_tours` est dépassé sans réponse finale, un message de repli (*fallback*) est renvoyé.
* L'appel retourne un dictionnaire complet contenant la réponse ainsi que les données d'audit : `modele`, `appels_outils`, `latence_s`, `tokens_entree`, `tokens_sortie` et `garde_fou_declenche`.
