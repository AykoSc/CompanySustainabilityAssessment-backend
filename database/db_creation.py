"""
Initializes the database with the given data scheme (as can also be seen in the ER model).
Uses SQLAlchemy and creates the database accordingly.
"""


from datetime import date

from sqlalchemy import create_engine, ForeignKey, Engine, event, CheckConstraint
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column

CASCADE_ALL_DELETE = "all, delete"
CONSTRAINT_NOT_EMPTY_STRING = "<> ''"


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def build_db_and_create_engine(db_path: str) -> Engine:
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)

    return engine


class Base(DeclarativeBase):
    pass


class Company(Base):
    __tablename__ = "Company"
    name: Mapped[str] = mapped_column(primary_key=True, index=True)

    synonyms: Mapped["Synonym"] = relationship(cascade=CASCADE_ALL_DELETE)
    news: Mapped["Contains"] = relationship(cascade=CASCADE_ALL_DELETE)

    __table_args__ = (
        CheckConstraint(f"name {CONSTRAINT_NOT_EMPTY_STRING}"),
    )


class Synonym(Base):
    __tablename__ = "Synonym"
    company_name: Mapped[str] = mapped_column(ForeignKey("Company.name", ondelete="CASCADE"), primary_key=True)
    name: Mapped[str] = mapped_column(primary_key=True, index=True)

    __table_args__ = (
        CheckConstraint(f"name {CONSTRAINT_NOT_EMPTY_STRING}"),
    )


class News(Base):
    __tablename__ = "News"
    news_ID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(unique=True, nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    link: Mapped[str] = mapped_column(nullable=False)
    sentiment: Mapped[float] = mapped_column(nullable=False)
    relevancy_score: Mapped[float] = mapped_column(nullable=False)
    date: Mapped[date]

    indicators: Mapped["NewsIndicator"] = relationship(cascade=CASCADE_ALL_DELETE)
    companies: Mapped["Contains"] = relationship(cascade=CASCADE_ALL_DELETE)

    __table_args__ = (
        CheckConstraint(f"title {CONSTRAINT_NOT_EMPTY_STRING}"),
        CheckConstraint(f"text {CONSTRAINT_NOT_EMPTY_STRING}"),
        CheckConstraint(f"link {CONSTRAINT_NOT_EMPTY_STRING}")
    )


class SustainabilityIndicator(Base):
    __tablename__ = "Sustainability_indicator"
    name: Mapped[str] = mapped_column(primary_key=True, index=True)

    news_indicators: Mapped["NewsIndicator"] = relationship(cascade=CASCADE_ALL_DELETE)

    __table_args__ = (
        CheckConstraint(f"name {CONSTRAINT_NOT_EMPTY_STRING}"),
    )


class NewsIndicator(Base):
    __tablename__ = "News_indicator"

    news_ID: Mapped[int] = mapped_column(ForeignKey("News.news_ID", ondelete="CASCADE"), primary_key=True)
    sustainability_indicator_name: Mapped[str] = \
        mapped_column(ForeignKey("Sustainability_indicator.name", ondelete="CASCADE"), primary_key=True)
    probability: Mapped[float] = mapped_column(nullable=False)


class Contains(Base):
    __tablename__ = "contains"
    news_ID: Mapped[int] = mapped_column(ForeignKey("News.news_ID", ondelete="CASCADE"), primary_key=True)
    company_name: Mapped[str] = mapped_column(ForeignKey("Company.name", ondelete="CASCADE"), primary_key=True)
