import pytest
import numpy as np
import tensorflow as tf
from PIL import Image
# Import de la fonction depuis votre module (à adapter selon votre arborescence)
from src.classifieur_images import predire_rayon_produit, SEUIL_CONFIANCE, CLASS_NAMES

# =====================================================================
# FIXTURES PYTEST
# =====================================================================

@pytest.fixture(scope="session")
def fake_images_dir(tmp_path_factory):
    """Fixture qui crée un dossier temporaire contenant de vrais fichiers images (.jpg)
    pour que TensorFlow puisse les lire sans planter au décodage."""
    tmp_dir = tmp_path_factory.mktemp("test_data")
    
    # 1. Créer une image unie rouge (représentant un cas standard)
    img_valide_path = tmp_dir / "produit_test.jpg"
    img_valide = Image.new("RGB", (300, 300), color="red")
    img_valide.save(img_valide_path)
    
    return {
        "valide": str(img_valide_path),
        "introuvable": str(tmp_dir / "inexistant.jpg")
    }

def test_predire_rayon_produit_fichier_introuvable(fake_images_dir):
    """Vérifie que la fonction gère correctement l'absence d'un fichier."""
    chemin_incorrect = fake_images_dir["introuvable"]
    resultat = predire_rayon_produit(chemin_incorrect)
    
    assert resultat["rayon"] == "Erreur"
    assert "Fichier introuvable" in resultat["statut"]
    assert resultat["confiance"] == 0.0


def test_predire_rayon_produit_cas_nominal(fake_images_dir, monkeypatch):
    """
    Simule une prédiction réussie avec une confiance élevée (ex: 85%).
    Vérifie que l'API renvoie le bon rayon et le statut 'Succès'.
    """
    chemin_image = fake_images_dir["valide"]
    
    # Mock (simulation) de la méthode de prédiction du modèle pour forcer un résultat à 85% de confiance
    # sur la classe d'index 1 ('cereales')
    def mock_predict(*args, **kwargs):
        # Crée un vecteur de probabilités simulé
        probabilites_simulees = np.array([[0.05, 0.85, 0.05, 0.02, 0.02, 0.01]], dtype=np.float32)
        return probabilites_simulees
    
    # On injecte le comportement simulé directement dans le classifieur importé
    from src import classifieur_images
    monkeypatch.setattr(classifieur_images.model, "predict", mock_predict)
    
    # Appel de la fonction réelle
    resultat = predire_rayon_produit(chemin_image)
    
    # Assertions Pytest
    assert resultat["statut"] == "Succès"
    assert resultat["rayon"] == "cereales"  # Index 1 dans ['biscuits', 'cereales', 'chips'...]
    assert resultat["confiance"] == 85.0
    assert resultat["confiance"] >= SEUIL_CONFIANCE


def test_predire_rayon_produit_sous_seuil_rejet(fake_images_dir, monkeypatch):
    """
    Simule une prédiction très hésitante (ex: l'IA hésite équitablement entre toutes les classes).
    Vérifie que la sécurité s'active et renvoie bien 'Je ne sais pas'.
    """
    chemin_image = fake_images_dir["valide"]
    
    # Mock pour forcer une prédiction floue sous le seuil (ex: l'IA est sûre à seulement 22% pour l'index 0)
    def mock_predict_flou(*args, **kwargs):
        # 22% est la valeur max, mais reste en dessous du seuil de 35%
        probabilites_simulees = np.array([[0.22, 0.18, 0.15, 0.15, 0.15, 0.15]], dtype=np.float32)
        return probabilites_simulees
    
    from src import classifieur_images
    monkeypatch.setattr(classifieur_images.model, "predict", mock_predict_flou)
    
    # Appel de la fonction
    resultat = predire_rayon_produit(chemin_image)
    
    # Assertions Pytest pour valider le mécanisme "Je ne sais pas"
    assert resultat["rayon"] == "Je ne sais pas"
    assert "Rejeté" in resultat["statut"]
    assert resultat["confiance"] == 22.0
    assert "details" in resultat
