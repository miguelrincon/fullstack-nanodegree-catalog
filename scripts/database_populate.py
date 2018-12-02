from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Item, Category, User


engine = create_engine('sqlite:///data/catalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def create_entry(entry):
    session.add(entry)
    session.commit()

category1 = Category(name='Sports')
create_entry(category1)

item1 = Item(name='Snowboard', description="The Snowboard that flies.", category=category1)
item2 = Item(name='Bowling Ball', description="A weightless bowling ball.", category=category1)
item3 = Item(name='Puck', description="Puck for the hockey fans.", category=category1)
item4 = Item(name='Running Shorts', description="Shorts that can run for you.", category=category1)

create_entry(item1)
create_entry(item2)
create_entry(item3)
create_entry(item4)

category2 = Category(name='Food')
create_entry(category2)

item5 = Item(name='A Cookie', description="The most chocolatastic cookie. Only one.", category=category2)
create_entry(item5)
