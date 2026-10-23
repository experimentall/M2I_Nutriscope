# Analyse des Cas d'Usage IA pour NutriScope

## 1. Analyse des 5 cas d'usage à la grille des 6 questions

### Cas d'usage 1 : Prédiction de l'attrition (*Churn*) (Marketing / Ventes)
* **1. Problème** : L'équipe marketing et produit souffre d'un désabonnement des utilisateurs Premium. Cela coûte environ **15 000 €/mois** en perte de MRR (revenu mensuel récurrent) et fait grimper le coût d'acquisition.
* **2. Sponsor** : Le **Chief Marketing Officer (CMO)** / Responsable Rétention.
* **3. Données** : Historique d'utilisation de l'application (fréquence des scans, requêtes à l'assistant), logs de connexion, et historique de facturation Stripe. Données disponibles depuis le lancement, conformes RGPD via les CGU.
* **4. Faisabilité** : Un modèle statistique simple (Régression logistique ou XGBoost) basé sur la baisse de fréquence des scans sur 14 jours suffit largement.
* **5. Intégration** : La prédiction génère une alerte dans l'outil de marketing automation (ex: Braze ou HubSpot) pour déclencher une notification push ou un email d'engagement ciblé.
* **6. Mesure** : KPI : Réduction du taux de churn de **15%**. Seuil d'arrêt : Si le coût des campagnes de rétention dépasse le gain en MRR sauvé sur 3 mois.

### Cas d'usage 2 : Scoring de prospects B2B pour l'API (Marketing / Ventes)
* **1. Problème** : L'unique commercial B2B perd **15 heures par semaine** à qualifier manuellement des distributeurs, épiceries en ligne et applications tierces qui s'inscrivent pour tester l'API, sans savoir lesquels ont un vrai budget.
* **2. Sponsor** : Le **Head of Sales** / Directeur Commercial.
* **3. Données** : Données du CRM (HubSpot), logs d'appels à l'API d'essai, données d'enrichissement d'entreprises (Sirene, LinkedIn via Clearbit). Profondeur de 6 à 12 mois.
* **4. Faisabilité** : Approche hybride. Un système de règles de filtrage (taille d'entreprise, volume de requêtes tests) combiné à un scoring prédictif simple.
* **5. Intégration** : Le score (A, B, C, D) est poussé directement dans le CRM pour trier la liste des tâches quotidiennes du commercial.
* **6. Mesure** : KPI : Augmentation du taux de conversion des démos de **20%**. Seuil d'arrêt : Si le modèle donne un score "A" à des leads qui ne répondent jamais (taux d'erreur > 40%).

### Cas d'usage 3 : Détection d'anomalies et de fraudes sur l'API (Production / Finance)
* **1. Problème** : L'équipe technique fait face à du "scraping" sauvage (vol de données à grande échelle via des comptes d'essai ou des clés API compromises), causant une surcharge serveur estimée à **3 000 €/mois** d'infrastructure cloud inutile.
* **2. Sponsor** : Le **Chief Technology Officer (CTO)**.
* **3. Données** : Logs de requêtes API en temps réel (adresses IP, patterns de requêtes, jetons d'accès). Profondeur de 3 mois de logs.
* **4. Faisabilité** : Des règles de *rate-limiting* fixes ne suffisent pas face à des attaquants agiles. Un modèle d'apprentissage non supervisé (Isolation Forest) est nécessaire pour détecter les comportements de requêtes atypiques.
* **5. Intégration** : Intégration directe dans la gateway API (ex: Kong ou AWS API Gateway) pour bloquer ou imposer un Captcha au jeton suspect.
* **6. Mesure** : KPI : Diminution de **80%** des requêtes frauduleuses identifiées. Seuil d'arrêt : Si le taux de "Faux Positifs" (blocage de vrais clients B2B payants) dépasse **0,1%**.

### Cas d'usage 4 : Extraction de documents et validation des étiquettes (RH / Fonctions Support)
* **1. Problème** : L'équipe Support/Data passe **25 heures par semaine** à vérifier manuellement les photos d'ingrédients envoyées par les utilisateurs pour corriger la base Open Food Facts ou valider des signalements.
* **2. Sponsor** : Le **Responsable Qualité des Données** / Customer Success Manager.
* **3. Données** : Photos soumises par les utilisateurs, base de données ingrédients textuelle. Historique de milliers de tickets déjà résolus.
* **4. Faisabilité** : Un pipeline OCR (reconnaissance de texte) couplé à un petit LLM spécialisé pour mapper le texte extrait vers le dictionnaire officiel des ingrédients. Une simple approche statistique ne suffit pas en raison de la variété des polices et des langues.
* **5. Intégration** : Intégration dans le back-office de modération des données ; l'IA pré-remplit les champs et le modérateur n'a plus qu'à cliquer sur "Valider".
* **6. Mesure** : KPI : Temps de traitement d'un ticket divisé par **3**. Seuil d'arrêt : Si le taux d'erreur de transcription de l'IA nécessite plus de temps de correction qu'une saisie de zéro.

### Cas d'usage 5 : Assistant interne de conformité réglementaire (RAG) (RH / Fonctions Support)
* **1. Problème** : L'équipe produit et l'équipe juridique perdent de nombreuses heures à éplucher les évolutions des réglementations (Nutri-Score, additifs interdits par l'UE, règles d'affichage) pour valider la conformité des algorithmes de l'application.
* **2. Sponsor** : Le **Directeur Juridique (Legal Counsel)** / Product Owner.
* **3. Données** : Textes de loi du Journal Officiel de l'UE, directives de la Commission Européenne, documentation interne. Pas d'historique requis, mais besoin d'une fraîcheur absolue des textes.
* **4. Faisabilité** : Un système RAG (Retrieval-Augmented Generation) branché sur un LLM. L'approche par mots-clés statistiques ne suffit pas pour interpréter le jargon légal.
* **5. Intégration** : Un bot accessible sur le Slack de l'entreprise ou une interface web interne.
* **6. Mesure** : KPI : Réduction du temps de recherche réglementaire de **50%**. Seuil d'arrêt : Si l'IA produit une seule hallucination critique (affirmation erronée sur une interdiction légale) non détectée lors d'un test mensuel.

---

## 2. Matrice Valeur × Faisabilité

| Valeur \ Faisabilité | FAIBLE | ÉLEVÉE |
| :--- | :--- | :--- |
| **HAUTE** | **[Cas 4] Extraction étiquettes** <br> *(Forte valeur opérationnelle)* <br><br> **[Cas 5] RAG Réglementaire** <br> *(Gain de temps expert)* | **[Cas 1] Prédiction Churn** <br> *(ROI direct sur le MRR)* <br><br> **[Cas 3] Détection Fraude API** <br> *(Protection Infra / IP)* |
| **FAIBLE** | *Aucun cas d'usage identifié* | **[Cas 2] Scoring Prospects B2B** <br> *(Process simple, équipe restreinte)* |

---

## 3. Sélection des 3 cas d'usage prioritaires

1. **Priorité 1 : Prédiction de l'attrition (Churn) [Cas 1]**
   * *Justification* : Dans un modèle freemium où le coût de changement d'application est nul, retenir un utilisateur payant avant qu'il ne parte est le levier financier le plus rentable et le plus rapide à mettre en œuvre. Les données d'utilisation de l'application étant déjà centralisées, la faisabilité technique est immédiate avec un excellent ROI.

2. **Priorité 2 : Extraction de documents / Validation des étiquettes [Cas 4]**
   * *Justification* : Ce cas d'usage s'attaque directement au point faible identifié dans le BMC : la dépendance et la qualité des données d'Open Food Facts. En automatisant la vérification des étiquettes soumises par la communauté, NutriScope accélère la création de sa propre couche de données enrichies et fiabilisées à moindre coût humain.

3. **Priorité 3 : Détection de fraude et de scraping sur l'API [Cas 3]**
   * *Justification* : Dès lors que NutriScope ouvre son API B2B pour générer des revenus, sa base de données devient sa principale propriété intellectuelle et sa structure de coûts cloud devient sensible. Sécuriser l'API grâce à l'IA évite les pertes financières directes liées au vol de données et aux requêtes abusives des concurrents.