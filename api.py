from datetime import date, timedelta
from functools import wraps
from multiprocessing import freeze_support
from typing import List, Type, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database.news_analysis_DAO import NewsAnalysisDAO
from logger import logger

app = FastAPI()
dao = NewsAnalysisDAO()

# Allow CORS for all origins (e.g., http://localhost:5173), all HTTP methods, and all headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

date_ranges = {
    "Heute": date.today(),
    "Diese Woche": date.today() - timedelta(days=7),
    "Dieser Monat": date.today() - timedelta(days=30),
    "Dieses Jahr": date.today() - timedelta(days=365),
    "Insgesamt": date.min
}

all_get_params = {
    "company_name",
    "synonym_name",
    "date_range",
    "indicator_name"
}


class Company(BaseModel):
    name: str


class Synonym(BaseModel):
    company_name: str
    name: str


class News(BaseModel):
    news_ID: int
    text: str
    title: str
    link: str
    sentiment: float
    date: date

    class Config:
        from_attributes = True


class SustainabilityIndicator(BaseModel):
    name: str

    class Config:
        from_attributes = True


class NewsIndicator(BaseModel):
    news_ID: int
    sustainability_indicator_name: str
    probability: float

    class Config:
        from_attributes = True


class IndicatorStats(BaseModel):
    indicator_name: str
    indicator_min: float
    indicator_avg: float
    indicator_max: float


def _valid_params(**kwargs) -> dict[str, str]:
    params = {}

    for param_name, param_value in kwargs.items():
        if param_name not in all_get_params:
            raise ValueError("Angegebener Parameter ist nicht gültig.")

        if param_value is None or param_value == "":
            error_message = "Wert nicht angegeben."
            if param_name == "company_name":
                error_message = "Unternehmen nicht angegeben."
            elif param_name == "synonym_name":
                error_message = "Synonym nicht angegeben."
            elif param_name == "date_range":
                error_message = "Zeitraum nicht angegeben."
            elif param_name == "indicator_name":
                error_message = "Indikator nicht angegeben."
            raise HTTPException(status_code=400, detail=error_message)

        params[param_name] = param_value
    return params


def does_exist(**kwargs):
    """
    Checks whether the input(-s) are valid and exist in the database.
    """
    params = _valid_params(**kwargs)

    exception = None
    if ("company_name" in params and params["company_name"] not in
            [company.name for company in dao.get_all_companies()]):
        exception = "Ungültiges Unternehmen."
    elif "company_name" not in params and "synonym_name" in params:
        exception = "Ungültiges Unternehmen für das angegebene Synonym."
    elif ("company_name" in params and "synonym_name" in params and params["synonym_name"] not in
          [synonym.name for synonym in dao.get_synonyms_by_company(params["company_name"])]):
        exception = "Ungültiges Synonym für das angegebene Unternehmen."
    elif "date_range" in params and params["date_range"] not in date_ranges:
        exception = "Ungültiger Zeitraum."
    elif ("indicator_name" in params and params["indicator_name"] not in
          [indicator.name for indicator in dao.get_all_sustainability_indicators()]):
        exception = "Ungültiger Indikator."
    elif "max_sentiment" in params:
        try:
            if 0 < float(params["max_sentiment"]) > 10:
                exception = "Ungültiges Sentiment."
        except ValueError:
            exception = "Ungültiges Sentiment."

    if exception:
        raise HTTPException(status_code=404, detail=exception)


def company_does_not_exist(company_name: str):
    if company_name and company_name in [company.name for company in dao.get_all_companies()]:
        raise HTTPException(status_code=409, detail="Unternehmen existiert bereits.")


def synonym_does_not_exist(company_name: str, synonym_name: str):
    if company_name and synonym_name and synonym_name in [synonym.name for synonym in
                                                          dao.get_synonyms_by_company(company_name)]:
        raise HTTPException(status_code=409, detail="Synonym existiert bereits für das angegebene Unternehmen.")


def none_to_error(func):
    """
    If the database returns None (aka no results), the API sends an HTTP exception with 404 code and an explanation
    instead.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if result is None:
            raise HTTPException(status_code=404, detail="Zu diesen Kriterien konnte kein Ergebnis gefunden werden.")
        return result

    return wrapper


@app.get("/companies", response_model=List[Company])
def get_companies() -> list[Type[Company]]:
    return dao.get_all_companies()


@app.get("/do_news_exist", response_model=bool)
def do_news_exist(company_name: str, date_range: str, max_sentiment: float, indicator_name: str | None = None) -> bool:
    does_exist(company_name=company_name, date_range=date_range)
    if not indicator_name:
        return dao.do_news_exist_by_company_and_date_range(company_name, date_ranges[date_range], max_sentiment)
    return dao.do_news_exist_by_company_indicator_and_date_range(company_name, date_ranges[date_range], indicator_name,
                                                                 max_sentiment)


@app.get("/news_minimum", response_model=Optional[News])
def get_news_with_lowest_sentiment(company_name: str, date_range: str, indicator_name: str | None = None) \
        -> Type[News] | None:
    does_exist(company_name=company_name, date_range=date_range)
    if not indicator_name:
        return dao.get_news_with_lowest_sentiment_by_company_and_date_range(company_name, date_ranges[date_range])
    does_exist(indicator_name=indicator_name)
    return dao.get_news_with_lowest_sentiment_by_company_indicator_and_date_range(company_name, indicator_name,
                                                                                  date_ranges[date_range])


@app.get("/news", response_model=List[News])
def get_news(company_name: str, date_range: str, max_sentiment: float, indicator_name: str | None = None) \
        -> list[Type[News]]:
    does_exist(company_name=company_name, date_range=date_range)
    if not indicator_name:
        return dao.get_news_by_company_and_date_range(company_name, max_sentiment, date_ranges[date_range])
    does_exist(indicator_name=indicator_name)
    return dao.get_news_by_company_indicator_and_date_range(company_name, indicator_name, max_sentiment,
                                                            date_ranges[date_range])


@app.get("/sustainability_indicators", response_model=List[SustainabilityIndicator])
def get_sustainability_indicators() -> list[Type[SustainabilityIndicator]]:
    return dao.get_all_sustainability_indicators()


@app.get("/indicator_stats", response_model=List[IndicatorStats])
@none_to_error
def get_indicator_stats(company_name: str, date_range: str, max_sentiment: float, indicator_name: str | None = None) \
        -> list[IndicatorStats]:
    does_exist(company_name=company_name, date_range=date_range)
    response_data = []

    if not indicator_name or indicator_name == "":
        indicators = dao.get_all_sustainability_indicators()
        for indicator in indicators:
            sentiment_stats = dao.get_sentiment_stats_by_company_indicator_and_date_range(company_name, max_sentiment,
                                                                                          indicator.name,
                                                                                          date_ranges[date_range])
            if sentiment_stats[0] and sentiment_stats[1] and sentiment_stats[2]:
                response_data.append(IndicatorStats(
                    indicator_name=indicator.name,
                    indicator_min=sentiment_stats[0],
                    indicator_avg=sentiment_stats[1],
                    indicator_max=sentiment_stats[2]
                ))
    else:
        does_exist(indicator_name=indicator_name)
        sentiment_stats = dao.get_sentiment_stats_by_company_indicator_and_date_range(company_name, max_sentiment,
                                                                                      indicator_name,
                                                                                      date_ranges[date_range])
        if sentiment_stats[0] and sentiment_stats[1] and sentiment_stats[2]:
            response_data.append(IndicatorStats(
                indicator_name=indicator_name,
                indicator_min=sentiment_stats[0],
                indicator_avg=sentiment_stats[1],
                indicator_max=sentiment_stats[2]
            ))

    return response_data


@app.post("/companies")
def create_company(company_name: str) -> bool:
    company_does_not_exist(company_name)
    company = dao.create_company(name=company_name)
    if not company:
        raise HTTPException(status_code=404, detail="Serverfehler: Unternehmen konnte nicht erstellt werden.")
    return True


@app.post("/synonyms")
def create_synonym(company_name: str, synonym_name: str) -> bool:
    does_exist(company_name=company_name)
    synonym_does_not_exist(company_name, synonym_name)
    synonym = dao.create_synonym(company_name=company_name, name=synonym_name)
    if not synonym:
        raise HTTPException(status_code=404,
                            detail="Serverfehler: Synonym konnte nicht erstellt werden für das angegebene Unternehmen.")
    return True


@app.delete("/companies")
def delete_company(company_name: str) -> bool:
    does_exist(company_name=company_name)
    deleted = dao.delete_company(company_name)
    if not deleted:
        raise HTTPException(status_code=404, detail="Serverfehler: Unternehmen konnte nicht gelöscht werden.")
    return True


@app.delete("/synonyms")
def delete_synonym(company_name: str, synonym_name: str) -> bool:
    does_exist(company_name=company_name, synonym_name=synonym_name)
    deleted = dao.delete_synonym(company_name, synonym_name)
    if not deleted:
        raise HTTPException(status_code=404,
                            detail="Serverfehler: Synonym konnte nicht gelöscht werden für das angegebene Unternehmen.")
    return True


def start_api():
    freeze_support()  # freeze_support() needs to be called before starting the server
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
    logger.info("API gestartet.")


if __name__ == "__main__":
    start_api()
