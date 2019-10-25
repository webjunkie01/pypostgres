from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    mapper,
    relation,
    backref,
    synonym,
    column_property,
    relationship,
)
from time import sleep
from sqlalchemy.sql import select, insert
from sqlalchemy.ext.automap import automap_base
import random

db_url = "postgresql://food_user:pac4life@localhost/fast_food_db"
engine = create_engine(db_url, echo=True)
metadata = MetaData(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal.configure(bind=engine)
Base = automap_base()


class Order(Base):
    __tablename__ = "orders"


Base.prepare(engine, reflect=True)

db = SessionLocal()
products = [
    "French Fries",
    "Hamburguer",
    "Nachos",
    "Soda",
    "Milkshake",
    "Burrito",
    "Hot Dog",
    "Salad",
]
qty = [1, 2, 3, 4, 5, 6, 7, 8, 9, 12]
for num in range(1, 200):
    order = Order()
    order.name = random.choice(products)
    order.price = random.choice(qty) * num
    order.quantity = random.choice(qty)
    db.add(order)
    db.commit()
    sleep(20)
