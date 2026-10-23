# Note des limites : Ce que le modèle sait et ne sait pas faire

## 1. Ce que le modèle sait faire

Sur le jeu de test de référence (5 965 produits), le modèle LightGBM Tuned affiche une exactitude globale (**Accuracy**) de **91,51 %** et un **F1-Score Macro** de **0,8992**. 

Pour l'utilisateur final, la gravité des erreurs est extrêmement modérée, car la quasi-totalité des prédictions erronées se situent à proximité immédiate de la note réelle :
- **Prédictions correctes :** 5 453 produits (**91,42 %**).
- **Écart de 1 cran (ex: B prédit au lieu de A) :** 456 produits (**7,64 %**).
- **Écart de 2 crans et plus (Erreurs notables) :** Seulement 56 produits (**0,94 %**).

Le modèle est donc fiable à **99,06 %** pour restituer la note exacte ou une note adjacente à un cran près.

## 2. Les classes difficiles

La classe **D** est la plus difficile à appréhender pour le modèle. Elle obtient le rappel le plus faible des classes standards, car elle subit une double frontière d'incertitude :
- **Le constat :** Un nombre significatif de produits notés réellement **D** sont classés à tort en **C** ou en **E** par le modèle (visualisable sur la diagonale de la matrice de confusion).
- **L'erreur la plus aberrante :** Le modèle souffre de cas d'inversion totale sur des produits ultra-spécifiques ou mal catégorisés. Par exemple, les produits *« Craquant rose framboise noir »*, *« Préparation penne toscane épinards tomates »* et *« 2 boudins blancs au foie de canard »* sont enregistrés avec un Nutri-Score réel de **A** mais sont prédits avec une confiance absolue (~100 %) en classe **E**. Cela s'explique par un conflit direct entre des valeurs nutritionnelles brutes défavorables (sucre, sel ou acides gras saturés élevés) et des cas particuliers du barème officiel (comme des bonus liés aux légumes ou fruits non traçables par de simples ratios).

## 3. Les rayons mal couverts

L'analyse des performances par catégorie PNNS 1 (`pnns_groups_1`) met en évidence des disparités majeures :

- **Alcoholic beverages (Boissons alcoolisées) :** Performance critique avec un **F1-Score Macro de 0,3888**. Le modèle y est structurellement aveugle.
- **Sugary snacks (Snacks sucrés) :** Performance en retrait avec un **F1-Score Macro de 0,8071**. Ce rayon concentre une forte densité de produits proches des bascules de points (haute teneur en sucre et graisses saturées), entraînant de nombreuses hésitations entre les notes D et E.

*Note sur les effectifs :* Les rayons comme *Fish Meat Eggs* (F1: 0,9146) ou *Salty snacks* (F1: 0,9073) disposent d'un volume et d'une régularité de données qui permettent au gradient boosting de converger efficacement, contrairement aux boissons où les règles de calcul divergent.

## 4. Quand ne pas faire confiance au modèle (Règles métiers)

Pour sécuriser l'expérience utilisateur et éviter l'affichage de notes aberrantes, l'application doit intercepter les prédictions et s'abstenir d'afficher un résultat dès lors que l'une des règles automatiques suivantes est validée :

- **Règle 1 (Filtre Rayon Alcool) :** Si `pnns_groups_1 == "Alcoholic beverages"`, **bloquer l'affichage** de la prédiction. 
  * *Justification :* Le barème officiel du Nutri-Score applique aux boissons alcoolisées une grille spécifique basée sur le degré d'alcool, une variable totalement absente de nos features actuelles. Le modèle n'a pas les moyens d'avoir raison.
- **Règle 2 (Seuil d'hésitation sur les frontières) :** Si la différence de probabilité entre les deux classes les plus probables (`top1_prob - top2_prob`) est **inférieure à 0,15**, et que ce duo de tête appartient aux paires `{b, c}` ou `{d, e}`, **marquer la note comme "Incertaine"** ou forcer une vérification humaine.
  * *Justification :* Le modèle montre une forte indécision sur les frontières de notation pour les produits complexes (ex: *Original BBQ Sauce* prédit D au lieu de E, ou *Frosted mini wheats* proche de la bascule).
- **Règle 3 (Incohérence Atwater majeure) :** Si la variable dérivée calculée par le préprocesseur `energy_kcal_error` (Écart entre l'énergie calculée via les macronutriments et l'énergie déclarée) est **supérieure à 150 kcal** en valeur absolue, **rejeter le produit** et lever une alerte de qualité de donnée.
  * *Justification :* Le modèle s'appuie massivement sur la cohérence des nutriments (formule d'Atwater). Une erreur trop élevée signale un produit mal saisi dans la base Open Food Facts, ce qui fausse mathématiquement la prédiction du gradient boosting.
