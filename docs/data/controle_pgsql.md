# Rapport de Contrôle Qualité

## comptage_par_rayon

| rayon | nb_produits | part_pourcentage |
| --- | --- | --- |
| Sugary snacks | 101934 | 19.01 |
| Fish Meat Eggs | 82171 | 15.33 |
| Milk and dairy products | 56237 | 10.49 |
| unknown | 54996 | 10.26 |
| Cereals and potatoes | 51303 | 9.57 |
| Beverages | 42678 | 7.96 |
| Composite foods | 38239 | 7.13 |
| Fat and sauces | 35688 | 6.66 |
| Fruits and vegetables | 33504 | 6.25 |
| Salty snacks | 28582 | 5.33 |
| Alcoholic beverages | 8330 | 1.55 |
| Baby foods | 2526 | 0.47 |

## completude

| rayon | pct_nutriscore | pct_7_nutriments | pct_categories |
| --- | --- | --- | --- |
| Alcoholic beverages | 0.58 | 23.71 | 100.00 |
| Baby foods | 0.00 | 91.88 | 100.00 |
| Beverages | 75.89 | 84.84 | 100.00 |
| Cereals and potatoes | 89.64 | 92.95 | 100.00 |
| Composite foods | 94.78 | 96.49 | 100.00 |
| Fat and sauces | 87.27 | 93.26 | 100.00 |
| Fish Meat Eggs | 94.38 | 94.67 | 100.00 |
| Fruits and vegetables | 86.88 | 88.40 | 100.00 |
| Milk and dairy products | 94.45 | 95.02 | 100.00 |
| Salty snacks | 94.83 | 95.33 | 100.00 |
| Sugary snacks | 89.97 | 92.24 | 100.00 |
| unknown | 68.43 | 87.04 | 100.00 |

## doublons

| indicateur | valeur |
| --- | --- |
| couples_nom_marque_repetes | 34088 |
| codes_en_double | 0 |

## bornes_et_coherences

| anomalie | nb_lignes |
| --- | --- |
| satures_superieur_lipides | 304 |
| sucres_superieur_glucides | 256 |
| energie_hors_0_900 | 17 |
| nutriment_hors_0_100 | 0 |
| sel_different_sodium_x2_5 | 980 |
| energie_nulle_avec_macronutriments | 2 |

## distribution_nutriscore

| grade | nb_produits | part_pourcentage | score_moyen_energie |
| --- | --- | --- | --- |
| a | 62825 | 11.72 | 172.7 |
| b | 49497 | 9.23 | 232.4 |
| c | 95912 | 17.89 | 192.0 |
| d | 121920 | 22.74 | 291.5 |
| e | 131883 | 24.60 | 389.0 |
| not-applicable | 26364 | 4.92 | 203.7 |
| unknown | 47787 | 8.91 | 257.4 |

