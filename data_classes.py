class NewsTextAnalysisResult:
    def __init__(self, sustainability_probabilities, recognized_companies, sentiment):
        self.sustainability_probabilities = sustainability_probabilities
        self.recognized_companies = recognized_companies
        self.sentiment = sentiment
