import joblib
import os


class ScamIntentDetector:
    
    def __init__(self):
        self.vectorizer = None  # TF-IDF Vectorizer
        self.classifier = None  # XGBoost Classifier
        self.models_loaded = False

        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.models_dir = os.path.join(self.base_dir, "models")

        self._load_models()
    
    def _load_models(self):
        vectorizer_path = os.path.join(self.models_dir, "tfidf_vectorizer.pkl")
        classifier_path = os.path.join(self.models_dir, "xgb_model.pkl")
        
        if not os.path.exists(vectorizer_path):
            print(f"Warning: TF-IDF vectorizer not found at {vectorizer_path}")
            return
        
        if not os.path.exists(classifier_path):
            print(f"Warning: XGBoost classifier not found at {classifier_path}")
            return
        
        try:
            self.vectorizer = joblib.load(vectorizer_path)
            self.classifier = joblib.load(classifier_path)
            self.models_loaded = True
            print("TF-IDF + XGBoost scam detection models loaded successfully!")
        except Exception as e:
            print(f"Error loading scam detection models: {e}")
            self.models_loaded = False
    
    def predict(self, text: str, threshold: float = 0.5) -> bool:
        if not self.models_loaded:
            return self._fallback_prediction(text)
        
        try:
            # Get probability and classify based on threshold
            probability = self.get_probability(text)
            is_scam = probability >= threshold
            
            print(f"[ScamDetector] Probability: {probability:.2%} | Threshold: {threshold:.0%} | Is Scam: {is_scam}")
            
            return is_scam
            
        except Exception as e:
            print(f"Error during prediction: {e}")
            return self._fallback_prediction(text)
    
    def get_probability(self, text: str) -> float:
        if not self.models_loaded:
            return 0.0
        
        try:
            text_vectorized = self.vectorizer.transform([text])
            
            if hasattr(self.classifier, 'predict_proba'):
                proba = self.classifier.predict_proba(text_vectorized)[0]
                # Assuming index 1 is the "scam" class
                return float(proba[1]) if len(proba) > 1 else float(proba[0])
            else:
                prediction = self.classifier.predict(text_vectorized)[0]
                return 1.0 if prediction else 0.0
                
        except Exception as e:
            print(f"Error getting probability: {e}")
            return 0.0
    
    def _fallback_prediction(self, text: str) -> bool:
        SCAM_KEYWORDS = [
            "urgent", "verify", "blocked", "suspended", "click", "otp",
            "prize", "winner", "lottery", "account", "password", "bank",
            "transfer", "payment", "kyc", "expire", "limited time"
        ]
        text_lower = text.lower()
        matches = sum(1 for keyword in SCAM_KEYWORDS if keyword in text_lower)
        return matches >= 2
    
_detector_instance = ScamIntentDetector()

def detect_scam_intent(message_text: str) -> bool:
    return _detector_instance.predict(message_text)