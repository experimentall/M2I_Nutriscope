# Modèle Économique et Analyse Stratégique : NutriScope

## 1. Business Model Canvas (BMC)

| Bloc Canvas | Contenu NutriScope |
| :--- | :--- |
| **Segments de clientèle** | **Consommateurs attentifs à la nutrition** ; **familles** ; à terme, **distributeurs (B2B)** |
| **Proposition de valeur** | **Score expliqué en langage clair**, **substitution « propose mieux »**, **assistant conversationnel** |
| **Canaux** | **Application mobile**, **magasins partenaires** |
| **Relation client** | **Self-service + assistant** ; **communauté contributive** |
| **Flux de revenus** | **Freemium (gratuit + premium)**, **API B2B pour distributeurs** |
| **Ressources clés** | **Base Open Food Facts (ODbL)**, **modèles de Machine Learning (ML)**, **équipe** |
| **Activités clés** | **Qualité des données**, **entraînement/évaluation des modèles**, **développement produit** |
| **Partenaires clés** | **Open Food Facts (crédit obligatoire)**, **hébergeur cloud** |
| **Structure de coûts** | **Infrastructure cloud**, **salaires**, **acquisition d'utilisateurs** |

---

## 2. Analyse des 5 Forces de Porter

* **Rivalité concurrentielle** : Marché très saturé et déjà dominé par des géants installés (**Yuka**, **Open Food Facts**, **ScanUp**).
* **Nouveaux entrants** : Barrière à l'entrée faible car la base est ouverte et une application de scan se clone rapidement.
* **Substituts** : Concurrence indirecte de l'**étiquetage Nutri-Score direct en rayon** ou du suivi humain par un **diététicien**.
* **Pouvoir des fournisseurs** : Dépendance stratégique et technologique forte envers **Open Food Facts** pour l'approvisionnement des données.
* **Pouvoir des acheteurs** : Pouvoir très fort des clients induit par un **modèle freemium** et un **coût de changement nul**.

---

## 3. Analyse des Vulnérabilités et Solutions IA

### Bloc A : Partenaires clés / Ressources clés (Dépendance aux données brutes d'Open Food Facts)
* **La fragilité** : NutriScope n'a pas de barrière défensive sur sa donnée de base. N'importe quel concurrent peut télécharger la même base ODbL. De plus, si la base communautaire contient des erreurs ou des fiches incomplètes, l'application perd toute sa fiabilité.
* **L'impact de l'IA** : L'IA doit être utilisée pour **nettoyer, enrichir et breveter la donnée**. Des modèles de *Computer Vision* et de *NLP* peuvent analyser instantanément les photos d'étiquettes envoyées par les utilisateurs pour corriger automatiquement les erreurs de la base publique ou estimer/prédire par recoupement les valeurs nutritionnelles manquantes ou incertaines. Cela transforme une ressource publique en une **base de données enrichie propriétaire à haute valeur ajoutée**.

### Bloc B : Relation client / Proposition de valeur (Rétention face à un coût de changement nul)
* **La fragilité** : Scanner un produit est devenu une commodité. Si NutriScope se contente d'afficher une note et une alternative textuelle, l'utilisateur repartira chez Yuka à la moindre frustration, car changer d'application ne lui coûte rien.
* **L'impact de l'IA** : L'**assistant conversationnel (LLM)** doit devenir un **hub d'hyper-personnalisation**. Au lieu d'un simple outil de diagnostic, l'IA crée une barrière à la sortie en agissant comme un coach nutritionnel qui mémorise les objectifs du foyer, les allergies de l'enfant ou les intolérances. Elle peut expliquer de manière fluide pourquoi un ingrédient est déconseillé et générer des recettes ou des listes de courses alternatives sur-mesure. Cette expérience sur-mesure crée un **coût psychologique au changement** très fort pour l'utilisateur.
