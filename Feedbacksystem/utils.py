from transformers import pipeline, XLMRobertaTokenizer, XLMRobertaForSequenceClassification
import logging

logger = logging.getLogger(__name__)

class sentiment_pipeline:
    _pipeline = None

    @staticmethod
    def get_pipeline():
        if sentiment_pipeline._pipeline is None:
            try:
                logger.info("Initializing sentiment analysis model...")
                model_path = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
                model = XLMRobertaForSequenceClassification.from_pretrained(model_path)
                tokenizer = XLMRobertaTokenizer.from_pretrained(model_path)
                sentiment_pipeline._pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
                logger.info("Sentiment analysis model initialized successfully.")
            except Exception as e:
                logger.error(f"Error initializing sentiment analysis model: {e}")
                raise
        return sentiment_pipeline._pipeline
