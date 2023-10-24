import os
import re
from datetime import date
from multiprocessing import Lock
from typing import Type, Optional

import yaml
from sqlalchemy import func, column, desc, asc
from sqlalchemy.orm import Session

from database.db_creation import Company, News, SustainabilityIndicator, Synonym, NewsIndicator, Contains, \
    build_db_and_create_engine
from exceptions import NoRelevantCompaniesInNewsTextException
from indicators import Indicators
from logger import logger


def _handle_db_exception(exception: Exception):
    """
    Handles db exceptions by formatting them properly. This helps make the console output
    more readable.

    :param exception: The Exception to be handled.
    """
    unique_match = re.search(r"UNIQUE constraint failed", str(exception))
    foreign_key_match = re.search(r"FOREIGN KEY", str(exception))
    if unique_match:
        unique_values = re.search(r"INTO (.+) VALUES", str(exception)).group(1)
        error_message = f"Eintrag existiert bereits: {unique_values}. Befehl wird ignoriert."
        logger.warning(error_message)
    elif foreign_key_match:
        foreign_column_name = re.search(r'INTO "(\w+)" \(', str(exception)).group(1)
        error_message = (f"Eintrag für '{foreign_column_name}' verletzt die Fremdschlüsselbeziehung. Befehl wird "
                         f"ignoriert.")
        logger.warning(error_message)
    else:
        logger.exception(exception)


class NewsAnalysisDAO:
    """
    This class uses the DAO pattern in order to access the database on an abstract level.
    This makes it especially easy to change the database type (e.g., from SQLite to another).

    Various methods exist to provide all functionality necessary. The methods have been directly named
    after the pre-defined functional requirements.
    """

    DB_PATH = "database/db.sqlite"
    _engine = None
    _lock = Lock()
    _config = None

    def __init__(self):
        with NewsAnalysisDAO._lock:
            with open("config.yaml", "r") as stream:
                NewsAnalysisDAO._config = yaml.safe_load(stream)

            add_indicators_to_db = False

            # Should DB file be non-existent, create it
            if not os.path.exists(NewsAnalysisDAO.DB_PATH):
                open(NewsAnalysisDAO.DB_PATH, "w").close()
                add_indicators_to_db = True

            # Create database und connection (can be changed with e.g., MySQL)
            if NewsAnalysisDAO._engine is None:
                NewsAnalysisDAO._engine = build_db_and_create_engine(NewsAnalysisDAO.DB_PATH)

            if add_indicators_to_db:
                [self.create_sustainability_indicator(indicator.value) for indicator in Indicators]
                logger.info("Datenbank erstellt.")

    def get_company_by_name(self, name: str) -> Optional[Type[Company]]:
        with Session(self._engine) as session:
            try:
                return session. \
                    query(Company). \
                    filter_by(name=name). \
                    first()
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()

    def get_all_companies(self) -> list[Type[Company]]:
        with Session(self._engine) as session:
            try:
                return session. \
                    query(Company). \
                    all()
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()

    def get_all_synonyms(self) -> list[Type[Synonym]]:
        with Session(self._engine) as session:
            try:
                return session. \
                    query(Synonym). \
                    all()
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()

    def get_all_news(self) -> list[Type[News]]:
        with Session(self._engine) as session:
            try:
                return session. \
                    query(News). \
                    all()

            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()

    def get_all_sustainability_indicators(self) -> list[Type[SustainabilityIndicator]]:
        with Session(self._engine) as session:
            try:
                return session. \
                    query(SustainabilityIndicator). \
                    order_by(desc(column("name"))). \
                    all()
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()

    def get_synonyms_by_company(self, company_name: str) -> list[Type[Synonym]]:
        with Session(self._engine) as session:
            try:
                return session. \
                    query(Synonym). \
                    filter_by(company_name=company_name). \
                    all()
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()

    def get_news_by_company_and_date_range(self, company_name: str, max_sentiment: float,
                                           from_date: date = date.min) -> list[Type[News]]:
        with Session(self._engine) as session:
            try:
                return session. \
                    query(News). \
                    join(Contains). \
                    join(NewsIndicator). \
                    filter(Contains.company_name == company_name,
                           News.sentiment <= max_sentiment,
                           News.relevancy_score >= NewsAnalysisDAO._config["news_are_relevant_threshold"],
                           NewsIndicator.probability >= NewsAnalysisDAO._config["indicator_belongs_to_news_threshold"],
                           News.date >= from_date). \
                    order_by(asc(column("sentiment"))). \
                    all()
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()

    def get_news_by_company_indicator_and_date_range(self, company_name: str, indicator_name: str, max_sentiment: float,
                                                     from_date: date = date.min) -> list[Type[News]]:
        with Session(self._engine) as session:
            try:
                return session. \
                    query(News). \
                    join(Contains). \
                    join(NewsIndicator). \
                    filter(Contains.company_name == company_name,
                           NewsIndicator.sustainability_indicator_name == indicator_name,
                           NewsIndicator.probability >= NewsAnalysisDAO._config["indicator_belongs_to_news_threshold"],
                           News.sentiment <= max_sentiment,
                           News.relevancy_score >= NewsAnalysisDAO._config["news_are_relevant_threshold"],
                           News.date >= from_date). \
                    order_by(asc(column("sentiment"))). \
                    all()
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()

    def get_news_with_lowest_sentiment_by_company_and_date_range(self, company_name: str,
                                                                 from_date: date = date.min) -> Type[News]:
        with Session(self._engine) as session:
            try:
                lowest_sentiment_news = session. \
                    query(News). \
                    join(Contains). \
                    join(NewsIndicator). \
                    filter(Contains.company_name == company_name,
                           NewsIndicator.probability >= NewsAnalysisDAO._config["indicator_belongs_to_news_threshold"],
                           News.relevancy_score >= NewsAnalysisDAO._config["news_are_relevant_threshold"],
                           News.date >= from_date). \
                    order_by(asc(column("sentiment"))). \
                    first()
                return lowest_sentiment_news
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()

    def get_news_with_lowest_sentiment_by_company_indicator_and_date_range(self, company_name: str, indicator_name: str,
                                                                           from_date: date = date.min) -> Type[News]:
        with Session(self._engine) as session:
            try:
                lowest_sentiment_news = session. \
                    query(News). \
                    join(Contains). \
                    join(NewsIndicator). \
                    filter(Contains.company_name == company_name,
                           NewsIndicator.sustainability_indicator_name == indicator_name,
                           NewsIndicator.probability >= NewsAnalysisDAO._config["indicator_belongs_to_news_threshold"],
                           News.relevancy_score >= NewsAnalysisDAO._config["news_are_relevant_threshold"],
                           News.date >= from_date). \
                    order_by(asc(column("sentiment"))). \
                    first()
                return lowest_sentiment_news
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()

    def do_news_exist_by_company_and_date_range(self, company_name: str, from_date: date, max_sentiment: float) -> bool:
        return len(self.get_news_by_company_and_date_range(company_name, max_sentiment, from_date)) > 0

    def do_news_exist_by_company_indicator_and_date_range(self, company_name: str, from_date: date, indicator_name: str,
                                                          max_sentiment: float) -> bool:
        return len(self.get_news_by_company_indicator_and_date_range(company_name, indicator_name, max_sentiment,
                                                                     from_date)) > 0

    def get_news_by_news_text(self, text: str) -> Optional[Type[News]]:
        with Session(self._engine) as session:
            try:
                return session. \
                    query(News). \
                    filter(News.text == text). \
                    first()
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()

    def get_news_indicators_by_news(self, news_id: int) -> list[Type[NewsIndicator]]:
        with Session(self._engine) as session:
            try:
                return session. \
                    query(NewsIndicator). \
                    filter(NewsIndicator.news_ID == news_id). \
                    order_by(desc(column("probability"))). \
                    all()
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()

    def get_sentiment_stats_by_company_and_date_range(self, company_name: str, max_sentiment: float, from_date: date) \
            -> Optional[tuple[float, float, float]]:
        with Session(self._engine) as session:
            try:
                query_result = session.query(
                    func.min(News.sentiment).label('min_sentiment'),
                    func.avg(News.sentiment).label('avg_sentiment'),
                    func.max(News.sentiment).label('max_sentiment')
                ).join(Contains). \
                    join(NewsIndicator). \
                    filter(
                    Contains.company_name == company_name,
                    News.sentiment <= max_sentiment,
                    NewsIndicator.probability >= NewsAnalysisDAO._config["indicator_belongs_to_news_threshold"],
                    News.relevancy_score >= NewsAnalysisDAO._config["news_are_relevant_threshold"],
                    News.date >= from_date
                ).one()

                return (
                    query_result.min_sentiment,
                    query_result.avg_sentiment,
                    query_result.max_sentiment
                )
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()

    def get_sentiment_stats_by_company_indicator_and_date_range(self, company_name: str, max_sentiment: float,
                                                                indicator_name: str, from_date: date) \
            -> Optional[tuple[float, float, float]]:
        with Session(self._engine) as session:
            try:
                query_result = session.query(
                    func.min(News.sentiment).label('min_sentiment'),
                    func.avg(News.sentiment).label('avg_sentiment'),
                    func.max(News.sentiment).label('max_sentiment')
                ).join(Contains). \
                    join(NewsIndicator). \
                    filter(NewsIndicator.sustainability_indicator_name == indicator_name,
                           Contains.company_name == company_name,
                           News.sentiment <= max_sentiment,
                           NewsIndicator.probability >= NewsAnalysisDAO._config["indicator_belongs_to_news_threshold"],
                           News.relevancy_score >= NewsAnalysisDAO._config["news_are_relevant_threshold"],
                           News.date >= from_date
                           ).one()

                return (
                    query_result.min_sentiment,
                    query_result.avg_sentiment,
                    query_result.max_sentiment
                )
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()

    def create_company(self, name: str) -> Optional[Company]:
        with Session(self._engine) as session:
            try:
                new_company = Company(name=name)
                session.add(new_company)
                session.commit()
                return new_company
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()

    def create_synonym(self, company_name: str, name: str) -> Optional[Synonym]:
        with Session(self._engine) as session:
            try:
                new_synonym = Synonym(company_name=company_name, name=name)
                session.add(new_synonym)
                session.commit()
                return new_synonym
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()

    def _create_contains(self, news_id: int, company_name: str) -> Optional[Contains]:
        with Session(self._engine) as session:
            try:
                new_contains = Contains(news_ID=news_id, company_name=company_name)
                session.add(new_contains)
                session.commit()
                return new_contains
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()

    def add_companies_to_news(self, news_id: int, company_names: list[str]) -> list[Contains]:
        new_contains = []
        with Session(self._engine) as session:
            try:
                for company in company_names:
                    new_contains.append(self._create_contains(news_id, company))
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()
        return new_contains

    def create_news(self, title: str, text: str, link: str, sentiment: float, news_date: date,
                    contained_company_names: list[str], relevancy_score) -> Optional[News]:
        with Session(self._engine) as session:
            try:
                # Modeling total relationship from News to Company
                if not contained_company_names:
                    raise NoRelevantCompaniesInNewsTextException(
                        "Es muss mindestens ein Unternehmen im Nachrichtenartikel vorkommen.")

                new_news = News(title=title, text=text, link=link, sentiment=sentiment, date=news_date,
                                relevancy_score=relevancy_score)
                session.add(new_news)
                session.commit()

                self.add_companies_to_news(new_news.news_ID, contained_company_names)

                return new_news
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()

    def create_sustainability_indicator(self, sustainability_indicator_name: str) -> Optional[SustainabilityIndicator]:
        with Session(self._engine) as session:
            try:
                new_indicator = SustainabilityIndicator(name=sustainability_indicator_name)
                session.add(new_indicator)
                session.commit()
                return new_indicator
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()

    def create_news_indicator(self, news_id: int, indicator_name: str, probability: float) -> Optional[NewsIndicator]:
        with Session(self._engine) as session:
            try:
                new_news_indicator = NewsIndicator(news_ID=news_id, sustainability_indicator_name=indicator_name,
                                                   probability=probability)
                session.add(new_news_indicator)
                session.commit()
                return new_news_indicator
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()

    def delete_company(self, company_name: str) -> bool:
        with Session(self._engine) as session:
            try:
                company = self.get_company_by_name(company_name)
                if company:
                    session.delete(company)
                    session.commit()
                    return True
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()
        return False

    def delete_synonym(self, company_name: str, synonym_name: str) -> bool:
        with Session(self._engine) as session:
            try:
                synonym = session.query(Synonym).filter_by(company_name=company_name, name=synonym_name).first()
                if synonym:
                    session.delete(synonym)
                    session.commit()
                    return True
            except Exception as e:
                session.rollback()
                _handle_db_exception(e)
            finally:
                session.close()
        return False
