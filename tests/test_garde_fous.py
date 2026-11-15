import pytest
from src.garde_fous import normaliser_texte, verifier_requete_medicale


class TestNormaliserTexte:
    def test_minuscules_et_accents(self):
        assert normaliser_texte("Diabète & Glycémie Élevée") == "diabete & glycemie elevee"

    def test_entree_non_chaine(self):
        assert normaliser_texte(None) == ""
        assert normaliser_texte(123) == ""


class TestVerifierRequeteMedicale:
    @pytest.mark.parametrize("question", [
        "Ce biscuit est-il bon pour le diabète ?",
        "J'ai du cholestérol, que manger ?",
        "Je suis enceinte, puis-je boire ce lait ?",
        "Quelle est la teneur en sucre pour mon traitement médical ?",
        "Est-ce que ce produit déclenche une ALLERGIE ?",
    ])
    def test_detection_intention_medicale(self, question):
        refus = verifier_requete_medicale(question)
        assert refus is not None
        assert "professionnel de santé" in refus

    @pytest.mark.parametrize("question", [
        "Quel est le Nutri-Score du Nutella ?",
        "Donne-moi les valeurs nutritionnelles des biscuits Prince.",
        "Une alternative plus saine au soda ?",
        # Vérification des frontières de mots (\b) : "maladie" ne doit pas matcher un faux positif
        "Combien de calories dans ce plat ?",
    ])
    def test_requete_nutritionnelle_autorisee(self, question):
        assert verifier_requete_medicale(question) is None
