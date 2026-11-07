# User Story : Comparaison de deux produits en rayon

**Épic de rattachement :** MVP - Module de décision / Restitution

## 1. Description
* **En tant que** parent pressé faisant ses courses en magasin
* **Je souhaite** comparer côte à côte deux produits de la même catégorie selon des critères clairs et transparents
* **Afin d'** identifier immédiatement le meilleur choix nutritionnel pour ma famille sans perdre de temps à alterner entre deux fiches.

## 2. Critères d'acceptation

### Scénario 1 : Déclenchement de la comparaison depuis une fiche produit
* **Étant donné** que je consulte la fiche synthétique d'un premier produit (Produit A)
* **Quand** j'appuie sur le bouton "Comparer ce produit"
* **Alors** l'application m'invite à scanner un second produit (Produit B) ou à le rechercher par son nom
* **Et** elle conserve le Produit A en mémoire pour l'étape suivante.

### Scénario 2 : Affichage de la vue comparative côte à côte
* **Étant donné** que j'ai sélectionné le Produit A et le Produit B
* **Quand** la vue comparative se charge (en moins de 3 secondes)
* **Alors** l'écran du smartphone affiche les deux produits côte à côte sous forme de tableau épuré
* **Et** les critères affichés doivent être strictement transparents et factuels :
  * Le Nutri-Score prédit de chaque produit (A, B, C, D ou E)
  * Les indicateurs clés divergents (ex: taux de sucre, matières grasses, présence de sel)
  * Les préférences simples si elles sont configurées (ex: mention "Bio" ou "Végétarien").

### Scénario 3 : Pédagogie et explication du "Meilleur choix"
* **Étant donné** la visualisation du tableau comparatif entre le Produit A et le Produit B
* **Quand** je regarde la synthèse à l'écran
* **Alors** l'application met en valeur de manière visuelle et rassurante le produit ayant les meilleures qualités nutritionnelles globales
* **Et** elle affiche une phrase d'explication simple et non technique (ex: "Le Produit A est recommandé car il contient deux fois moins d'acides gras saturés que le Produit B").

### Scénario 4 : Gestion de produits de catégories totalement différentes (Incohérence)
* **Étant donné** que j'ai sélectionné une boîte de biscuits (Produit A) et que je tente de la comparer avec une bouteille de shampoing ou un produit d'une autre catégorie (Produit B)
* **Quand** le système vérifie la cohérence des catégories issues de la base *Open Food Facts*
* **Alors** l'application m'affiche une alerte fluide et bienveillante (ex: "La comparaison est plus utile entre deux produits alimentaires similaires (ex: deux paquets de gâteaux) ! Vous souhaitez plutôt afficher la fiche du Produit B ?").

## 3. Règles de gestion & Contraintes strictes
* **Refus du conseil médical :** L'explication du meilleur choix ne doit reposer sur aucun argument médical, traitement de santé ou pathologie. Le classement doit rester purement nutritionnel et vulgarisé.
* **Neutralité commerciale :** Le choix mis en valeur par l'application dépend uniquement des données objectives d'Open Food Facts. Aucun partenariat avec un distributeur ou une marque ne doit biaiser ou influencer la recommandation lors de la comparaison.
* **Contrainte de temps & UI :** L'affichage doit être ultra-lisible, optimisé pour l'écran d'un smartphone manipulé d'une seule main en situation de courses. La réponse globale de la brique (FastAPI) doit respecter le seuil de performance de **moins de 3 secondes**.
