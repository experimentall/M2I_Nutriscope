# Rapport de Contrôle Qualité

## comptage_par_rayon

| rayon | nb_produits | part_pourcentage |
| --- | --- | --- |
| fish-meat-eggs | 82171 | 24.58 |
| milk-and-dairy-products | 56237 | 16.82 |
| sugary-snacks | 101934 | 30.49 |
| cereals-and-potatoes | 51303 | 15.35 |
| beverages | 42678 | 12.77 |

## completude

| rayon | pct_nutriscore | pct_7_nutriments | pct_categories |
| --- | --- | --- | --- |
| fish-meat-eggs | 94.38 | 94.67 | 100.0 |
| sugary-snacks | 89.97 | 92.24 | 100.0 |
| cereals-and-potatoes | 89.64 | 92.95 | 100.0 |
| milk-and-dairy-products | 94.45 | 95.02 | 100.0 |
| beverages | 75.89 | 84.84 | 100.0 |

## doublons

| indicateur | valeur |
| --- | --- |
| codes_en_double | 0 |
| couples_nom_marque_repetes | 21264 |

## bornes_et_coherences

| anomalie | nb_lignes |
| --- | --- |
| nutriment_hors_0_100 | 0 |
| energie_hors_0_900 | 12 |
| sucres_superieur_glucides | 184 |
| satures_superieur_lipides | 158 |
| sel_different_sodium_x2_5 | 607 |
| energie_nulle_avec_macronutriments | 0 |

## distribution_nutriscore

| grade | nb_produits | part_pourcentage | score_moyen_energie |
| --- | --- | --- | --- |
| b | 28189 | 8.43 | 150.0759934064187 |
| d | 84470 | 25.27 | 281.3915104749541 |
| not-applicable | 2678 | 0.8 | 257.9287306271862 |
| a | 35994 | 10.77 | 204.53671171773578 |
| unknown | 30888 | 9.24 | 243.73014937827895 |
| c | 52821 | 15.8 | 180.8803075888559 |
| e | 99283 | 29.7 | 388.5355126211989 |

