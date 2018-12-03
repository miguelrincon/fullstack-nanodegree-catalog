from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from scripts.database_setup import Base, User, Category, Item

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from flask import session as login_session

import json
import random
import string
import urllib.parse

app = Flask(__name__)

# Connect to Database and create database session
engine = sqlalchemy.create_engine('sqlite:///data/catalog.db', connect_args={'check_same_thread': False})
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

@app.route('/category/<int:category_id>/create', methods=['GET', 'POST'])
def createItem(category_id):
    if request.method == 'POST':
        category = session.query(Category).filter_by(id = category_id).one()
        item = Item()
        item.name = request.form['name']
        item.description = request.form['description']
        item.category = category
        session.add(item)
        session.commit()
        flash('"%s" created succesfully!' % item.name)
        return redirect(url_for('showItem', item_id=item.id))
    else:
        categories = session.query(Category).order_by(sqlalchemy.asc(Category.name)).all()
        category = session.query(Category).filter_by(id = category_id).one()
        items = session.query(Item).filter_by(category_id = category.id).all()
        return render_template('item.create.html', categories=categories, category=category, items=items)

@app.route('/item/<int:item_id>')
def showItem(item_id):
    categories = session.query(Category).order_by(sqlalchemy.asc(Category.name)).all()
    item = session.query(Item).filter_by(id = item_id).one()
    category = item.category
    items = session.query(Item).filter_by(category_id = category.id).all()
    return render_template('item.html', categories=categories, category=category, items=items,item=item)

@app.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(item_id):
    if request.method == 'POST':
        item = session.query(Item).filter_by(id = item_id).one()
        item.name = request.form['name']
        item.description = request.form['description']
        session.add(item)
        session.commit()
        flash('"%s" updated succesfully!' % item.name)
        return redirect(url_for('showItem', item_id=item.id))
    else:
        categories = session.query(Category).order_by(sqlalchemy.asc(Category.name)).all()
        item = session.query(Item).filter_by(id = item_id).one()
        category = item.category
        items = session.query(Item).filter_by(category_id = category.id).all()
        return render_template('item.edit.html', categories=categories, category=category, items=items,item=item)

@app.route('/item/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(item_id):
    if request.method == 'POST':
        item = session.query(Item).filter_by(id = item_id).one()
        category_id = item.category_id
        session.delete(item)
        session.commit()
        flash('"%s" deleted succesfully!' % item.name)
        return redirect(url_for('showCategory', category_id=category_id))
    else:
        categories = session.query(Category).order_by(sqlalchemy.asc(Category.name)).all()
        item = session.query(Item).filter_by(id = item_id).one()
        category = item.category
        items = session.query(Item).filter_by(category_id = category.id).all()
        return render_template('item.delete.html', categories=categories, category=category, items=items,item=item)

@app.route('/login')
def showLogin():
    categories = session.query(Category).order_by(sqlalchemy.asc(Category.name)).all()

    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state

    app_id = json.loads(open('config/github_secrets.json', 'r').read())['web']['app_id']
    github_authorize_url = 'https://github.com/login/oauth/authorize?' + urllib.parse.urlencode({
        'client_id': app_id,
        'state': state,
        'scope': 'user',
        'redirect_uri': 'http://localhost:5001/github-callback'
    })
    return render_template('login.html', github_authorize_url=github_authorize_url, categories=categories)

@app.route('/github-callback')
def githubCallback():
    code = request.args.get('code')
    state = request.args.get('state')
    return 'Should try to login now... <br>code: %s, state: %s' % (code, state)


if __name__ == '__main__':
    app.secret_key = 'my_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5001)