"""SQLAlchemy 모델."""
from __future__ import annotations

from sqlalchemy import Date, Numeric, SmallInteger, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class LivingPopulationDong(Base):
    """생활인구(행정동 단위). 연령·성별 세부 항목은 raw에 원본 그대로 보존한다."""

    __tablename__ = "living_population_dong"

    stdr_de_id: Mapped[Date] = mapped_column(Date, primary_key=True)
    tmzon_pd_se: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    adstrd_code_se: Mapped[str] = mapped_column(String(8), primary_key=True)
    tot_lvpop_co: Mapped[float] = mapped_column(Numeric)
    raw: Mapped[dict] = mapped_column(JSONB)
