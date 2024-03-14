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
    review = re.sub("[^a-zA-Z]", " ", comments)
    review = review.lower().split()
    review = [stemmer.stem(word) for word in review if not word in STOPWORDS]
    review = " ".join(review)
    corpus.append(review)
    X_prediction = cv.transform(corpus).toarray()
    X_prediction_scl = scaler.transform(X_prediction)
    y_predictions = predictor.predict_proba(X_prediction_scl)
    y_predictions = y_predictions.argmax(axis=1)[0]

    return "Positive" if y_predictions == 1 else "Negative"