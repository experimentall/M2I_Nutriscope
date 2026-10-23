# Étude de Faisabilité - Projet NutriScope

Ce document évalue la faisabilité technique, organisationnelle, juridique et éthique du projet NutriScope à partir du cadrage stratégique, des objectifs business et des contraintes identifiées pour le MVP.

---

## 1. Faisabilité technique : la liste de contrôle

### Données
* **Sources critiques :** La base de données principale est **Open Food Facts**. Les données complémentaires envisagées incluent des informations calculées, des retours utilisateurs et, à terme, des partenariats avec des distributeurs ou des marques.
* **Validation des critères ("Les cinq portes") :** 
  * *Disponibilité :* Oui, via Open Food Facts. 
  * *Volume/Couverture :* Dépendance forte à la couverture initiale d'Open Food Facts. Le comportement de l'application en cas de produit inconnu reste à définir.
  * *Qualité/Fiabilité :* Qualité variable. Les fiches produits sont parfois incomplètes, anciennes, dupliquées ou contradictoires.
  * *Données critiques manquantes :* Absence de données fiables sur le prix et la disponibilité locale des produits en magasin.
  * *Traçabilité :* Obligation stricte de tracer les sources et les versions des données utilisées.

### Approche
* **Type de problème :** Le projet utilise des méthodes algorithmiques et d'IA classiques et connues :
  * **Classification / Régression :** Pour la prédiction du Nutri-Score à partir des caractéristiques du produit.
  * **Similarité / Filtrage :** Pour la recherche et la proposition d'alternatives plus saines selon des critères explicites.
  * **Génération (RAG) :** Un chatbot fondé sur le catalogue et des sources publiques de référence pour l'assistant nutritionnel.
* **Niveau d'innovation :** Il s'agit d'ingénierie et d'intégration de technologies existantes (FastAPI, RAG), et non de recherche fondamentale.

### Performance atteignable
* **Objectif métier :** Fournir une réponse standard en **moins de 3 secondes**, permettant une utilisation fluide en magasin en situation de courses sous contrainte de temps.
* **Engagement :** Aucun engagement contractuel de performance n'est fixé à ce stade du MVP. Le niveau de confiance des informations devra être affiché.

### Intégration
* **Point d'atterrissage :** La prédiction et les réponses atterrissent sur une **interface mobile fluide** (smartphone) via une **API FastAPI**.
* **Mode d'exécution :** Principalement en temps réel (requêtes à la demande lors du scan d'un code-barres ou d'une recherche textuelle).

### Compétences
* **État des lieux :** L'équipe data/IA interne est **très réduite**. Elle est accompagnée par un Product Owner à mi-temps et une UX designer partagée.
* **Contrainte RH :** Il est **impossible de recruter** de nouveaux profils avant la démonstration du MVP. L'équipe doit maîtriser l'architecture RAG et l'ingénierie des données de manière autonome.

### Infrastructure
* **Composants requis :** Conteneurisation, déploiement cloud, intégration et déploiement continus (CI/CD).
* **Disponibilité et budget :** Intégrés dans le budget maximal de **120 000 euros** prévu pour le MVP (incluant la conception, le développement, l'hébergement et les tests utilisateurs). Le coût d'utilisation des modèles génératifs doit être maintenu sous contrôle.
* **Limitation :** Absence actuelle d'une plateforme MLOps complète au sein de l'entreprise.

### Maintenance
* **Responsabilité :** L'équipe data/IA restreinte est responsable de la totalité du chantier, du cadrage à la maintenance en production.
* **Surveillance :** Nécessité de mettre en place un outillage pour surveiller les réponses incorrectes, les dérives du modèle, et les tentatives de détournement de l'assistant (prompt injection). Une procédure de supervision humaine, de retrait ou de correction des données doit être prévue.

---

## 2. Faisabilité organisationnelle

| Question | Pourquoi elle bloque | Qui y répond / Arbitre | Solution NutriScope |
| :--- | :--- | :--- | :--- |
| **Y a-t-il un sponsor avec un budget et une autorité ?** | Sans lui, il n'y a pas d'arbitrage final sur le périmètre ni d'accès sécurisé aux ressources financières. | **Direction générale** | **Claire Delcourt** (Directrice générale et cofondatrice). Pouvoir et intérêt très élevés. Elle porte la vision et valide le budget. |
| **Les utilisateurs sont-ils partie prenante du cadrage ?** | Un outil conçu sans l'alignement des utilisateurs cibles risque d'être inadapté ou contourné. | **Métier / Marketing** | La cible prioritaire est identifiée : les **familles pressées** effectuant leurs courses sur smartphone sous contrainte de temps. |
| **Le processus cible est-il accepté par ceux qui le vivront ?** | Le marketing et le produit doivent s'approprier l'outil. Des tensions existent sur l'exploitation des données et les promesses de calendrier. | **Métier / Produit / RH** | Le marketing souhaite exploiter l'historique des scans pour segmenter, tandis que la direction veut collecter le moins de données possible. Alignement requis lors des ateliers. |
| **Les compétences internes existent-elles pour faire vivre la solution ?** | Un modèle d'IA sans propriétaire technique ou sans gouvernance dérive et devient obsolète en quelques mois. | **DSI / Direction** | L'équipe data/IA gère l'ensemble du cycle de vie. La dépendance à Open Food Facts doit être réduite progressivement sans copier abusivement leurs données. |
| **Le calendrier est-il compatible avec les autres projets ?** | Les équipes produit et UX sont partagées sur d'autres projets, créant un risque de goulet d'étranglement. | **Direction / DSI** | Calendrier ultra-serré : Démonstration au CA dans **10 semaines**, version pilote dans **3 mois**, et lancement public dans **4 mois**. |

---

## 3. Faisabilité juridique et éthique

### RGPD (Règlement Général sur la Protection des Données)
* **Données personnelles :** La personnalisation de l'application implique la collecte ou l'inférence de données personnelles (comptes utilisateurs, profils, préférences hors diagnostic médical).
* **Données de santé sensibles :** Vigilance extrême concernant les données de santé indirectes. L'expression de préférences liées à des pathologies (ex: diabète, allergies) permet de déduire l'état de santé de l'utilisateur.
* **Principes fondamentaux :** Le Délégué à la Protection des Données (DPD/DPO) alerte sur les risques de ralentissement liés à la mise en conformité. Le projet doit intégrer dès la conception :
  * Le consentement explicite de l'utilisateur.
  * La minimisation des données (conflit potentiel avec le marketing qui souhaite exploiter l'historique des scans).
  * La limitation de la durée de conservation et le droit d'accès/suppression.
* **Analyse d'Impact :** Une **AIPD (Analyse d'Impact sur la Protection des Données)** est fortement recommandée, voire obligatoire, en raison du traitement potentiel à grande échelle de profils de consommation liés à la santé.

### AI Act
* **Classification du système :** L'assistant conversationnel nutritionnel de NutriScope entre dans la catégorie des systèmes d'IA à **risque minimal** ou soumis à des **obligations de transparence** (informer explicitement l'utilisateur qu'il interagit avec une IA).
* **Exclusion du Haut Risque :** NutriScope **refuse le diagnostic, la prescription ou le remplacement d'un professionnel de santé**. L'application ne souhaite pas devenir un dispositif médical, ce qui exclut les réglementations de santé de l'Annexe III de l'AI Act.

### Licences
* **Open Food Facts :** Les données utilisées proviennent majoritairement de cette base distribuée sous licence **ODbL (Open Database License)**. 
* **Obligations :** NutriScope doit obligatoirement créditer Open Food Facts. Toute modification ou enrichissement direct de la base de données partagée doit être republié sous la même licence (partage à l'identique). L'entreprise doit veiller à ne pas recopier ou revendre abusivement ces données ouvertes.

### Propriété intellectuelle
* **Modèles et code :** Le MVP reposant sur des API et des modèles externes, la propriété intellectuelle de NutriScope se concentrera sur le code applicatif propriétaire (FastAPI), l'architecture de la base de données locale enrichie, et les briques spécifiques du système RAG.

### Responsabilité
* **Erreurs de recommandation :** Une recommandation alimentaire erronée ou dangereuse pour une personne allergique ou diabétique constitue un **risque majeur de crise** pour l'entreprise. 
* **Engagement légal :** Bien que NutriScope décline toute responsabilité médicale, un conseil nutritionnel faux engage sa réputation et sa responsabilité civile. Les réponses du chatbot doivent être strictement encadrées et refuser les demandes d'ordre médical.

### Éthique
* **Biais et discrimination :** Intégration dès la conception de mécanismes de prévention des biais envers certains régimes, budgets, cultures alimentaires ou situations de handicap.
* **Inclusion :** L'accessibilité numérique doit être prise en compte dès le développement de l'interface mobile.
* **Positionnement moral :** L'application doit être perçue comme un outil d'aide transparent, pédagogique et bienveillant, sans jamais devenir culpabilisante ou moralisatrice envers l'utilisateur.
