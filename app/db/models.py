from app.db.database import Base
from sqlalchemy import Column, Date, Integer, Float


class Cases(Base):
    __tablename__ = 'cases'
    date = Column('date', Date, primary_key=True)
    positive_tests = Column('P', Integer)
    tests = Column('T', Integer)
    rolling_average = Column('Mean', Float)
    positive_rate = Column('RollingRate', Float)
    rolling_tests = Column('RollingTests', Float)

