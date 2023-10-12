from sqlalchemy import Column, Date, Integer, TIMESTAMP, ForeignKey
from databases.database import Base


class Coil(Base):
    __tablename__ = 'coils_test'
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    length = Column(Integer, index=True, nullable=False)
    weight = Column(Integer, index=True, nullable=False)
    add_date = Column(Date, index=True, nullable=False)
    delete_date = Column(Date, default=None, index=True, nullable=True)




