
---
### Crédits
Données issues de la base de données ouverte [Open Food Facts][https://openfoodfacts.org](https://openfoodfacts.org).  
Ces données sont publiées sous la licence [Open Database License (ODbL)][https://opendatacommons.org](https://opendatacommons.org).  
Données : © Open Food Facts contributors — ODbL.
    
**Généré le :** 07/11/2026 à 12:51

### Volumetrie
- **Avant:** 386465 lignes, 34 colonnes
- **Après:** 334323 lignes, 51 colonnes
    
### Compte rendu du nettoyage

**Règle:** normaliser_unites  
**Avant:** 386465 lignes  
**Après:** 386465 lignes  
**Modifiée(s):** 30221 lignes(s)  
**Détails:**  
energy_kcal_100g_manquant_calcul_derivees: 158  
energy_kcal_100g_hors_borne_recalculees: 28568  
salt_100g_manquant_calcul_derivees: 0  
sodium_100g_manquant_calcul_derivees: 0  
sodium_100g_incoherent_recalculees: 1593
        

**Règle:** borner_nutriments  
**Avant:** 386465 lignes  
**Après:** 386465 lignes  
**Modifiée(s):** 648 lignes(s)  
**Détails:**  
fat_100g_hors_bornes: 11  
saturated-fat_100g_hors_bornes: 8  
carbohydrates_100g_hors_bornes: 28  
sugars_100g_hors_bornes: 22  
proteins_100g_hors_bornes: 11  
salt_100g_hors_bornes: 14  
fruits-vegetables-legumes_100g_hors_bornes: 252  
sugars_incoherent_glucides: 236  
saturated_incoherent_fat: 93
        

**Règle:** corriger_energie  
**Avant:** 386465 lignes  
**Après:** 386465 lignes  
**Modifiée(s):** 320414 lignes(s)  
**Détails:**  
energy_kcal_100g_nulles_recalculees: 163  
energy_kcal_100g_plus_900_recalculees: 35  
energy_kcal_100g_plus_900_invalidees: 9  
incoherentes_energy-kcal_100g_recalculees: 1058
        

**Règle:** dedupliquer_codes  
**Avant:** 386465 lignes  
**Après:** 386455 lignes  
**Modifiée(s):** 10 lignes(s)  
**Détails:**  
sans_code: 0  
doublons_supprimes: 10
        

**Règle:** traiter_categories_vides  
**Avant:** 386455 lignes  
**Après:** 386455 lignes  
**Modifiée(s):** 0 lignes(s)  
**Détails:**  
rayon_manquant_unknown: 0  
drapeau_categorie_vide_ajoute: 0  
inclassables_supprimes: 0
        

**Règle:** normaliser_textes  
**Avant:** 386455 lignes  
**Après:** 386455 lignes  
**Modifiée(s):** 374328 lignes(s)  
**Détails:**  
grades_unknown_nettoyes: 0  
noms_vides_nettoyes: 0  
marques_harmonisees: 24805
        

**Règle:** typer_colonnes  
**Avant:** 386455 lignes  
**Après:** 386455 lignes  
**Modifiée(s):** 386455 lignes(s)  
**Détails:**  
statut: le DataFrame à été modifié
        

**Règle:** strategie_manquants  
**Avant:** 386455 lignes  
**Après:** 334323 lignes  
**Modifiée(s):** 52113 lignes(s)  
**Détails:**  
colonnes_analysees: 24  
colonnes_traitees: 15  
colonnes_supprimees: 1  
drapeaux_crees: 15  
lignes_nutriments_cles_supprimees: 52113  
lignes_completeness_inf_025_supprimees: 19
        