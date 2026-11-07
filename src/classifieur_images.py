import os
import numpy as np
import tensorflow as tf
from pathlib import Path

# Configuration des constantes (doivent matcher l'entraînement)
IMG_HEIGHT, IMG_WIDTH = 180, 180
SEUIL_CONFIANCE = 35.0  # Justification : > 2x le hasard pur (16.67% pour 6 classes)

# Définition manuelle ou dynamique des classes dans le bon ordre alphabétique
# (Assurez-vous que cet ordre correspond EXACTEMENT à vos dossiers d'origine)
CLASS_NAMES = ['biscuits', 'cereales', 'chips', 'chocolats', 'pates', 'pizzas']

CURRENT_PATH = Path(__file__).resolve().parent
# Chargement unique du modèle (pour éviter de le recharger à chaque appel d'API)
MODEL_PATH = CURRENT_PATH.parent / "data" / "checkpoints" / "cnn_images_ft.keras"

if os.path.exists(MODEL_PATH):
    print(f"Chargement du modèle de Fine-Tuning : {MODEL_PATH}")
    model = tf.keras.models.load_model(MODEL_PATH)
else:
    raise FileNotFoundError(f"Le fichier modèle est introuvable à l'emplacement : {MODEL_PATH}")


def predire_rayon_produit(image_path: str):
    if not os.path.exists(image_path):
        return {
            "rayon": "Erreur", 
            "confiance": 0.0, 
            "statut": f"Fichier introuvable : {image_path}"
        }
    
    """
    Analyse une photo de produit, applique les prétraitements natifs de MobileNetV2,
    et renvoie le rayon ainsi que l'indice de confiance. Retoune 'Je ne sais pas' sous le seuil.
    """
    try:
        # Prétraitement binaire identique au pipeline tf.data du projet
        img_raw = tf.io.read_file(image_path)
        img_decoded = tf.io.decode_image(img_raw, channels=3, expand_animations=False)
        img_resized = tf.image.resize(img_decoded, [IMG_HEIGHT, IMG_WIDTH])
        img_batch = tf.expand_dims(img_resized, axis=0)  # Shape finale : (1, 180, 180, 3)

        # Inférence (Prédiction)
        preds = model.predict(img_batch, verbose=0)[0]  # Récupère le vecteur de probabilités
        
        # Extraction de la meilleure classe et de sa confiance
        best_class_idx = np.argmax(preds)
        confiance = preds[best_class_idx] * 100

        # Vérification du seuil de sécurité
        if confiance < SEUIL_CONFIANCE:
            return {
                "rayon": "Je ne sais pas",
                "confiance": float(confiance),
                "statut": "Rejeté (Confiance trop faible)",
                "details": f"La classe détectée était '{CLASS_NAMES[best_class_idx]}' mais sous le seuil de {SEUIL_CONFIANCE}%"
            }
        
        return {
            "rayon": CLASS_NAMES[best_class_idx],
            "confiance": float(confiance),
            "statut": "Succès"
        }

    except tf.errors.NotFoundError:
        return {"rayon": "Erreur", "confiance": 0.0, "statut": f"Fichier introuvable : {image_path}"}
    except Exception as e:
        return {"rayon": "Erreur", "confiance": 0.0, "statut": f"Erreur technique : {str(e)}"}
