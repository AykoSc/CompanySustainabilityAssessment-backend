import torch
from transformers import pipeline, AutoTokenizer

from database.news_analysis_DAO import NewsAnalysisDAO
from models.esgify_model import ESGify
from models.ner_flair_processing import process_text_using_ner


class SustainabilityCategoryClassification:
    """
    Is used to perform category classification on a given text.
    The analysis includes feeding the text into an ESG category classification AI,
    as well as converting the result into an easily readable format.
    """
    MODEL_HUGGINGFACE_URL = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli"
    MODEL_HUGGINGFACE_URL_NEW = "sileod/deberta-v3-base-tasksource-nli"

    @staticmethod
    def classify_sustainability_categories_zero_shot(text: str):
        """
        Categorize the given text into sustainability categories. This method can be used to perform zero-shot
        classification. This method is often more flexible than pre-trained models, the trade-off often being worse
        performance and/or accuracy.

        :param text: The text to categorize.
        :return: A list consisting of the list of labels at index 0,
        and accordingly the list of probabilities at index 1.
        """
        # Use list of sustainability indicators as labels
        sustainability_indicators = NewsAnalysisDAO().get_all_sustainability_indicators()
        indicator_names = [indicator.name for indicator in sustainability_indicators]

        classifier = pipeline("zero-shot-classification",
                              model=SustainabilityCategoryClassification.MODEL_HUGGINGFACE_URL,
                              device="cuda" if torch.cuda.is_available() else "cpu")
        outputs = classifier(text, indicator_names, multi_label=True)

        class_probabilities = [outputs['labels'], outputs['scores']]
        return class_probabilities

    @staticmethod
    def classify_sustainability_categories(text: str):
        """
        Categorize the given text into sustainability categories. Uses the microsoft/mpnet-base model pre-trained on
        2000 texts with manual annotation of ESG specialists (found at https://huggingface.co/ai-lab/ESGify).

        :param text: The text to categorize.
        :return: A list consisting of the list of labels at index 0,
        and accordingly the list of probabilities at index 1.
        """
        # Loading pre-trained weights of the model and tokenizer
        model = ESGify.from_pretrained('ai-lab/ESGify')
        tokenizer = AutoTokenizer.from_pretrained('ai-lab/ESGify')

        text_with_mask = process_text_using_ner(text)

        # Model inference on the masked text
        to_model = tokenizer.encode_plus(
            text_with_mask,
            add_special_tokens=True,
            max_length=512,
            return_token_type_ids=False,
            padding="max_length",
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
        )
        results = model(**to_model)

        # Map probabilities to labels using id2label
        label_mapping = model.config.id2label
        probabilities = results[0]  # Assuming results is the output tensor you provided

        # Create a list to store label-probability pairs
        label_probabilities = [(label_mapping[i], prob.item()) for i, prob in enumerate(probabilities)]

        # Sort the label-probability pairs by probability in descending order
        label_probabilities.sort(key=lambda x: x[1], reverse=True)

        class_probabilities = [[], []]
        for label, probability in label_probabilities:
            class_probabilities[0].append(label)
            class_probabilities[1].append(probability)

        return class_probabilities
