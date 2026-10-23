# Analyse de la Qualité des Données — Base Open Food Facts

Dans le cadre d'un cas d'usage ciblant le **calcul automatisé du Nutri-Score** ou le **classement nutritionnel des aliments**, la nature collaborative et ouverte (*crowdsourcing*) de la base Open Food Facts expose les données à de fortes anomalies de saisie. 

Voici la sélection des **trois dimensions de qualité les plus critiques** menaçant ce cas d'usage, accompagnées des requêtes SQL permettant de mesurer leur impact.

---

## 1. La Cohérence

### Pourquoi c'est une menace
Il s'agit de la menace prioritaire. Si un contributeur inverse les grammes et les milligrammes, ou commet une faute de frappe, le profil nutritionnel global devient aberrant. Une somme de macronutriments supérieure à la masse totale du produit (100g) ou une valeur énergétique impossible fausse irrémédiablement le calcul du score de santé.

### Requête de mesure (SQL)
```sql
SELECT 
    COUNT(*) AS total_incoherents,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM produits), 2) AS part_incoherents
FROM produits
WHERE 
    (glucides_100g + proteines_100g + lipides_100g + sel_100g) > 100
    OR (energie_kj_100g IS NOT NULL AND energie_kj_100g > 3700); -- Seuil supérieur à de l'huile pure
```

---

## 2. La Validité

### Pourquoi c'est une menace
L'algorithme du Nutri-Score applique des règles et des barèmes spécifiques selon la nature du produit (les boissons, les fromages ou les matières grasses ont des grilles d'évaluation distinctes). Si la catégorie principale d'un produit est saisie en texte libre ou n'appartient pas à la taxonomie officielle d'Open Food Facts, l'application ne pourra pas déterminer la formule de calcul adéquate.

### Requête de mesure (SQL)
```sql
SELECT 
    COUNT(*) AS total_invalides,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM produits), 2) AS part_categories_invalides
FROM produits p
LEFT JOIN referentiel_categories r ON p.categorie_principale = r.id_categorie
WHERE r.id_categorie IS NULL AND p.categorie_principale IS NOT NULL;
```

---

## 3. La Complétude

### Pourquoi c'est une menace
Une fiche produit peut posséder un code-barres valide et une catégorie correcte, mais si des variables indispensables comme les acides gras saturés, le sucre, le sodium ou les fibres manquent à l'appel, l'exécution de l'algorithme est bloquée. Les fiches incomplètes rendent le produit inexploitable pour l'utilisateur final.

### Requête de mesure (SQL)
```sql
SELECT 
    COUNT(*) AS fiches_incompletes,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM produits), 2) AS part_incompletes
FROM produits
WHERE 
    categorie_principale IS NULL 
    OR energie_100g IS NULL 
    OR lipides_satures_100g IS NULL
    OR sucres_100g IS NULL
    OR proteines_100g IS NULL;
```
