# Technical Story : Ingestion Open Food Facts et mise en place de l'API FastAPI

**Épic de rattachement :** MVP - Architecture & Socle Technique

## 1. Description (Format Technique)
* **En tant que** Développeur Backend / Data Engineer du projet NutriScope
* **Je souhaite** mettre en place un pipeline d'ingestion de la base Open Food Facts et exposer les données via une API FastAPI performante
* **Afin d'** alimenter en temps réel l'application mobile et de garantir un temps de réponse inférieur à 3 secondes lors du scan ou de la recherche d'un produit.

## 2. Critères d'acceptation (Spécifications Techniques)

### Scénario 1 : Ingestion et synchronisation de la base Open Food Facts
* **Étant donné** le dump de données public mis à disposition par Open Food Facts (format Parquet)
* **Quand** le script de synchronisation hebdomadaire s'exécute en tâche de fond
* **Alors** le système télécharge, filtre et stocke les informations essentielles (code-barres, nom, marque, ingrédients, valeurs nutritionnelles, catégories) dans notre base de données locale
* **Et** le pipeline doit nettoyer ou marquer les fiches contenant des données manifestement aberrantes ou incomplètes pour éviter de fausser le modèle de prédiction.

### Scénario 2 : Performance de l'API FastAPI (Contrainte < 3 secondes)
* **Étant donné** une requête d'un smartphone utilisateur envoyant un code-barres à l'API
* **Quand** l'endpoint `GET /api/v1/products/{barcode}` est sollicité
* **Alors** FastAPI interroge la base locale, applique la logique de prédiction du Nutri-Score et retourne le payload JSON structuré
* **Et** le temps de réponse total de cet endpoint (hors latence réseau mobile) doit être **inférieur à 200ms** pour garantir le respect du seuil de 3 secondes côté interface utilisateur.

### Scénario 3 : Disponibilité des endpoints clés pour le MVP
* **Étant donné** les besoins de développement de l'application front-end (mobile)
* **Quand** l'API FastAPI est déployée en environnement de staging/production
* **Alors** elle doit exposer de manière sécurisée et documentée (Swagger/OpenAPI accessible sur `/docs`) les endpoints suivants :
  * `GET /api/v1/products/{barcode}` : Récupération et analyse d'un produit.
  * `POST /api/v1/products/{barcode}/compare` : Comparaison avec un second produit.
  * `POST /api/v1/feedback` : Réception des signalements d'erreurs.
  * `POST /api/v1/chat` : Point d'entrée pour l'assistant conversationnel encadré (RAG).

### Scénario 4 : Journalisation et traçabilité de l'usage
* **Étant donné** le trafic de production sur l'API FastAPI
* **Quand** une requête est traitée (succès ou échec)
* **Alors** l'API génère des logs standardisés contenant le code-barres ciblé, le statut de la réponse (200, 404, 500) et le temps d'exécution
* **Et** ces métriques anonymisées doivent être structurées de manière à pouvoir alimenter automatiquement le **Dashboard d'usage** des équipes non-techniciennes.

## 3. Règles de gestion & Contraintes architecturales
* **Architecture RAG & IA :** L'API doit être conçue pour s'interfacer nativement avec la brique de vectorisation des données et le modèle LLM pour la partie *Assistant conversationnel*, en limitant le nombre de requêtes sortantes pour maîtriser les coûts de jetons (tokens).
* **Sécurité & RGPD :** L'API ne stocke aucun log nominatif, aucune adresse IP et aucun identifiant publicitaire. L'endpoint `/chat` et `/feedback` doivent être protégés contre le spam et les injections de prompts par un mécanisme de limitation de requêtes (*Rate Limiting*).
* **Fiabilité des données :** En cas d'indisponibilité ou de corruption de la base Open Food Facts locale, l'API doit renvoyer un code d'erreur propre et géré (`404` ou `422` avec un message explicite) permettant au front-end d'afficher l'écran dégradé prévu.
