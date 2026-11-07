# User Story : Recommandation et proposition d'alternatives plus saines

**Épic de rattachement :** MVP - Moteur de recommandation

## 1. Description
* **En tant que** parent pressé faisant ses courses en magasin
* **Je souhaite** que l'application me propose 2 ou 3 alternatives plus saines au produit que je viens de scanner
* **Afin de** pouvoir faire un meilleur choix alimentaire facilement et rapidement sans avoir à chercher d'autres produits par moi-même.

## 2. Critères d'acceptation

### Scénario 1 : Affichage d'alternatives disponibles et plus saines
* **Étant donné** que je consulte la fiche d'un produit ayant un Nutri-Score défavorable (ex: Nutri-Score D ou E)
* **Quand** le moteur de recommandation calcule les résultats
* **Alors** l'application affiche une liste restreinte de **2 ou 3 alternatives maximum**
* **Et** ces produits doivent être plus sains selon des règles explicites (ex: Nutri-Score A ou B, moins de sucres saturés)
* **Et** ils doivent être cohérents avec le produit initial (ex: proposer une autre marque de biscuits chocolatés, pas un légume frais).

### Scénario 2 : Transparence et pédagogie de la recommandation
* **Étant donné** que des alternatives me sont présentées à l'écran
* **Quand** je regarde la liste des recommandations
* **Alors** l'application doit me permettre de **comprendre les raisons de la recommandation** grâce à des critères transparents et affichés (ex: mention "70% de sucre en moins", "Meilleur Nutri-Score").

### Scénario 3 : Prise en compte des préférences simples (Hors profil médical)
* **Étant donné** que j'ai configuré des préférences non médicales simples dans l'application (ex: végétarien, bio, ou sans alcool)
* **Quand** le système génère les alternatives plus saines
* **Alors** les produits proposés doivent **strictement respecter ces filtres** si la donnée existe dans la base *Open Food Facts*.

### Scénario 4 : Absence de données ou produit déjà optimal (Scénario alternatif)
* **Étant donné** que le produit scanné est déjà le mieux noté de sa catégorie (ex: Nutri-Score A) ou qu'aucune alternative réaliste n'est disponible
* **Quand** la fiche produit s'affiche
* **Alors** l'application n'affiche pas de bloc de recommandation vide
* **Et** elle affiche un message bienveillant (ex: "Ce produit fait déjà partie des meilleurs choix de sa catégorie !").

## 3. Règles de gestion & Contraintes strictes
* **Refus du médical :** Les recommandations ne doivent s'appuyer sur aucun profil médical, historique de santé ou pathologie (interdiction de recommander un produit "pour le diabète" ou "bon pour le cœur").
* **Éthique et neutralité :** Les alternatives doivent être basées uniquement sur des règles nutritionnelles objectives. Le classement ne doit pas être biaisé par des critères publicitaires ou des partenariats commerciaux masqués.
* **Performance :** Le calcul et l'affichage des alternatives doivent être intégrés dans le temps de réponse standard de **moins de 3 secondes**.
