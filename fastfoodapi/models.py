from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    orm,
    MetaData,
    Table,
    DateTime,
    LargeBinary,
    ForeignKey,
    Table,
    Boolean,
    func,
    String,
    BigInteger,
    Numeric,
)
from sqlalchemy.orm import relationship
from .meta import Base
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text)
    quantity = Column(Integer)
    price = Column(Numeric)
