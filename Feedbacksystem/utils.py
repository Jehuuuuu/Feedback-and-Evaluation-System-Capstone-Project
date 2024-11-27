import pickle
from sklearn.ensemble import RandomForestClassifier
from django.conf import settings
from .models import LikertEvaluation
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import matplotlib.pyplot as plt
import pandas as pd
import pickle
import base64
import re
import os
import nltk

try:
    stopwords.words("english")
except LookupError:
    nltk.download("stopwords")
STOPWORDS = set(stopwords.words("english"))

def load_prediction_models():
    # Loads the pickled prediction models for use in Django views. 
    
    with open(os.path.join(settings.BASE_DIR, 'Models', 'xgboost_model.pkl'), 'rb') as f:
        predictor = pickle.load(f)

    with open(os.path.join(settings.BASE_DIR, 'Models', 'scaler.pkl'), 'rb') as f:
        scaler = pickle.load(f)

    with open(os.path.join(settings.BASE_DIR, 'Models', 'countVectorizer.pkl'), 'rb') as f:
        cv = pickle.load(f)

    return predictor, scaler, cv

def single_prediction(comments):
    predictor, scaler, cv = load_prediction_models()
    corpus = []
    stemmer = PorterStemmer()
    nltk.download('punkt')  # Download sentence tokenizer (optional, but recommended for negation)
    review = re.sub(r'[^\w\s]', '', comments)  # Remove non-alphanumeric characters
    review = review.lower().split()

    negated = False
    NEGATION_WORDS = {"not", "no", "never", "n't", "wouldn't", "couldn't", "shouldn't", "didn't", "isn't", "ain't"}
    POSITIVE_WORDS = {"like", "grasp", "has", }  # Add "like" to positive words
    NEGATIVE_WORDS = {"bad", "unsatisfactory"}  # Add "bad" to negative words
    processed_words = []
    for word in review:
        if word in NEGATION_WORDS:
            negated = True
        elif negated:
            processed_words.append(f"NOT_{stemmer.stem(word)}")  # Append negated word
            negated = False  # Reset negation flag
        elif word in POSITIVE_WORDS:  # Check if the word is positive
            processed_words.append("best")  # Replace "like" with a designated positive token
        elif word in NEGATIVE_WORDS:  # Check if the word is negative
            processed_words.append("poor")  # Replace "bad" with a designated negative token
        else:
            processed_words.append(stemmer.stem(word))

    review = ' '.join(processed_words)
    corpus.append(review)
    X_prediction = cv.transform(corpus).toarray()
    X_prediction_scl = scaler.transform(X_prediction)
    y_predictions = predictor.predict_proba(X_prediction_scl)
    y_predictions = y_predictions.argmax(axis=1)[0]

    return "Positive" if y_predictions == 1 else "Negative"