# M2I_Nutriscope

**Installation:**  
Créer un fichier **.env** à la racine du projet.  
Copier le contenu de **.env.dist** dans **.env**  
Modifier les valeurs des variables d'environnement selon sa configuration locale

```bash
pip install -r requirements.txt
```

**Création du fichier CSV filtré**  
```bash
python -m src.filter_csv
```

**Chargement du schema de la database**  
```bash
python -m src.create_db
```

**Import en BDD**  
```bash
python -m src.load_db
```

**Requêtes de contôle PGSQL**  
```bash
python -m src.run_queries --con pgsql
```



**Lancement pipeline**
```bash
python -m src.pipeline
```

**Conversion parquet**
```bash
python -m src.convert_parquet
```

**Requêtes de contrôle .parquet**
```bash
python -m src.run_queries --con parquet
```

**Export features**
```bash
python -m src.export_features --input-dir ./data/parquet/produits --output-dir ./data/exports --force
```

**Génération notebooks/eda_reference.ipynb**
```bash
python -m jupyter nbconvert --to notebook --execute --inplace notebooks/eda_reference.ipynb
```

**Tests**
```bash
python -m pytest -q
python -m pytest -v tests/test_regles.py
python -m pytest -v -s tests/test_regles.py::test_dedupliquer_codes_garde_le_plus_complet
```

**Génération requirements.txt**
```bash
pipreqs ./src --force
```