from torch.nn import Softmax
from transformers import AutoTokenizer, AutoModelForSequenceClassification

"""
This code can be used to test a pre-trained sdg-classification-model trained on BERT.

It is, however, incomplete, and throws errors!
"""


class SustainabilityCategoryClassificationSDG:
    MODEL_HUGGINGFACE_URL = "sadickam/sdg-classification-bert"

    @staticmethod
    def classify_sustainability_categories(text: str):
        # Use Huggingface model
        tokenizer = AutoTokenizer.from_pretrained(SustainabilityCategoryClassificationSDG.MODEL_HUGGINGFACE_URL)
        model = AutoModelForSequenceClassification. \
            from_pretrained(SustainabilityCategoryClassificationSDG.MODEL_HUGGINGFACE_URL)

        tokens = tokenizer.encode_plus(text, padding=True, truncation=True, return_tensors="pt")

        outputs = model(**tokens)

        logits = outputs.logits

        softmax = Softmax(dim=1)
        probabilities = softmax(logits)[0]

        # List of the first 16 SDGs
        sdg_goals = [
            "Keine Armut",
            "Kein Hunger",
            "Gesundheit und Wohlergehen",
            "Hochwertige Bildung",
            "Gleichstellung der Geschlechter",
            "Sauberes Wasser und Sanitäreinrichtungen",
            "Bezahlbare und saubere Energie",
            "Menschenwürdige Arbeit und Wirtschaftswachstum",
            "Industrie, Innovation und Infrastruktur",
            "Weniger Ungleichheiten",
            "Nachhaltige Städte und Gemeinden",
            "Verantwortungsvolle Konsum- und Produktionsmuster",
            "Maßnahmen zum Klimaschutz",
            "Leben unter Wasser",
            "Leben an Land",
            "Frieden, Gerechtigkeit und starke Institutionen"
        ]

        # Obtain a list of classes and their probabilities
        sorted_class_probabilities = []
        for i in range(len(sdg_goals)):
            sorted_class_probabilities.append((sdg_goals[i], probabilities[i].item()))

        # Sort the list in descending order of probability
        sorted_class_probabilities.sort(key=lambda x: x[1], reverse=True)
        return sorted_class_probabilities
