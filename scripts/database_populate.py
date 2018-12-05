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

userA = User(name='Alexander Z', email='usera@example.com', picture='/static/user.jpeg')
userB = User(name='Bernard X', email='userb@example.com', picture='/static/user.jpeg')

category1 = Category(name='Sports')
create_entry(category1)

item1 = Item(name='Snowboard', description="The Snowboard that flies.", category=category1, user=userA)
item2 = Item(name='Bowling Ball', description="A weightless bowling ball.", category=category1, user=userB)
item3 = Item(name='Puck', description="Puck for the hockey fans.", category=category1)
item4 = Item(name='Running Shorts', description="Shorts that can run for you.", category=category1, user=userB)

create_entry(item1)
create_entry(item2)
create_entry(item3)
create_entry(item4)

category2 = Category(name='Food')
create_entry(category2)

item5 = Item(name='A Cookie', description="The most chocolatastic cookie. Only one.", category=category2, user=userA)
create_entry(item5)

item6 = Item(name='Some chips', description="Also known as french fries.", category=category2)
create_entry(item6)


category3 = Category(name='Electronics')
create_entry(category3)

item7 = Item(name='Roomba', description="It cleans for you.", category=category3, user=userA)
create_entry(item7)
item8 = Item(name='Smart speaker X', description="Speaker that's smarter than you.", category=category3)
create_entry(item8)


session.close()
engine.dispose()
