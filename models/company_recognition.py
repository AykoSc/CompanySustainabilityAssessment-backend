from database.news_analysis_DAO import NewsAnalysisDAO


class CompanyClassifier:
    """
    Provides functionality to recognize all companies in the database within a given news text.
    Uses basic string matching.
    """

    @staticmethod
    def is_company_in_text(text: str, company_name: str) -> bool:
        """

        :param text: The text to analyze.
        :param company_name: The company name to search for.
        :return: True if the company name is in the given text.
        """
        if company_name in text:
            return True
        else:
            synonyms = NewsAnalysisDAO().get_synonyms_by_company(company_name)
            for synonym in synonyms:
                if synonym.name in text:
                    return True

        return False

    @staticmethod
    def recognize_companies(text: str) -> list[str]:
        """
        Uses string matching to recognize all companies (which exist in the database) within
        a given text.

        :param text: The text to analyze.
        :return: A list of all recognized company names
        """
        company_names = [company.name for company in NewsAnalysisDAO().get_all_companies()]
        mentioned_companies = []

        for company_name in company_names:
            if company_name in text:
                mentioned_companies.append(company_name)
            else:
                synonyms = NewsAnalysisDAO().get_synonyms_by_company(company_name)
                for synonym in synonyms:
                    if synonym.name in text:
                        mentioned_companies.append(company_name)
                        break

        return mentioned_companies
