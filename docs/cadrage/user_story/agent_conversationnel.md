# User Story : Assistant conversationnel limité et encadré pour les produits alimentaires

**Épic de rattachement :** MVP - Assistant IA & RAG

## 1. Description
* **En tant que** parent pressé faisant ses courses en magasin
* **Je souhaite** poser une question simple en langage naturel à un assistant spécialisé sur un produit alimentaire
* **Afin d'** obtenir une réponse claire, fiable et nuancée sans avoir à analyser moi-même des données nutritionnelles trop techniques.

## 2. Critères d'acceptation

### Scénario 1 : Réponse réussie sur les qualités d'un produit
* **Étant donné** que je consulte la fiche d'un produit et que j'ouvre la fenêtre de l'assistant
* **Quand** je pose une question fermée ou ciblée sur l'alimentation (ex: "Pourquoi ce produit est-il trop salé ?" ou "Est-ce adapté pour un enfant ?")
* **Alors** l'assistant génère une réponse courte et vulgarisée en **moins de 3 secondes**
* **Et** cette réponse doit être fondée sur le catalogue de référence et des sources publiques fiables.

### Scénario 2 : Refus strict et automatique des demandes médicales
* **Étant donné** que j'utilise l'assistant conversationnel en magasin
* **Quand** je pose une question d'ordre médical, thérapeutique ou liée à une pathologie (ex: "Puis-je manger ceci avec mon diabète ?" ou "Est-ce bon pour mon hypertension ?")
* **Alors** l'assistant refuse poliment et instantanément d'y répondre via une formulation encadrée
* **Et** il m'affiche un message neutre rappelant que NutriScope n'est pas un dispositif médical et invite à consulter un professionnel de santé.

### Scénario 3 : Gestion des questions hors sujet (Hors alimentation)
* **Étant donné** que la fenêtre de discussion est ouverte
* **Quand** je pose une question totalement étrangère à l'alimentation ou aux produits de l'application (ex: "Quel temps fait-il à Lille ?" ou "Raconte-moi une histoire")
* **Alors** l'agent conversationnel applique une règle de garde-fou (*guardrail*)
* **Et** il me redirige poliment vers son rôle initial (ex: "Je suis un assistant spécialisé dans l'aide au choix alimentaire. Je ne peux pas répondre à cette question.").

### Scénario 4 : Transparence et explicabilité de la réponse
* **Étant donné** que l'assistant m'affiche sa réponse textuelle
* **Quand** je lis l'explication générée à l'écran
* **Alors** l'interface doit afficher de manière transparente la source des informations utilisées pour construire la réponse (ex: données du catalogue Open Food Facts ou directives nutritionnelles publiques) pour garantir la traçabilité.

## 3. Règles de gestion & Contraintes strictes
* **Maîtrise des coûts (Finances) :** Pour limiter les coûts d'infrastructure et d'utilisation des modèles génératifs, les interactions par utilisateur sont bridées (ex: 3 questions maximum par session/produit). Les invites système (*system prompts*) doivent être optimisées pour limiter la consommation de jetons (*tokens*).
* **Sécurité & Image de marque :** L'assistant utilise des réponses encadrées pour éviter les hallucinations de l'IA, les dérives de langage ou les tentatives de détournement (*prompt injection*). Le ton ne doit jamais être culpabilisant ou moralisateur.
* **Performance technique :** Bien qu'il s'agisse d'un modèle génératif, la réponse standard simplifiée doit s'afficher en moins de 3 secondes pour ne pas bloquer l'utilisateur dans le rayon du magasin.
