# Rapport de Contrôle Qualité

## comptage_par_rayon

| rayon | nb_produits | part_pourcentage |
| --- | --- | --- |
| milk-and-dairy-products | 56237 | 16.82 |
| fish-meat-eggs | 82171 | 24.58 |
| sugary-snacks | 101934 | 30.49 |
| cereals-and-potatoes | 51303 | 15.35 |
| beverages | 42678 | 12.77 |

## completude

| rayon | pct_nutriscore | pct_7_nutriments | pct_categories |
| --- | --- | --- | --- |
| fish-meat-eggs | 0.0 | 94.67 | 100.0 |
| milk-and-dairy-products | 0.0 | 95.02 | 100.0 |
| sugary-snacks | 0.0 | 92.24 | 100.0 |
| cereals-and-potatoes | 0.0 | 92.95 | 100.0 |
| beverages | 0.0 | 84.84 | 100.0 |

## doublons

| indicateur | valeur |
| --- | --- |
| codes_en_double | 0 |
| couples_nom_marque_repetes | 21264 |

## bornes_et_coherences

| anomalie | nb_lignes |
| --- | --- |
| nutriment_hors_0_100 | 0 |
| energie_hors_0_900 | 11 |
| sucres_superieur_glucides | 184 |
| satures_superieur_lipides | 158 |
| sel_different_sodium_x2_5 | 607 |
| energie_nulle_avec_macronutriments | 0 |

## distribution_nutriscore

| grade | nb_produits | part_pourcentage | score_moyen_energie |
| --- | --- | --- | --- |
| C | 52821 | 15.8 | 180.8778454644358 |
| A | 35994 | 10.77 | 204.53417657920667 |
| unknown | 33566 | 10.04 | 245.14249430700548 |
| B | 28189 | 8.43 | 150.06716836024736 |
| E | 99283 | 29.7 | 388.53516009964545 |
| D | 84470 | 25.27 | 281.38386961704134 |

