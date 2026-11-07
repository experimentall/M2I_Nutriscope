# User Story : Configuration du profil utilisateur (Préférences alimentaires simples)

**Épic de rattachement :** MVP - Personnalisation & RGPD

## 1. Description
* **En tant que** client de l'application NutriScope
* **Je souhaite** configurer mes préférences alimentaires non médicales de manière simple et rapide
* **Afin que** l'application adapte l'affichage des fiches produits et filtre automatiquement les alternatives plus saines selon mes choix.

## 2. Critères d'acceptation

### Scénario 1 : Configuration initiale des préférences simples
* **Étant donné** que je me rends sur l'écran "Mon Profil" (accessible sans obligation de créer un compte utilisateur complet pour le MVP)
* **Quand** je sélectionne mes préférences parmi les choix simples disponibles :
  * Régime : Végétarien / Végétalien (Vegan)
  * Label : Certifié Bio
  * Critère : Sans alcool / Budget indicatif restreint
* **Alors** mes choix sont enregistrés localement sur mon smartphone.

### Scénario 2 : Refus strict de la collecte de données médicales ou de santé
* **Étant donné** l'écran de configuration du profil utilisateur
* **Quand** l'interface me présente les filtres et préférences disponibles
* **Alors** l'application ne doit proposer **aucun choix lié à une pathologie** (ex: diabète, cholestérol) ou à une allergie médicale critique (ex: arachide, gluten)
* **Et** un message informatif clair doit rappeler le refus du diagnostic ou du conseil médical personnalisé.

### Scénario 3 : Application des préférences lors de l'affichage produit
* **Étant donné** que j'ai activé le filtre "Certifié Bio" et "Végétarien" dans mon profil
* **Quand** je scanne un produit qui ne correspond pas à ces critères (ex: un plat préparé à base de viande non bio)
* **Alors** la fiche produit affiche un indicateur visuel clair et fluide signalant que le produit ne correspond pas à mes préférences
* **Et** le moteur de recommandation adapte sa brique pour ne proposer que des alternatives strictement végétariennes et bio.

### Scénario 4 : Transparence, consentement et suppression (Conformité RGPD)
* **Étant donné** que je souhaite effacer mes traces de l'application
* **Quand** je clique sur le bouton "Réinitialiser mes préférences" ou "Supprimer mes données" depuis l'écran profil
* **Alors** l'ensemble des filtres configurés est instantanément purgé de l'application
* **Et** le système cesse toute personnalisation sans conserver d'historique sur un serveur externe.

## 3. Règles de gestion & Contraintes strictes
* **Minimisation des données :** Conformément aux exigences du Délégué à la Protection des Données (DPD), l'application applique le principe de minimisation. Elle collecte le strict minimum pour la personnalisation en magasin et n'associe aucun profil à des données d'identité réelles.
* **Complexité vs Simplicité :** L'interface doit rester épurée pour éviter de créer de la frustration ou de la confusion chez les familles pressées en situation de courses.
* **Performance :** L'application des filtres du profil lors du scan d'un produit ne doit pas ralentir l'affichage, qui reste soumis à la contrainte absolue de **moins de 3 secondes**.
