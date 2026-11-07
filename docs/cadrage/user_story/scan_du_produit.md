# User Story : Fonctionnalité de Scan Produit

**Épic de rattachement :** MVP - Module d'acquisition produit

## 1. Description
* **En tant que** parent pressé faisant ses courses en magasin
* **Je souhaite** pouvoir scanner le code-barres d'un produit avec l'appareil photo de mon smartphone
* **Afin d'** accéder immédiatement à sa fiche d'analyse nutritionnelle sans avoir à taper son nom.

---

## 2. Critères d'acceptation

### Scénario 1 : Scan réussi d'un produit existant
* **Étant donné que** je suis sur l'écran d'accueil de l'application et que j'autorise l'accès à la caméra
* **Quand** je place le code-barres d'un article dans la zone de visée de l'appareil photo
* **Alors** l'application vibre/émet un signal sonore léger pour confirmer la capture
* **Et** elle me redirige en moins de 3 secondes vers la fiche synthétique du produit.

### Scénario 2 : Gestion d'un code-barres mal lisible ou inconnu
* **Étant donné que** l'application détecte un code-barres mais qu'il n'est pas répertorié dans la base Open Food Facts
* **Quand** le traitement du scan échoue
* **Alors** l'interface affiche un message d'erreur clair et fluide ("Produit non trouvé")
* **Et** elle me propose un mécanisme simple pour signaler la donnée manquante ou saisir le nom manuellement.

### Scénario 3 : Absence de réseau en magasin (Mode dégradé)
* **Étant donné que** le réseau internet (4G/5G) est instable ou coupé dans le supermarché
* **Quand** je tente de scanner un produit
* **Alors** l'application affiche une notification m'invitant à réessayer
* **Et** elle enregistre l'action dans mon historique des scans (marqué "en attente") pour que je puisse le consulter dès le retour du réseau.

---

## 3. Règles de gestion & Contraintes techniques

* **Performance** : L'ouverture de la caméra et la détection du code-barres doivent être fluides et instantanées pour respecter la contrainte de temps de l'utilisateur.
* **RGPD & Sécurité** : Le flux vidéo de la caméra est traité localement sur le smartphone. Aucune image ou vidéo de l'utilisateur n'est envoyée ou stockée sur les serveurs de NutriScope.
* **Évolution future (Post-MVP)** : Le code doit être conçu de manière à pouvoir intégrer facilement un module complémentaire de type classifieur d'images (reconnaissance du produit directement par sa forme/pack si le code-barres est arraché).
