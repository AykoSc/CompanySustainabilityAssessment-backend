from torch.nn import Softmax
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class SentimentAnalyzer:
    """
    Is used to perform sentiment analysis on a given text.
    The analysis includes feeding the text into a sentiment analysis AI,
    as well as converting the result into an easily readable number.
    """
    MODEL_HUGGINGFACE_URL = "ProsusAI/finbert"
    MODEL_HUGGINGFACE_URL_NEW = "Seethal/sentiment_analysis_generic_dataset"

    @staticmethod
    def analyze_sentiment(text: str) -> float:
        """
        Analyzes the sentiment of a given text using the finbert model available on huggingface.
        :param text: Text to analyze
        :return: Sentiment in the range 0-10, with 0 being negative, 5 neutral, and 10 positive.
        """
        # Use Huggingface model
        tokenizer = AutoTokenizer.from_pretrained(SentimentAnalyzer.MODEL_HUGGINGFACE_URL)
        model = AutoModelForSequenceClassification.from_pretrained(SentimentAnalyzer.MODEL_HUGGINGFACE_URL)

        tokens = tokenizer(text, padding=True, truncation=True, return_tensors="pt", max_length=512)

        outputs = model(**tokens)

        logits = outputs.logits

        softmax = Softmax(dim=1)
        probabilities = softmax(logits)[0].tolist()

        return SentimentAnalyzer.convert_to_rating(probabilities)

    @staticmethod
    def convert_to_rating(probabilities: list[float]) -> float:
        """
        Converts a 3-point sentiment (positive, negative, neutral) into a sentiment rating from 0 to 10,
        where 0 is negative, 5 is neutral, and 10 is positive.

        :param probabilities: 3-point sentiment (positive, negative, neutral)
        :return: Sentiment rating from 0 to 10
        """
        negative_weight = 0
        neutral_weight = 5
        positive_weight = 10

        rating = (probabilities[0] * positive_weight +
                  probabilities[1] * negative_weight +
                  probabilities[2] * neutral_weight) / sum(probabilities)
        return rating
