# Rapport de Synthèse : Analyse Exploratoire des Données NutriScope

## Contexte Général

### Descriptif du Projet
Le projet NutriScope vise à analyser la composition nutritionnelle et à décrypter la structure du score et des grades de calcul du Nutri-Score. 

### Périmètre et Échantillon
L'étude est menée sur un échantillon extrait de la base globale Open Food Facts, restreint aux produits vendus en France. L'analyse porte spécifiquement sur les variables nutritionnelles de référence rapportées à une portion de 100 grammes (ou 100 ml).

### Rappel du Nettoyage Initial (TP 9)
Le jeu de données d'entrée a subi une phase de nettoyage.  
Les filtres appliqués sont les suivants :
* **Filtrage des lignes exploitables** : Exclusion des lignes présentant des doublons de codes-barres.
* **Contrôle des valeurs physiques** : Nettoyage et suppression des valeurs hors bornes, forçant les macronutriments à s'inscrire strictement dans l'intervalle possible de 0g, 100g.
* **Validation de la cohérence énergétique** : Suppression des anomalies de déclaration d'énergie jugées impossibles (ex: valeurs d'énergie supérieures au seuil maximal de 900 kcal/100g).
* **Restriction au périmètre métier** : Exclusion des fiches produits n'ayant aucun rayon d'appartenance connu.

## Messages Clés de l'Analyse Exploratoire

### 1. Profiling Univarié & Asymétrie des Nutriments
* **Message** : Les moyennes des nutriments critiques (sucres et sel) sont faussées par une asymétrie positive. La moyenne n'est pas représentative du produit.
* **Chiffres** : Le sucre affiche une moyenne de 12,94 g pour une médiane de seulement 3,0 g (asymétrie de +1,89). Le sel présente un profil plus extrême avec une moyenne de 1,07 g et une médiane à 0,5 g (asymétrie de +11,13), écrasé par un aplatissement (kurtosis) de 240,78 généré par des valeurs maximales à 77,5 g.

### 2. Qualité Nutritionnelle & Structuration par Rayon
* **Message** : Le rayon (pnns_group_1) influence le profil nutritionnel global et la note finale.
* **Chiffres** : Le coefficient V de Cramér de 0,34 entre le rayon et le grade Nutri-Score prouve une forte association. La normalisation par ligne révèle que le rayon *Fruits and vegetables* est dominé par la catégorie saine (50,3 % de 'A', 6,7 % de 'E'), tandis que le rayon *Sugary snacks* présente une trajectoire critique (0,9 % de 'A' contre 66,1 % de 'E').

### 3. Fiabilité et Complétude de la Base
* **Message** : Le taux de remplissage et la fiabilité des fiches varient entre les catégories de produits, créant un risque de biais d'analyse.
* **Chiffres** : Les sept nutriments requis sont simultanément renseignés (taux de fiches complètes) à hauteur de 74,8 % pour le rayon *Sugary snacks*, mais s'effondrent à seulement 14,6 % au sein du rayon des boissons alcoolisées (*Alcoholic beverages*).

### 4. Les Véritables Moteurs du Nutri-Score
* **Message** : La dégradation de la note du Nutri-Score est principalement régie par les acides gras saturés et l'apport calorique.
* **Chiffres** : Les corrélations de rang de Spearman avec le score numérique montrent que les acides gras saturés (0,54) et l'énergie (0,52) sont les facteurs les plus influents au niveau global. Les protéines, en revanche, n'affichent aucune liaison linéaire globale (0,05).

### 5. Paradoxe de Simpson au Sein des Produits Laitiers
* **Message** : L'effet d'un nutriment peut s'inverser totalement à l'échelle d'un rayon, rendant l'analyse aveugle aux réalités métiers.
* **Chiffres** : Globalement, la quantité de sucre est positivement corrélée au score Nutri-Score (0,39 : dégradation de la note). Pourtant, au sein du rayon *Milk and dairy products*, cette corrélation devient négative (-0,30). Les fromages sont très gras et très salés (médiane du score à 14,0) mais ne contiennent pas de sucre, tandis que les yaourts sont sucrés mais globalement mieux notés (médiane du score à 4,0), provoquant une inversion de tendance.

### 6. Colinéarité Parfaite Sel/Sodium
* **Message** : La matrice de corrélation révèle des variables parfaitement redondantes apportant une information strictement identique.
* **Chiffres** : Le coefficient de Spearman entre `salt_100g` et `sodium_100g` est égal à 0,99. Cette colinéarité parfaite s'explique par la simple application d'un coefficient multiplicateur (Sel = 2,5 x Sodium).

### 7. Facteurs de Biais sur le Coefficient de Pearson
* **Message** : Les coefficients de Pearson sont perturbés par les distributions à longue traîne ou contenant des sous-groupes extrêmes.
* **Chiffres** : Pour la relation lipides / score, le coefficient de Pearson n'est que de 0,30 tandis que le coefficient de Spearman atteint 0,47. Les 60 huiles du dataset (100 g de lipides pour un score de 2) brisent l'alignement linéaire (Pearson baisse) sans pour autant perturber la monotonie des rangs (Spearman reste élevé).

### 8. Erreurs de Déclaration de l'Énergie
* **Message** : L'examen des écarts par rapport aux formules théoriques révèle que le signal de l'énergie déclarée est pollué par erreurs de saisie humaine.
* **Chiffres** : des produits de la base affichent un écart supérieur à 150 kcal entre la valeur énergétique déclarée sur l'étiquette et la valeur calculée par la formule d'Atwater (9 x Lipides + 4 x Glucides + 4 x Protéines + 2 x Fibres).

---

## Registre des Hypothèses Exploratoires

| Hypothèse | Méthode | Résultat (Chiffres & Statut) | Décision & Action |
| :--- | :--- | :--- | :--- |
| **H1** : Les produits notés A contiennent moins de sucres que ceux notés E dans tous les rayons. | `comparer_deux_groupes` stratifié par `pnns_groups_1` entre les grades 'a' et 'e' sur la variable `sugars_100g`. | **RÉFORMULÉE**. Vrai dans 5 rayons sur 9 (ex: *Beverages*). Faux ou inversé dans 4 rayons (ex: *Salty snacks*, les biscuits salés apéritifs 'E' contenant moins de sucre que les 'A' aux fruits). | **Action** : Reformuler en : "Le sucre discrimine fortement les grades A et E uniquement dans les rayons sucrés et de boissons". Conserver la stratification par rayon pour l'apprentissage. |
| **H2** : Le rayon des en-cas sucrés (*Sugary snacks*) est plus calorique que le rayon des boissons (*Beverages*). | `comparer_deux_groupes` global sur l'énergie (`energy-kcal_100g`) entre les deux rayons. | **VALIDÉE**. Médiane *Sugary snacks* = 421 kcal, Médiane *Beverages* = 37 kcal. Différence de +384 kcal. | **Action** : Feature retenue. Cette différence d'échelle confirme l'obligation de standardiser l'énergie ou d'isoler le rayon des boissons. |
| **H3** : Les produits notés A contiennent moins de sel que ceux notés E dans tous les rayons. | `comparer_deux_groupes` stratifié par `pnns_groups_1` entre les grades 'a' et 'e' sur la variable `salt_100g`. | **REJETÉE**. Faux dans la filière *Salty snacks* et *Fat and sauces* où le sel n'est pas le moteur principal de dégradation par rapport aux acides gras saturés. | **Action** : Abandonner l'hypothèse d'une corrélation du sel. Créer une règle de pénalité sectorielle spécifique au sel uniquement pour les produits céréaliers et les plats composés. |
| **H4** : Les produits ultra-transformés (NOVA 4) contiennent plus de sucre que les produits peu transformés (NOVA 1, 2). | `comparer_deux_groupes` global sur `sugars_100g` entre les groupes `nova_group` == 4 et `nova_group.isin([1, 2])`. | **VALIDÉE**. Différence médiane de +12.5g en faveur du groupe NOVA 4. | **Action** : Conserver la classification NOVA comme indicateur indirect de charge en sucre. Utile pour le feature engineering. |

---

## 🛠️ Décisions d'Ingénierie par Travaux Pratiques (TP)

### Décisions pour le Nettoyage (`src/cleaning.py`)
1. **Drapeau `boisson_sel_incoherent`** : Détecter et exclure de l'échantillon d'apprentissage tout produit appartenant au rayon des boissons (*Beverages*) dont la teneur en sel dépasse 2 g pour 100 g (valeur isolée par l'analyse des extrêmes sur une eau de table erronée).
2. **Drapeau `viande_sel_aberrant`** : Filtrer et exclure du rayon *Fish Meat Eggs* les fiches présentant des taux de sel supérieurs à 15 g pour 100 g (le maximum théorique des charcuteries très sèches de type magret ou saucisson se situant autour de 8-10 g).
3. **Validation Atwater** : Automatiser le calcul de l'énergie théorique et rejeter systématiquement au nettoyage les fiches présentant une divergence absolue supérieure à 150 kcal par rapport à la déclaration de l'étiquette.

### Décisions par le `notebooks/eda_reference.ipynb`

**Rappel :**  
**V de Cramér :** Résume la liaison en un nombre entre 0 et 1  
**MAD :** (Median Absolute Deviation) ; dispersion robuste ; l'équivalent médian de l'écart-type  
**paradoxe de Simpson :** Une tendance observée globalement s'inverse quand on l'observe séparément dans chaque sous-groupe  
**ACP :** Transforme des variables numériques corrélées en composantes principales  
**Pearson :** Mesure une relation linéaire ; comme la moyenne, sensible aux extrêmes  
**Spearman :** Mesure une relation monotone, pas forcément en ligne droite ; robuste aux extrêmes et invariant à toute transformation croissante  
**zscore_robuste :** Indicateur qui sert à mesurer un outlier dans un jeu de données