# Business Case & Analyse d'Opportunité — NutriScope (Projet Data/IA)

Ce document établit le cadrage macro-économique et l'analyse de risques pour le lancement du MVP de NutriScope, projeté sur une période de 3 ans.

---

## 1. Chiffrage de la Valeur des Briques (Formule : Volume × Gain × Taux de Succès)

Pour évaluer la valeur économique annuelle du projet, nous appliquons la formule de référence à chaque brique fonctionnelle du MVP. Les volumes reposent sur l'objectif métier des **30 000 utilisateurs actifs mensuels (MAU)** stabilisés à 12 mois, générant une hypothèse moyenne de **4 scans par utilisateur et par mois**, soit **1 440 000 scans par an** au total.

### 📊 Brique 1 : Prédiction et Explication synthétique du Nutri-Score
*Cette brique comble les fiches produits incomplètes d'Open Food Facts afin d'éviter la frustration de l'utilisateur.*
*   **Volume (Annuel)** : 1 440 000 scans totaux.
*   **Gain Unitaire (€)** : **0,15 €** (Équivalent au coût d'acquisition utilisateur sauvé grâce à l'évitement d'une fiche vide, qui provoquerait l'abandon de l'application).
*   **Taux de Succès Attendue** : **25 %** (Part estimée des fiches Open Food Facts initialement incomplètes, anciennes ou contradictoires qu'il faut corriger par prédiction).
*   **Calcul de la Valeur Annuelle** : 
    $$1\ 440\ 000 \times 0,15 \times 0,25 = \mathbf{54\ 000\ \text{€ / an}}$$

### 📈 Brique 2 : Proposition d'Alternatives plus saines (Substitution)
*Cette brique propose des produits de substitution réalistes et disponibles en magasin.*
*   **Volume (Annuel)** : 1 440 000 scans totaux, dont **40 %** concernent des produits mal notés, soit 576 000 requêtes de substitution potentielles par an.
*   **Gain Unitaire (€)** : **0,20 €** (Valeur moyenne du lead qualifié, monétisable à terme via les partenariats avec les marques ou distributeurs pour pousser leurs alternatives MDD saines).
*   **Taux de Succès Attendue** : **15 %** (Taux d'acceptation et de choix effectif de l'alternative par l'utilisateur en rayon).
*   **Calcul de la Valeur Annuelle** : 
    $$576\ 000 \times 0,20 \times 0,15 = \mathbf{17\ 280\ \text{€ / an}}$$

### 🔎 Brique 3 : Comparaison de deux ou trois produits
*Permet de comparer les critères (nutrition, prix si disponible, additifs) sur un seul écran.*
*   **Volume (Annuel)** : **144 000 comparaisons** par an (On estime que 10 % des sessions de scan mènent à une comparaison active en rayon).
*   **Gain Unitaire (€)** : **0,50 €** (Valeur perçue du gain de temps pour l'utilisateur, moteur principal de l'objectif de **40 % de réutilisation sous 30 jours**).
*   **Taux de Succès Attendue** : **85 %** (Part des comparaisons où les données du catalogue permettent un affichage transparent et sans conflit).
*   **Calcul de la Valeur Annuelle** : 
    $$144\ 000 \times 0,50 \times 0,85 = \mathbf{61\ 200\ \text{€ / an}}$$

### 💡 Brique 4 : Assistant conversationnel spécialisé encadré (RAG)
*Répond aux questions sur la qualité nutritionnelle sans vocabulaire trop technique.*
*   **Volume (Annuel)** : **288 000 requêtes** (On estime que 20 % des scans déclenchent une question de précision à l'assistant).
*   **Gain Unitaire (€)** : **0,25 €** (Économie en fidélisation, transformation de l'application en un "assistant réflexe" qui évite le recours à des sites concurrents trop techniques).
*   **Taux de Succès Attendue** : **90 %** (Taux de réponses jugées fiables, non médicales et n'entrant pas dans une dérive de modèle).
*   **Calcul de la Valeur Annuelle** : 
    $$288\ 000 \times 0,25 \times 0,90 = \mathbf{64\ 800\ \text{€ / an}}$$

---

## 2. Estimation des Coûts sur Trois Ans (Ordres de grandeur)

L'enveloppe budgétaire initiale étant plafonnée à **120 000 € pour le MVP**, l'allocation financière sur 3 ans doit anticiper l'industrialisation (Post-Levée de fonds).

### ✅ Build (Année 1 — Phase MVP) : 120 000 €
*   **Ingénierie & Design** : Rémunération de la petite équipe data/IA, du PO à mi-temps et de l'UX designer partagée.
*   **Mise en place technique** : Développement de l'API FastAPI, du classifieur d'images, de la base produits de départ et du pipeline RAG initial.

### 🛠️ Run (Réparti sur 3 ans) : 95 000 €
*   **Année 1** : 15 000 € (Hébergement cloud de départ, premiers tokens LLM pour 30 000 MAU sans engagement).
*   **Année 2** : 35 000 € (Montée en charge de l'infrastructure, maintenance corrective, coûts récurrents des requêtes de l'assistant conversationnel).
*   **Année 3** : 45 000 € (Gestion de l'infrastructure pour l'historique des scans à grande échelle et support utilisateur).

### 🔄 Change (Années 2 et 3) : 110 000 €
*   **Année 2** : 50 000 € (Mise en place d'une plateforme MLOps complète, intégration des fonctionnalités de personnalisation avancées et comptes utilisateurs).
*   **Année 3** : 60 000 € (Recrutements data suite à la levée de fonds, intégration des agents d'automatisation et des données environnementales).

---

## 3. Matrice et Gestion des Risques

### Liste des 6 Risques identifiés (Probabilité × Impact de 1 à 5)

1.  **Risque R1 : Crise Sanitaire / Réputationnelle (Allergies/Diabète)**
    *   *Description* : L'IA commet une erreur de recommandation dangereuse pour un profil sensible.
    *   *Cotation* : Probabilité 1 / Impact 5 (Score : **5** — Zone Rouge)
2.  **Risque R2 : Mauvaise qualité / Données incomplètes (Open Food Facts)**
    *   *Description* : Base de données inutilisable, fiches contradictoires bloquant la prédiction.
    *   *Cotation* : Probabilité 4 / Impact 3 (Score : **12** — **Zone Orange**)
3.  **Risque R3 : Dérapage du Calendrier (Livraison après la campagne nationale)**
    *   *Description* : Incapacité à livrer le MVP en 4 mois à cause de la complexité technique.
    *   *Cotation* : Probabilité 3 / Impact 4 (Score : **12** — **Zone Orange**)
4.  **Risque R4 : Explosion des coûts des modèles génératifs (LLM)**
    *   *Description* : Le coût des tokens de l'assistant conversationnel dépasse le budget de run.
    *   *Cotation* : Probabilité 3 / Impact 3 (Score : **9** — **Zone Orange**)
5.  **Risque R5 : Non-conformité Réglementaire (RGPD & AI Act)**
    *   *Description* : Sanctions pour collecte non autorisée de données de santé ou classification interdite.
    *   *Cotation* : Probabilité 2 / Impact 4 (Score : **8** — **Zone Orange**)
6.  **Risque R6 : Dérive de l'assistant conversationnel (Hallucinations)**
    *   *Description* : L'assistant répond à des questions médicales ou s'écarte du sujet de l'alimentation.
    *   *Cotation* : Probabilité 4 / Impact 2 (Score : **8** — **Zone Orange**)

### 📊 Positionnement dans la Matrice (Probabilité × Impact)

| Impact (Ordonnée) \ Probabilité (Abscisse) | Faible (1-2) | Moyenne (3) | Forte (4-5) |
| :--- | :--- | :--- | :--- |
| **Fort (4-5)** | **R1** : Crise Sanitaire (1, 5)<br>**R5** : Non-conformité RGPD/AI Act (2, 4) | **R3** : Dérapage Calendrier (3, 4) | |
| **Moyen (3)** | | **R4** : Explosion Coûts LLM (3, 3) | **R2** : Mauvaise Qualité Données (4, 3) |
| **Faible (1-2)** | | | **R6** : Dérive Assistant/Hallucinations (4, 2) |

*   **Zone Rouge (Score 15-25)** : Aucun risque dans cette zone, le risque R1 est bloqué par son impact mais sa probabilité reste très faible grâce aux garde-fous.
*   **Zone Orange (Score 5-12)** : R2, R3, R4, R5, R6 nécessitent un plan d'action.

### 🛠️ Plan de Mitigation (Zone Orange)

*   **Pour R2 (Données Open Food Facts imparfaites)** : Mettre en place un mécanisme de repli algorithmatique. Si les données obligatoires manquent, l'application affiche explicitement "Données insuffisantes pour prédire le score" et propose un bouton permettant à l'utilisateur de signaler l'erreur.
*   **Pour R3 (Dérapage du Calendrier)** : Geler strictement le périmètre du MVP. Supprimer toutes les fonctionnalités secondaires (comme les recommandations personnalisées ou l'historique des scans) pour se concentrer uniquement sur les 10 semaines de développement avant le passage au CA.
*   **Pour R4 (Coûts LLM)** : Remplacer l'usage de modèles génératifs commerciaux par un modèle open-source plus petit et spécialisé, combiné à un système de mise en cache (cache) des réponses pour éviter de recalculer les explications des 500 produits les plus scannés.
*   **Pour R5 (RGPD / AI Act)** : Refuser la création de comptes au lancement (Zéro collecte de données nominatives). Les préférences (ex: végétarien, bio) sont stockées localement sur le smartphone de l'utilisateur, sans transit sur les serveurs de NutriScope.
*   **Pour R6 (Dérive de l'assistant)** : Utiliser un filtrage strict des requêtes par expressions régulières et classifieur avant l'envoi au LLM. Si la question contient un mot médical (ex: "diabète", "guérir", "maladie"), l'assistant renvoie une réponse statique codée en dur : *"Je ne suis pas un dispositif médical, je ne peux pas répondre à cette question."*.

---

## 4. Alternatives Stratégiques (Brique : Substitution d'un produit mal noté)

### Scénario Zéro : Le Statu Quo
*   **Concept** : L'entreprise décide de ne pas développer l'application mobile NutriScope et conserve son organisation actuelle.
*   **Impact financier & opérationnel** : Économie immédiate des 120 000 € du budget MVP. Cependant, l'entreprise ne crée aucun actif technologique. Elle échoue à atteindre les objectifs de 100 000 utilisateurs et ne peut pas préparer la levée de fonds. Le positionnement sur le marché est manqué, laissant la place aux applications concurrentes.