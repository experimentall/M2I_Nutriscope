# Stratégie de Traitement des Données Manquantes — NutriScope

Ce document détaille les choix méthodologiques pour la gestion des données manquantes du projet OpenFoodFacts. L'objectif est de préparer les données pour le pipeline de Machine Learning en évitant toute fuite de données (*data leakage*).

---

## 1. Dictionnaire Complet des Stratégies (STRATEGIE_PAR_DEFAUT)

| Colonne | Usage dans NutriScope | Type de Manquant | Décision | Justification Métier / Technique |
| :--- | :--- | :--- | :--- | :--- |
| `product_name` | Affichage / Identification | NA | `garder + drapeau` | Identification essentielle, le manque est suspect. Le drapeau isole l'anomalie. |
| `brands` | Assistant / Affichage | NA, MAR | `garder + drapeau` | Lié à la notoriété de la marque ou au circuit de distribution. Impossible à deviner. |
| `quantity` | Affichage portion / Fiche | NA, MNAR | `garder + drapeau` | Souvent omis sur les produits en vrac ou les formats spécifiques. |
| `categories_tags` | Regroupement / Alignement | NA, MAR/MNAR | `garder + drapeau` | Règle métier : supprimé si `main_category` ET `categories_tags` sont manquants. |
| `main_category` | Classification produit | Substitution | `garder + drapeau` | Remplacé par `categories_tags` si disponible. |
| `labels_tags` | Filtres (Bio, Vegan...) | Élevé | `supprimer la colonne` | Taux de manquants trop critique (>90%), information inexploitable. |
| `stores` | Affichage cartographique | Élevé | `supprimer la colonne` | Information volatile et non requise pour le cœur du modèle prédictif. |
| `ingredients_text` | Assistant conversationnel | NA, MAR | `garder + drapeau` | Un texte d'ingrédients est unique. Aucune valeur statistique n'est plausible. |
| `allergens` | Sécurité / Alertes | NA, MNAR | `garder + drapeau` | L'absence peut signifier l'absence d'allergènes (Non Déclaré). |
| `additives_n` | Score / Classification | NA, MAR | `garder + drapeau` | Fortement corrélé au degré de transformation du produit. |
| `nova_group` | Feature catégorielle | MAR | `imputation statistique après split (méthode)` | *À imputer post-split par le mode.* Dépend fortement du rayon de l'aliment. |
| `nutriscore_score` | Cible du modèle | unknown -> NA | `garder` | Variable cible potentielle. Les valeurs `unknown` deviennent NA. On ne l'impute jamais. |
| `serving_size` | Affichage de la portion | MCAR-proche | `garder` | Feature dérivée textuelle. Syntaxe trop hétérogène (ex: 1 pot, 2 biscuits). |
| `energy-kcal_100g` | Feature nutritionnelle clé | MAR | `imputation statistique après split (méthode)` | *À imputer post-split par la médiane du rayon.* Valeur physique indispensable. |
| `energy_100g` | Feature nutritionnelle clé | Imputation métier | `garder` | Doublon potentiel avec kcal, sert aux calculs et vérifications. |
| `fat_100g` | Macronutriment | NA, MNAR | `garder + drapeau` | Absence sur certaines catégories (ex: boissons) ou omission volontaire. |
| `saturated-fat_100g`| Composante Nutri-Score | NA, MNAR | `garder + drapeau` | Donnée critique pour le calcul des points négatifs de la cible. |
| `carbohydrates_100g`| Macronutriment | NA, MNAR | `garder + drapeau` | Valeur nutritionnelle macro-économique essentielle. |
| `sugars_100g` | Composante Nutri-Score | NA, MAR | `garder` | Souvent lié aux déclarations obligatoires. |
| `fiber_100g` | Composante Nutri-Score | NA, MNAR | `garder + drapeau` | **Plus de 10% de manquants.** Non obligatoire dans certains pays. |
| `proteins_100g` | Composante Nutri-Score | NA, MNAR | `garder + drapeau` | Valeur nutritionnelle macro (points positifs). |
| `salt_100g` | Composante Nutri-Score | NA, MAR | `garder` | Imputation métier déterministe possible via la formule exacte avec le sodium. |
| `sodium_100g` | Feature nutritionnelle clé | Calcul métrologique | `garder` | Imputation métier déterministe possible via la formule exacte avec le sel. |
| `fruits-vegetables-legumes_100g` | Composante Nutri-Score | NA, MNAR | `garder + drapeau` | **Plus de 10% de manquants.** Très rarement renseigné textuellement. |

---

## 2. Point de Contrôle 3 : Justification des Variables > 10% de Manquants

Pour chaque colonne présentant un taux d'absence critique (> 10 %), voici l'analyse de son usage, la cause du manque et la modélisation mathématique retenue :

### `fiber_100g`
* **Usage dans NutriScope :** Calcul des composantes positives du Nutri-Score (bonification des fibres).
* **Pourquoi le manque ?** La déclaration des fibres sur l'étiquetage nutritionnel arrière n'est pas obligatoire selon les réglementations de plusieurs pays (notamment le règlement INCO européen, sauf si une allégation spécifique comme "Riche en fibres" est mise en avant). Il s'agit d'un manque de type **MNAR** (Missing Not At Random).
* **Décision :** `garder + drapeau`. Le manque est conservé intact dans la cellule d'origine. Une colonne booléenne `fiber_100g_manquant` est créée afin que le modèle de Machine Learning apprenne le comportement des produits sans déclaration de fibres.

### `fruits-vegetables-legumes_100g`
* **Usage dans NutriScope :** Composante majeure et bonification du score Nutri-Score (points N).
* **Pourquoi le manque ?** Cette information nécessite un calcul précis des matières premières de la part du fabricant. Elle apparaît très rarement de manière brute sur le packaging. C'est un cas pur de **MNAR**.
* **Décision :** `garder + drapeau`. La valeur brute ne subit aucune imputation statistique grossière à ce stade car un manquant est fortement assimilable à une valeur proche de `0` pour les produits ultra-transformés. Le drapeau portera l'information de non-déclaration.

### `labels_tags`
* **Usage dans NutriScope :** Moteur de filtres pour l'assistant ou l'application (recherche de produits certifiés Bio, Label Rouge, Sans Gluten).
* **Pourquoi le manque ?** La majorité des produits ne possèdent pas de labels officiels, ou l'information n'a pas été numérisée lors du scan de l'article. 
* **Décision :** `supprimer la colonne`. Le taux d'absence est si proche de 100 % que la colonne entière n'apporte aucun pouvoir prédictif global ou statistique stable pour le modèle cœur.

### `stores`
* **Usage dans NutriScope :** Affichage cartographique des points de vente pour l'utilisateur.
* **Pourquoi le manque ?** Information purement déclarative par les utilisateurs d'OpenFoodFacts, extrêmement volatile géographiquement et rarement complétée à la saisie.
* **Décision :** `supprimer la colonne`. Non requise pour le traitement algorithmique du Nutri-Score et trop parcellaire pour être exploitable.

---

## 3. Règles d'Intégrité Globales

1. **Cas « Produit sans aucun nutriment clé » :**
   Tout produit ne présentant *aucune* valeur pour les macronutriments principaux (`fat_100g`, `carbohydrates_100g`, `proteins_100g`, `energy_100g`) est considéré comme une coquille vide ou une erreur d'encodage. L'action appliquée est `supprimer la ligne`.
   
2. **Isolation stricte de l'Imputation Statistique :**
   Conformément aux exigences, les choix `mediane_rayon` et `mode` inscrits pour `energy-kcal_100g` et `nova_group` servent uniquement de déclaration d'intention. **Aucune imputation statistique n'est exécutée à cette étape de nettoyage de données**. Le calcul des médianes/modes s'effectuera exclusivement au sein du pipeline scikit-learn, **après le split Train/Test**, pour garantir l'absence totale de fuite de données (*Data Leakage*).
