# User Story : Collecte de retours utilisateurs et signalement d'erreurs

**Épic de rattachement :** MVP - Qualité des données & Feedback

## 1. Description
* **En tant que** parent pressé faisant ses courses en magasin
* **Je souhaite** pouvoir signaler facilement une erreur ou une donnée manquante sur la fiche d'un produit
* **Afin de** contribuer à la fiabilité de l'application et d'aider l'équipe à corriger les informations inexactes d'Open Food Facts.

## 2. Critères d'acceptation

### Scénario 1 : Signalement d'une erreur sur un produit existant
* **Étant donné** que je consulte la fiche d'un produit et que je remarque une incohérence (ex: mauvais Nutri-Score, ingrédients erronés)
* **Quand** j'appuie sur le bouton "Signaler une erreur"
* **Alors** l'application m'affiche un menu de sélection simple et rapide (ex: "Donnée fausse", "Image incorrecte", "Produit périmé/obsolète")
* **Et** elle me permet de valider mon signalement en un seul clic sans m'obliger à saisir du texte.

### Scénario 2 : Signalement depuis un écran de produit inconnu
* **Étant donné** que je viens de scanner un code-barres qui n'existe pas dans la base de données
* **Quand** l'écran "Produit non trouvé" s'affiche
* **Alors** un bouton d'action me propose de "Signaler ce produit manquant"
* **Et** la validation envoie automatiquement le code-barres concerné à l'équipe technique pour investigation.

### Scénario 3 : Confirmation fluide et rassurante
* **Étant donné** que je viens de soumettre un signalement (produit inconnu ou erroné)
* **Quand** l'envoi est validé avec succès par l'API
* **Alors** l'interface affiche un message de remerciement court et bienveillant (ex: "Merci ! Votre retour nous aide à rendre NutriScope plus fiable.")
* **Et** l'application me redirige automatiquement vers l'écran d'accueil/scanner pour ne pas bloquer mes courses.

### Scénario 4 : Remontée des données dans le tableau de bord interne
* **Étant donné** qu'un utilisateur soumet un feedback en magasin
* **Quand** le signalement est enregistré par le système
* **Alors** la donnée est immédiatement poussée vers le tableau de bord d'usage destiné aux équipes non-techniciennes (Marketing/Produit)
* **Et** elle inclut obligatoirement : le code-barres, le type d'erreur coché, la source (Open Food Facts) et l'horodatage.

## 3. Règles de gestion & Contraintes strictes
* **Simplicité absolue :** Le parcours de signalement doit prendre moins de 5 secondes pour respecter le contexte de l'utilisateur sous contrainte de temps en magasin.
* **RGPD & Anonymat :** La collecte des retours est totalement anonyme. Aucun identifiant utilisateur, donnée de localisation précise ou historique personnel n'est attaché au signalement.
* **Supervision humaine :** Les retours collectés doivent être structurés de manière à pouvoir être traités ultérieurement par une procédure de révision ou de correction humaine, conformément aux exigences de gouvernance du projet.
