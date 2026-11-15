from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest
from src.assistant import AssistantNutriScope


def _creer_reponse_llm(content=None, tool_calls=None, prompt_tokens=10, completion_tokens=5):
    """Helper pour simuler la structure de réponse de client.chat.completions.create."""
    message = SimpleNamespace(content=content, tool_calls=tool_calls)
    choice = SimpleNamespace(message=message)
    usage = SimpleNamespace(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)
    return SimpleNamespace(choices=[choice], usage=usage)


@pytest.fixture
def assistant_mock():
    catalogue = MagicMock()
    with patch("src.assistant.OpenAI") as mock_openai_cls:
        assistant = AssistantNutriScope(catalogue_outils=catalogue, max_tours=2)
        assistant.client = mock_openai_cls.return_value
        yield assistant, catalogue


class TestAssistantNutriScope:
    def test_blocage_garde_fou_medical_sans_appel_llm(self, assistant_mock):
        assistant, _ = assistant_mock
        resultat = assistant.demander("Ce produit est-il adapté pour mon diabète ?")

        assert resultat["garde_fou_declenche"] is True
        assert resultat["appels_outils"] == []
        assert resultat["tokens_entree"] == 0
        assistant.client.chat.completions.create.assert_not_called()

    def test_flux_nominal_avec_appel_outil(self, assistant_mock):
        assistant, catalogue = assistant_mock

        # Le LLM demande l'exécution de chercher_produit
        appel_outil = SimpleNamespace(
            id="call_1",
            function=SimpleNamespace(name="chercher_produit", arguments='{"nom": "lait"}')
        )
        rep_tour_1 = _creer_reponse_llm(tool_calls=[appel_outil], prompt_tokens=50, completion_tokens=15)

        # Le LLM formule la réponse finale après réception du résultat
        rep_tour_2 = _creer_reponse_llm(content="Le lait demi-écrémé a un Nutri-Score A.", prompt_tokens=80, completion_tokens=20)

        assistant.client.chat.completions.create.side_effect = [rep_tour_1, rep_tour_2]
        catalogue.executer_appel_brut.return_value = {"statut": "ok", "total": 1, "produits": [{"nom": "Lait", "nutriscore": "A"}]}

        resultat = assistant.demander("Quel est le Nutri-Score du lait ?")

        assert resultat["garde_fou_declenche"] is False
        assert resultat["reponse"] == "Le lait demi-écrémé a un Nutri-Score A."
        assert len(resultat["appels_outils"]) == 1
        assert resultat["appels_outils"][0]["outil"] == "chercher_produit"
        assert resultat["tokens_entree"] == 130
        assert resultat["tokens_sortie"] == 35

    def test_securite_max_tours_atteint(self, assistant_mock):
        assistant, catalogue = assistant_mock

        # Le LLM boucle indéfiniment sur des appels d'outils
        appel_outil = SimpleNamespace(
            id="call_loop",
            function=SimpleNamespace(name="chercher_produit", arguments='{"nom": "biscuit"}')
        )
        rep_boucle = _creer_reponse_llm(tool_calls=[appel_outil])
        assistant.client.chat.completions.create.return_value = rep_boucle
        catalogue.executer_appel_brut.return_value = {"statut": "introuvable", "total": 0, "produits": []}

        resultat = assistant.demander("Cherche un biscuit")

        assert "limite d'étapes autorisée" in resultat["reponse"]
        assert len(resultat["appels_outils"]) == 2  # Correspond à max_tours=2

    def test_reinitialisation_historique(self, assistant_mock):
        assistant, _ = assistant_mock
        assistant.demander("Question sur le diabète")
        assert len(assistant.historique) == 3  # system + user + assistant

        assistant.reinitialiser()
        assert len(assistant.historique) == 1
        assert assistant.historique[0]["role"] == "system"
