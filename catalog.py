from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from scripts.database_setup import Base, User, Category, Item

import sqlalchemy
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

# Connect to Database and create database session
engine = sqlalchemy.create_engine('sqlite:///data/catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def showHome():
    categories = session.query(Category).order_by(sqlalchemy.asc(Category.name)).all()
    return render_template('home.html', categories=categories)

@app.route('/category/<int:category_id>')
def showCategory(category_id):
    categories = session.query(Category).order_by(sqlalchemy.asc(Category.name)).all()
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(Item).filter_by(category_id = category_id).all()
    return render_template('category.html', categories=categories, category=category, items=items)

if __name__ == '__main__':
    app.secret_key = 'my_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5001)
