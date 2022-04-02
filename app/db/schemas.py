import datetime

from pydantic import BaseModel


class CasesBase(BaseModel):
    date: datetime.date
    positive_tests: int
    tests: int
    rolling_average: float


class Cases(CasesBase):
    class Config:
        orm_mode = True
