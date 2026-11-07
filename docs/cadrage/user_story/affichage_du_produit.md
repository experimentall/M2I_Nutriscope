# User Story : Fiche Produit et Analyse Nutritionnelle Épurée

**Épic de rattachement :** MVP - Restitution de l'information

## 1. Description
* **En tant que** parent pressé faisant ses courses en magasin
* **Je souhaite** visualiser une fiche produit claire, synthétique et épurée après avoir scanné ou recherché un article
* **Afin de** comprendre instantanément sa qualité nutritionnelle et de décider si je l'achète sans perdre de temps.

---

## 2. Critères d'acceptation

### Scénario 1 : Affichage des informations nutritionnelles clés
* **Étant donné que** l'application a identifié avec succès le produit scanné
* **Quand** la fiche produit se charge (en moins de 3 secondes)
* **Alors** l'écran doit afficher les éléments obligatoires suivants :
  * Le nom du produit et sa marque
  * La prédiction graphique du Nutri-Score (A, B, C, D ou E)
  * Une explication textuelle synthétique en langage simple (ex : *"Faible en matières grasses, mais teneur élevée en sucre"*)
  * La source des données (Open Food Facts) ainsi que la date de dernière mise à jour.

### Scénario 2 : Transparence sur les données manquantes ou limites
* **Étant donné que** le produit possède des fiches incomplètes ou anciennes dans Open Food Facts
* **Quand** je consulte la fiche produit
* **Alors** l'application affiche un indicateur visuel discret signalant les limites de l'information (ex : *"Données nutritionnelles incomplètes"*)
* **Et** elle affiche un bouton d'action pour me permettre de signaler une erreur ou une donnée manquante.

### Scénario 3 : Absence de jargon médical ou thérapeutique
* **Étant donné que** le produit analysé contient des allergènes ou des ingrédients spécifiques (ex : gluten, sucre pour un profil potentiellement diabétique)
* **Quand** l'explication du Nutri-Score ou des composants est générée
* **Alors** le texte doit rester purement informatif et vulgarisé
* **Et** l'application ne doit jamais afficher de diagnostic, de contre-indication médicale ou de mention du type *"Recommandé pour les diabétiques"*.

---

## 3. Règles de gestion & Contraintes du MVP

* **Interface mobile fluide** : L'UI doit être rassurante et optimisée pour une lecture à une seule main en rayon de magasin. Aucun élément de texte ne doit être culpabilisant ou moralisateur.
* **Performance** : L'affichage complet de la fiche produit (appel API FastAPI + génération de l'explication) ne doit pas dépasser le seuil de performance de 3 secondes.
* **RGPD (Minimisation)** : L'affichage de cette fiche standard ne nécessite et ne doit collecter aucune donnée personnelle de l'utilisateur à ce stade du MVP.
