import datetime

from pydantic import BaseModel


class CasesBase(BaseModel):
    date: datetime.date
    positive_tests: int
    tests: int
    rolling_average: float
    positive_rate: float


class Cases(CasesBase):
    class Config:
        orm_mode = True
