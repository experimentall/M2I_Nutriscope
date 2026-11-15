import json
import pandas as pd
import pytest
from unittest.mock import patch
from src.outils import formater_fiche, CatalogueOutils


class TestFormaterFiche:
    def test_fiche_complete(self):
        ligne = {
            "code": "3017620422003",
            "nom": "Pâte à tartiner",
            "nutriscore": "e",
            "kcal": 539.456,
            "lipides": 30.9,
            "satures": 10.6,
            "sucres": 56.3,
            "sel": 0.107,
            "fibres": 3.4,
            "proteines": 6.3,
        }
        fiche = formater_fiche(ligne)
        assert fiche["nutriscore"] == "E"
        assert fiche["incomplet"] is False
        assert fiche["nutriments"]["kcal"] == 539.46

    def test_fiche_incomplete_avec_nan(self):
        ligne = {
            "code": "12345",
            "nom": "Produit incomplet",
            "nutriscore": float("nan"),
            "kcal": 200,
            "lipides": None,
            "satures": 2.0,
            "sucres": 10.0,
            "sel": 0.5,
            "fibres": float("nan"),
            "proteines": 5.0,
        }
        fiche = formater_fiche(ligne)
        assert fiche["nutriscore"] is None
        assert fiche["incomplet"] is True
        assert fiche["nutriments"]["lipides"] is None
        assert fiche["nutriments"]["fibres"] is None


@pytest.fixture
def catalogue_mock():
    """Crée une instance de CatalogueOutils avec un DataFrame en mémoire."""
    df_fictif = pd.DataFrame([
        {
            "code": "111", "nom": "Biscuit Chocolat", "nutriscore": "E",
            "kcal": 500, "lipides": 25, "satures": 12, "sucres": 40,
            "sel": 0.5, "fibres": 2, "proteines": 6
        },
        {
            "code": "222", "nom": "Biscuit Avoine", "nutriscore": "B",
            "kcal": 410, "lipides": 14, "satures": 2, "sucres": 15,
            "sel": 0.3, "fibres": 8, "proteines": 9
        },
        {
            "code": "333", "nom": "Lait Demi-Écrémé", "nutriscore": "A",
            "kcal": 46, "lipides": 1.5, "satures": 1.0, "sucres": 4.8,
            "sel": 0.1, "fibres": 0.0, "proteines": 3.2
        }
    ])

    with patch("src.outils.preparation_donnee", return_value=df_fictif), \
         patch("src.outils.compute_scales", return_value={}):
        yield CatalogueOutils()


class TestCatalogueOutils:
    def test_recherche_par_code_ok(self, catalogue_mock):
        res = catalogue_mock.chercher_produit(code="333")
        assert res["statut"] == "ok"
        assert res["total"] == 1
        assert res["produits"][0]["nom"] == "Lait Demi-Écrémé"

    def test_recherche_par_nom_ambigu(self, catalogue_mock):
        res = catalogue_mock.chercher_produit(nom="biscuit")
        assert res["statut"] == "ambigu"
        assert res["total"] == 2
        assert len(res["produits"]) == 2

    def test_recherche_introuvable(self, catalogue_mock):
        res = catalogue_mock.chercher_produit(nom="pizza")
        assert res["statut"] == "introuvable"
        assert res["total"] == 0
        assert res["produits"] == []

    def test_priorite_code_sur_nom(self, catalogue_mock):
        res = catalogue_mock.chercher_produit(nom="biscuit", code="333")
        assert res["statut"] == "ok"
        assert res["produits"][0]["code"] == "333"

    def test_avec_alternatives(self, catalogue_mock):
        alts_fictives = [{"code": "222", "nom": "Biscuit Avoine", "nutriscore": "B", "sucres": 15, "satures": 2, "kcal": 410}]
        with patch("src.outils.suggest_substitutes", return_value=alts_fictives) as mock_sub:
            res = catalogue_mock.chercher_produit(code="111", avec_alternatives=True)
            mock_sub.assert_called_once()
            assert "alternatives_saines" in res["produits"][0]
            assert res["produits"][0]["alternatives_saines"][0]["code"] == "222"


class TestValidationAppelBrut:
    def test_outil_non_autorise(self, catalogue_mock):
        res = catalogue_mock.executer_appel_brut("supprimer_base", "{}")
        assert "erreur" in res

    def test_json_invalide(self, catalogue_mock):
        res = catalogue_mock.executer_appel_brut("chercher_produit", "{bad json")
        assert "erreur" in res

    @pytest.mark.parametrize("payload", [
        {},  # Ni nom ni code
        {"nom": "lait", "param_inconnu": 123},  # Clé non autorisée
        {"nom": 12345},  # Mauvais type pour nom
        {"nom": "lait", "limite": 10},  # Limite hors bornes [1, 5]
        {"nom": "lait", "limite": True},  # Booléen passé à la place d'un int
        {"nom": "lait", "avec_alternatives": "oui"},  # Mauvais type booléen
    ])
    def test_arguments_invalides(self, catalogue_mock, payload):
        res = catalogue_mock.executer_appel_brut("chercher_produit", json.dumps(payload))
        assert "erreur" in res
