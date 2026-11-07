# User Story : Tableau de bord (Dashboard) interne de suivi de l'usage et de la qualité

**Épic de rattachement :** MVP - Outils internes & Pilotage

## 1. Description
* **En tant que** membre de l'équipe non-technicienne
* **Je souhaite** accéder à un tableau de bord interne simple et visuel recensant les statistiques d'usage de l'application et les alertes de données
* **Afin de** piloter le succès du lancement du pilote, d'analyser l'engagement et de traiter en priorité les erreurs de données remontées par les utilisateurs.

## 2. Critères d'acceptation

### Scénario 1 : Visualisation des KPI d'adoption et de performance globale
* **Étant donné** que je suis connecté à l'interface du dashboard interne
* **Quand** l'écran principal (Vue Générale) se charge
* **Alors** le système affiche les indicateurs clés agrégés en temps réel :
  * Le nombre total de scans effectués (par jour / semaine).
  * Le volume de questions posées à l'agent conversationnel.
  * Le temps de réponse moyen de l'API (pour vérifier le respect des < 3 secondes).
  * Les 10 produits les plus scannés en magasin.

### Scénario 2 : Traitement des signalements d'erreurs et produits inconnus
* **Étant donné** que des clients ont soumis des retours via le bouton "Signaler une erreur" en magasin
* **Quand** je me rends sur l'onglet "Gestion de la Qualité"
* **Alors** le système affiche la liste triée par volume de signalements comprenant :
  * Le code-barres et le nom du produit concerné.
  * La nature du problème coché (Donnée fausse, Produit inconnu, etc.).
  * Un bouton d'action pour forcer la resynchronisation manuelle de la fiche avec *Open Food Facts*.

### Scénario 3 : Surveillance des coûts de l'Agent Conversationnel (IA)
* **Étant donné** la nécessité de maîtriser le budget des modèles génératifs
* **Quand** je consulte l'onglet de suivi financier du Chatbot
* **Alors** le dashboard affiche une estimation du nombre de jetons (*tokens*) consommés
  * Et l'équivalent du coût financier généré (en euros), mis à jour quotidiennement.

### Scénario 4 : Respect de l'anonymat et sécurité des données (RGPD)
* **Étant donné** que je navigue sur n'importe quel écran du tableau de bord
* **Quand** je consulte les données d'usage ou les logs d'activité
* **Alors** le dashboard ne doit afficher **aucune donnée personnelle identifiable** (pas d'adresse email, pas d'identifiant d'appareil, pas de géolocalisation précise) conformément aux règles de minimisation.

## 3. Règles de gestion & Contraintes du produit
* **Simplicité technique :** L'interface doit être épurée, sans jargon technique (SQL, logs bruts). Elle doit être utilisable immédiatement par les équipes métiers pour préparer les rapports destinés au conseil d'administration.
* **Actualisation :** Les données d'usage et de performance sont actualisées au minimum toutes les heures (pas besoin d'un flux à la milliseconde pour le MVP).
* **Accessibilité :** Ce dashboard est une application web interne sécurisée, accessible uniquement via le réseau de l'entreprise ou un accès authentifié sécurisé.
