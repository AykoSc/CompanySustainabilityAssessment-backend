import math
import multiprocessing
import queue
import sched
import threading
import time
from datetime import datetime, timedelta
from typing import Any

import torch
import yaml
from gnews import GNews

from data_classes import NewsTextAnalysisResult
from database.news_analysis_DAO import NewsAnalysisDAO
from exceptions import NoRelevantCompaniesInNewsTextException, LabelNotFoundException
from indicators import Indicators
from logger import logger
from models.company_recognition import CompanyClassifier
from models.sentiment_analysis import SentimentAnalyzer
from models.sustainability_category_classification import SustainabilityCategoryClassification


with open("config.yaml", "r") as stream:
    config = yaml.safe_load(stream)


def _get_gpu_memory_gb() -> int:
    """
    Tries to receive the VRAM of the connected GPU in gigabytes (GB).

    :return: The VRAM in GB, else 0
    """
    if torch.cuda.is_available():
        device = torch.device("cuda")
        gpu_properties = torch.cuda.get_device_properties(device)
        return math.ceil(gpu_properties.total_memory / 1024 ** 3)
    else:
        return 0


def start_analysis(cycle_time_delta: timedelta) -> None:
    """
    Starts the analysis. Each new cycle will be started with a delay of cycle_time_delta.
    If an old cycle has not yet finished, the new cycle waits.
    :param cycle_time_delta: The time delta until the system tries to start a new cycle.
    """
    logger.info(f"Analyse-Zyklus wird alle {cycle_time_delta} Sekunden durchgeführt.")

    _analyze_and_cycle(cycle_time_delta)


def _analyze_and_cycle(cycle_time_delta: timedelta) -> None:
    """
    Helper method for analyze_and_cycle(). Is used to check if the old cycle has finished.
    If so, the method will call itself recursively.
    :param cycle_time_delta: The time delta until the system tries to start a new cycle.
    """
    if len(multiprocessing.active_children()) == 0:
        analyze_api_news_for_each_company()
    else:
        logger.warning("Überspringe Analyse-Zyklus, da noch Analyse-Prozesse aktiv sind.")

    # Timer for the next cycle
    s = sched.scheduler(time.time, time.sleep)
    s.enter(cycle_time_delta.total_seconds(), 1, _analyze_and_cycle, (cycle_time_delta,))
    s.run()


def _get_thread_amount_and_chunks_for_bulk_search(search_items: list[str], max_thread_amount: int) \
        -> tuple[int, list[list[str]]]:
    """
    Used to receive the optimal amount of both threads, and news terms to search for mapped to those threads.
    :param search_items: The items to search for (for the use-case of this project: news terms).
    :param max_thread_amount: The maximum amount of threads that are to be created.
    :return: A pair of the optimal amount of threads, and search term chunks (one for each thread).
    """
    used_threads_amount = min(len(search_items), max_thread_amount)
    if used_threads_amount == 0:
        return 0, []

    chunk_size = len(search_items) // used_threads_amount
    news_chunks = []
    for i in range(used_threads_amount):
        start_index = i * chunk_size
        end_index = (i + 1) * chunk_size if i < used_threads_amount - 1 else len(search_items)
        news_chunks.append(search_items[start_index:end_index])
    return used_threads_amount, news_chunks


def analyze_api_news_for_each_company() -> None:
    """
    Controls the analysis. First, it searches for new news using multithreading.
    Then, it feeds the newly acquired news into analysis processes.
    :return:
    """
    logger.info("Starte Analyse.")

    # Obtain all search terms.
    news_topics_to_search_for = []
    [news_topics_to_search_for.append(company.name) for company in NewsAnalysisDAO().get_all_companies()]
    [news_topics_to_search_for.append(synonym.name) for synonym in NewsAnalysisDAO().get_all_synonyms()]

    # Use threads to increase search speed with parallel searches.
    used_threads_amount, news_chunks = _get_thread_amount_and_chunks_for_bulk_search(news_topics_to_search_for,
                                                                                     config["threads_for_news_search"])
    threads = []
    received_news = queue.Queue()
    for i in range(used_threads_amount):
        analysis_thread = threading.Thread(target=receive_news_from_api_thread,
                                           args=(news_chunks[i], received_news))
        analysis_thread.daemon = True  # daemon: terminates with the main thread.
        threads.append(analysis_thread)
    logger.info("Starte Suche von Nachrichtenbeiträgen.")
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # Use multiprocessing to perform analysis faster.
    received_news_list = [received_news.get() for _ in range(received_news.qsize())]
    try:
        optimal_processes_amount = 1
        if config["use_cuda"]:
            memory_per_process_gb = 3
            gpu_memory_gb = _get_gpu_memory_gb()
            if gpu_memory_gb > 0:
                # Heuristic for the optimal number of processes. May not be optimal for all systems.
                optimal_processes_amount = max(int(gpu_memory_gb / config["vram_gb_per_analysis_multiprocess"]), 1)
                logger.info(f"GPU Arbeitsspeicher: {gpu_memory_gb} GB")
                logger.info(f"Erstelle {optimal_processes_amount} Analyseprozesse")
            else:
                logger.info("Konnte kein CUDA-fähiges Gerät erkenne. Nutze CPU.")
        with multiprocessing.Pool(processes=optimal_processes_amount) as pool:
            pool.map(analyze_news_text, received_news_list)
    except NoRelevantCompaniesInNewsTextException as e:
        logger.warning(f"Überspringe Nachrichtenartikel: {e.args[0]}")
    # Alternative in case multiprocessing is to be fully removed:
    #
    # while not received_news.empty():
    #     try:
    #         news_item = received_news.get()
    #         analyze_news_text(news_item)
    #     except NoRelevantCompaniesInNewsTextException as e:
    #         logger.warning(f"Überspringe Nachrichtenartikel: {e.args[0]}")
    logger.info("Analyse beendet.")


def receive_news_from_api_thread(news_items: list[str], received_news: queue):
    """
    Feeds all search terms into the API and returns the received news.
    :param news_items: News terms/items to search for.
    :param received_news: All the received news from those search terms.
    """
    for item in news_items:
        receive_news_from_api(item, received_news)


def receive_news_from_api(news_topic: str, received_news: queue) -> None:
    """
    Directly interacts with the GNews API and puts the received news into the given queue.

    :param news_topic: News topic to search for.
    :param received_news: Queue to which the acquired news should be attached to.
    """
    google_news = GNews(language="en")
    json_resp = google_news.get_news(news_topic)

    # Obtain the full article texts with newspaper3k.
    for resp in json_resp:
        resp["article"] = resp["title"]  # Fallback, should add_full_article fail or not be used.
        if config["use_entire_news_articles_instead_of_headlines"]:
            add_full_article_to_news_item(resp)

    logger.info(f"{news_topic}: Es wurden {len(json_resp)} Nachrichten gefunden.")

    for news in json_resp:
        # Convert the date into a datetime.date object.
        date_format = "%a, %d %b %Y %H:%M:%S %Z"
        date_object = datetime.strptime(news["published date"], date_format).date()
        news["published date"] = date_object

        received_news.put(news)


def add_full_article_to_news_item(news_item: dict[str, Any]) -> None:
    """
    Scrapes the given news item and attaches the full news text to the "article" attribute.

    :param news_item: The news item to scrape.
    """
    google_news = GNews(language="en")

    article = google_news.get_full_article(news_item["url"])
    if article and article.text:
        news_item["article"] = article.text


def analyze_news_text(news: dict[str, Any]) -> NewsTextAnalysisResult:
    """
    Handles the analysis of a given news item.
    First, it recognizes all companies (saved in the db) in the article.
    Then, it classifies the article into sustainability categories.
    Lastly, it analyzes the sentiment of the article and saves all this information into the db.

    Should the news already be analyzed already, then it only searches for new companies within them.

    The entire process is logged.
    :param news: The news item to analyze.
    :return: The result of the analysis.
    """
    output = f"Analysiere Nachrichtenartikel: {news['title']}"
    news_text = news["article"]

    recognized_company_names = CompanyClassifier.recognize_companies(news_text)

    if len(recognized_company_names) == 0:
        raise NoRelevantCompaniesInNewsTextException(
            "Es muss mindestens ein Unternehmen im Nachrichtenartikel vorkommen.")

    output += "\nIm Text genannte Unternehmen sind:"
    for recognized_company_name in recognized_company_names:
        output += f"\n    Name: {recognized_company_name}"

    news_in_db = NewsAnalysisDAO().get_news_by_news_text(news_text)
    # If this news has not been analyzed yet, then analyze and save everything in the database.
    if news_in_db is None:
        sorted_class_probabilities = SustainabilityCategoryClassification() \
            .classify_sustainability_categories(news_text)

        output += "\nErfolgte Klassifizierung:"
        for i in range(len(sorted_class_probabilities[0])):
            label = sorted_class_probabilities[0][i]
            probability = round(sorted_class_probabilities[1][i], 2)
            output += f"\n    Label: {label:<50} Prob: {probability}"

        analyzed_sentiment = SentimentAnalyzer.analyze_sentiment(news_text)

        output += f"\nErhaltenes Sentiment:\n    {analyzed_sentiment}/10"
        if analyzed_sentiment > 7:
            output += " (Positiv)"
        elif analyzed_sentiment > 3:
            output += " (Neutral)"
        else:
            output += " (Negativ)"
        logger.info(output)

        # Find the index of the label "Not relevant to ESG" in the sorted_class_probabilities[0] list.
        # Then use the same index to get the probability from sorted_class_probabilities[1].
        relevancy_score_label = "Not Relevant to ESG"
        if relevancy_score_label in sorted_class_probabilities[0]:
            index = sorted_class_probabilities[0].index(relevancy_score_label)
            relevancy_score = 1 - sorted_class_probabilities[1][index]
        else:
            raise LabelNotFoundException(sorted_class_probabilities[0])

        new_news = NewsAnalysisDAO().create_news(news["title"], news["article"], news["url"], analyzed_sentiment,
                                                 news["published date"], recognized_company_names, relevancy_score)

        # If no error occurred, save the indicator analysis results.
        if not isinstance(new_news, str):
            for label, probability in zip(sorted_class_probabilities[0], sorted_class_probabilities[1]):
                if label in [indicator.value for indicator in Indicators]:
                    NewsAnalysisDAO().create_news_indicator(new_news.news_ID, label, probability)

    # Otherwise, add new companies to the news and use existing analysis.
    else:
        NewsAnalysisDAO().add_companies_to_news(news_in_db.news_ID, recognized_company_names)
        sorted_class_probabilities = NewsAnalysisDAO().get_news_indicators_by_news(news_in_db.news_ID)
        analyzed_sentiment = news_in_db.sentiment

    return NewsTextAnalysisResult(sorted_class_probabilities, recognized_company_names, analyzed_sentiment)


if __name__ == "__main__":
    start_analysis(timedelta(seconds=config["cycle_time_delta"]))
