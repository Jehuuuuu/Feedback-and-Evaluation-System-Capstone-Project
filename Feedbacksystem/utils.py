import logging
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import requests
import os

logger = logging.getLogger(__name__)
API_TOKEN = os.getenv("HUGGINGFACE_API_KEY")

def get_sentiment(text):
    API_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-xlm-roberta-base-sentiment"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": text})
        response.raise_for_status()  # Raise an exception for HTTP errors
        predictions = response.json()
        return predictions
    except requests.exceptions.RequestException as e:
        print(f"Error using Hugging Face API: {e}")
        return None

def generate_wordcloud(text, max_words=200, width=800, height=400, colormap='viridis'):
    """
    Generate a word cloud image from the given text.
    """
    wordcloud = WordCloud(width=width, height=height, max_words=max_words, background_color="white", colormap=colormap).generate(text)
    
    # Save the word cloud image to a BytesIO object
    img = BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    
    # Return the image as a base64 string for embedding in HTML
    return base64.b64encode(img.getvalue()).decode('utf-8')
