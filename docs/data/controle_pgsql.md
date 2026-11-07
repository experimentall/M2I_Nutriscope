# Rapport de Contrôle Qualité

## comptage_par_rayon

| rayon | nb_produits | part_pourcentage |
| --- | --- | --- |
| Sugary snacks | 101934 | 30.49 |
| Fish Meat Eggs | 82171 | 24.58 |
| Milk and dairy products | 56237 | 16.82 |
| Cereals and potatoes | 51303 | 15.35 |
| Beverages | 42678 | 12.77 |

## completude

| rayon | pct_nutriscore | pct_7_nutriments | pct_categories |
| --- | --- | --- | --- |
| Beverages | 75.89 | 84.84 | 100.00 |
| Cereals and potatoes | 89.64 | 92.95 | 100.00 |
| Fish Meat Eggs | 94.38 | 94.67 | 100.00 |
| Milk and dairy products | 94.45 | 95.02 | 100.00 |
| Sugary snacks | 89.97 | 92.24 | 100.00 |

## doublons

| indicateur | valeur |
| --- | --- |
| couples_nom_marque_repetes | 21264 |
| codes_en_double | 0 |

## bornes_et_coherences

| anomalie | nb_lignes |
| --- | --- |
| satures_superieur_lipides | 158 |
| sucres_superieur_glucides | 184 |
| energie_hors_0_900 | 12 |
| nutriment_hors_0_100 | 0 |
| sel_different_sodium_x2_5 | 619 |
| energie_nulle_avec_macronutriments | 0 |

## distribution_nutriscore

| grade | nb_produits | part_pourcentage | score_moyen_energie |
| --- | --- | --- | --- |
| a | 35994 | 10.77 | 204.5 |
| b | 28189 | 8.43 | 150.1 |
| c | 52821 | 15.80 | 180.9 |
| d | 84470 | 25.27 | 281.4 |
| e | 99283 | 29.70 | 388.5 |
| not-applicable | 2678 | 0.80 | 257.9 |
| unknown | 30888 | 9.24 | 243.7 |

