from datetime import date

from sqlalchemy.orm import Session
from . import models


def get_cases(db: Session, start_date: date):
    return db.query(models.Cases).filter(models.Cases.date > start_date).all()