# ADR-001 : Choix de LightGBM Tuned comme modèle de classification pour le Nutri-Score

## Contexte

L'objectif est de déployer un modèle de classification capable de prédire fidèlement la note Nutri-Score (`nutriscore_grade`) des produits alimentaires à partir de leurs caractéristiques nutritionnelles. Le volume de données nécessite une solution industrialisable, capable d'absorber des mises à jour régulières. Les contraintes du projet imposent un arbitrage rigoureux entre la performance globale (F1-score macro), l'exactitude brute (Accuracy), la rapidité d'inférence par produit pour les API temps réel (latence), et l'empreinte de stockage sur le serveur (taille du modèle).

## Options considérées

Les métriques ci-dessous proviennent des phases de validation croisée (5 plis) et d'évaluation sur le jeu de test contenant **5 965 produits**. La latence correspond au temps de prédiction total divisé par 5 965. La taille a été mesurée après sérialisation via `joblib.dump` et application de `Path.stat().st_size`.

| Critères | Option 1 : HistGradientBoosting (Baseline) | Option 2 : XGBoost Tuned (Optuna) | Option 3 : LightGBM Tuned (Optuna) |
| :--- | :--- | :--- | :--- |
| **Performance (F1-Score Macro)** | 0,8909 (+/- 0,0050) | 0,8975 (+/- 0,0064) | **0,8992 (+/- 0,0073)** |
| **Performance (Accuracy)** | 90,87 % | 91,40 % | **91,51 %** |
| **Latence (par produit)** | **0,000008 s** (0,047s / 5 965) | 0,000011 s (0,068s / 5 965) | 0,000024 s (0,143s / 5 965) |
| **Taille (sur disque)** | ~1,2 Mo | ~2,8 Mo | **~750 Ko** |
| **Explicabilité** | Moyenne (Feature Importances globales) | Moyenne (Feature Importances globales) | Moyenne (Feature Importances globales) |
| **Maintenance** | Faible (Scikit-Learn natif) | Moyenne (Dépendance externe XGBoost) | Moyenne (Dépendance externe LightGBM) |
| **Coût de réentraînement** | Faible (Ajustement : 1,875 s) | Élevé (Ajustement : 7,298 s) | Faible (Ajustement : 2,392 s) |

## Décision

Nous retenons le modèle LightGBM Tuned pour l'attribution des notes Nutri-Score.

## Conséquences

- **Avantages permanents :** L'option choisie maximise l'exactitude globale avec une **Accuracy de 91,51 %** et offre la meilleure représentativité des classes minoritaires (**F1 Macro de 0,8992**). De plus, son empreinte mémoire est la plus faible de toutes les architectures de Gradient Boosting évaluées (**~750 Ko sur disque**), optimisant le stockage au sein de l'image Docker de production. Le coût d'ajustement reste très maîtrisé (**2,392 s**) pour des réentraînements automatisés fréquents.
- **Inconvénients et sacrifices :** Nous sacrifions une légère fraction de vitesse d'inférence, la latence par produit s'élevant à **0,000024 s** contre 0,000008 s pour la baseline Scikit-Learn. Cela reste néanmoins largement en deçà du seuil critique toléré pour nos API (1 ms). L'introduction de la bibliothèque `lightgbm` ajoute également une dépendance externe à maintenir dans l'environnement virtuel du projet.

## Ce qui déclencherait une révision

La décision sera réévaluée si l'un des événements suivants survient :
1. Une dégradation de la performance globale constatée en production où l'**Accuracy Équilibrée descend en dessous de 85 %** sur un échantillon glissant de 10 000 nouveaux produits étiquetés.
2. Une modification des exigences de l'infrastructure d'accueil imposant une latence d'inférence par produit strictement inférieure à **0,000010 s**, rendant obligatoire le passage à *HistGradientBoosting*.
3. Une évolution réglementaire du Nutri-Score nécessitant une explicabilité stricte et auditable des décisions au niveau local (Shapley values insuffisantes), ce qui forcerait un retour à une *Régression Logistique* malgré sa faible exactitude brute de 80,28 %.
