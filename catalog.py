#!usr/bin/env python3

import json
import os
import random
import string
from urllib.parse import urlencode

import httplib2
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
from flask import Flask, render_template, request, redirect, \
    jsonify, url_for, flash, make_response

from scripts.database_setup import Base, User, Category, Item


app = Flask(__name__)

# Connect to Database and create database session
here = os.path.dirname(__file__)
db_config_file = os.path.join(here, 'config', 'database.json')
db_url = json.loads(open(db_config_file, 'r').read())['url']
# engine = sqlalchemy.create_engine(db_url, connect_args={'check_same_thread': False})
engine = sqlalchemy.create_engine(db_url)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
def showHome():
    categories = session.query(Category).order_by(
        sqlalchemy.asc(Category.name)).all()
    user = getUserInfo()
    return render_template('home.html', user=user, categories=categories)


@app.route('/category/<int:category_id>')
def showCategory(category_id):
    categories = session.query(Category).order_by(
        sqlalchemy.asc(Category.name)).all()
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    user = getUserInfo()
    return render_template('category.html', user=user,
                           categories=categories,
                           category=category,
                           items=items)


@app.route('/category/<int:category_id>.json')
def showCategoryJson(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    return jsonify(category.serialize)


@app.route('/category/<int:category_id>/items.json')
def showCategoryItemsJson(category_id):
    items = session.query(Item).filter_by(category_id=category_id).all()
    # Convert list of items to an array for serialization
    itemJson = []
    for i in items:
        itemJson.append(i.serialize)
    return jsonify(itemJson)


@app.route('/category/<int:category_id>/create', methods=['GET', 'POST'])
def createItem(category_id):
    user = getUserInfo()
    # Only logged in users can create items
    if(not user):
        return make_response(
            render_template('error.html', code=401,
                            message='Please login to create items.'),
            401
        )
    if request.method == 'POST':
        category = session.query(Category).filter_by(id=category_id).one()
        # Create an item with data, category and user and show it
        item = Item()
        item.name = request.form['name']
        item.description = request.form['description']
        item.category = category
        item.user = user
        session.add(item)
        session.commit()
        flash('"%s" created succesfully!' % item.name)
        return redirect(url_for('showItem', item_id=item.id))
    else:
        # Render the create item form
        categories = session.query(Category).order_by(
            sqlalchemy.asc(Category.name)).all()
        category = session.query(Category).filter_by(id=category_id).one()
        items = session.query(Item).filter_by(category_id=category.id).all()
        return render_template('item.create.html', user=user,
                               categories=categories,
                               category=category,
                               items=items)


@app.route('/item/<int:item_id>')
def showItem(item_id):
    categories = session.query(Category).order_by(
        sqlalchemy.asc(Category.name)).all()
    item = session.query(Item).filter_by(id=item_id).one()
    category = item.category
    items = session.query(Item).filter_by(category_id=category.id).all()
    user = getUserInfo()
    return render_template('item.html', user=user,
                           categories=categories,
                           category=category,
                           items=items, item=item)


@app.route('/item/<int:item_id>.json')
def showItemJson(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(item.serialize)


@app.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(item_id):
    user = getUserInfo()
    # Only logged in users can edit items
    if(not user):
        return make_response(
            render_template('error.html', code=401,
                            message='Please login to delete items.'),
            401
        )
    # Only authors of items can edit their items
    item = session.query(Item).filter_by(id=item_id).one()
    if(user.id != item.user_id):
        return make_response(
            render_template('error.html', code=401,
                            message='You can only delete your own items.'),
            403
        )
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        session.add(item)
        session.commit()
        flash('"%s" updated succesfully!' % item.name)
        return redirect(url_for('showItem', item_id=item.id))
    else:
        categories = session.query(Category).order_by(
            sqlalchemy.asc(Category.name)).all()
        category = item.category
        items = session.query(Item).filter_by(category_id=category.id).all()
        return render_template('item.edit.html', user=user,
                               categories=categories,
                               category=category,
                               items=items,
                               item=item)


@app.route('/item/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(item_id):
    user = getUserInfo()
    # Only logged in users can delete items
    if(not user):
        return make_response(
            render_template('error.html', code=401,
                            message='Please login to delete items.'),
            401
        )
    # Only authors of items can delete their items
    item = session.query(Item).filter_by(id=item_id).one()
    if(user.id != item.user_id):
        return make_response(
            render_template('error.html', code=401,
                            message='You can only delete your own items.'),
            403
        )
    if request.method == 'POST':
        category_id = item.category_id
        session.delete(item)
        session.commit()
        flash('"%s" deleted succesfully!' % item.name)
        return redirect(url_for('showCategory', category_id=category_id))
    else:
        # Render a simple form with single button to confirm delete
        categories = session.query(Category).order_by(
            sqlalchemy.asc(Category.name)).all()
        category = item.category
        items = session.query(Item).filter_by(category_id=category.id).all()
        return render_template('item.delete.html', user=user,
                               categories=categories, category=category,
                               items=items, item=item)


@app.route('/login')
def showLogin():
    categories = session.query(Category).order_by(
        sqlalchemy.asc(Category.name)).all()

    # Generate a random string to use as an unguessable "state"
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state

    here = os.path.dirname(__file__)
    gh_config_file = os.path.join(here, 'config', 'github_secrets.json')
    app_id = json.loads(open(gh_config_file,
                             'r').read())['web']['app_id']

    # Create Github Oauth API URL, see:
    # https://developer.github.com/apps/building-oauth-apps/authorizing-oauth-apps/#1-request-a-users-github-identity
    github_authorize_url = 'https://github.com/login/oauth/authorize?' + \
        urlencode({
            'client_id': app_id,
            'state': state,
            'scope': 'user',
            'redirect_uri': 'http://localhost:5001/github-callback'
        })
    return render_template('login.html', user=getUserInfo(),
                           github_authorize_url=github_authorize_url,
                           categories=categories)


@app.route('/logout')
def logout():
    access_token = login_session['github_access_token']
    here = os.path.dirname(__file__)
    gh_config_file = os.path.join(here, 'config', 'github_secrets.json')
    app_id = json.loads(open(gh_config_file,
                             'r').read())['web']['app_id']
    app_secret = json.loads(
        open(gh_config_file, 'r').read())['web']['app_secret']

    # Revoke a session token, see:
    # https://developer.github.com/v3/oauth_authorizations/#delete-an-authorization
    github_access_token_revoke_url = \
        'https://api.github.com/applications/%s/tokens/%a' % (
            app_id, access_token)
    h = httplib2.Http()
    h.add_credentials(app_id, app_secret)
    (revoke_response, revoke_content) = h.request(
        github_access_token_revoke_url,
        method='DELETE',
        headers={'Accept': 'application/json'})
    if revoke_response.get('error') is not None:
        response = make_response(
            render_template('error.html', code=500,
                            message=revoke_response.get('error')),
            500
        )
        return response
    
    # Delete all information of user on session
    del login_session['name']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['github_access_token']
    flash('You have been logged out.')
    return redirect(url_for('showHome'))


@app.route('/github-callback')
def githubCallback():
    code = request.args.get('code')
    state = request.args.get('state')
    if (request.args.get('state') != login_session['state']):
        response = make_response(
            render_template('error.html', code=401,
                            message='Invalid state parameter.'),
            401
        )
        return response

    # Request long term access token from Github Oauth API:
    # https://developer.github.com/apps/building-oauth-apps/authorizing-oauth-apps/#2-users-are-redirected-back-to-your-site-by-github
    here = os.path.dirname(__file__)
    gh_config_file = os.path.join(here, 'config', 'github_secrets.json')
    app_id = json.loads(open(gh_config_file,
                             'r').read())['web']['app_id']
    app_secret = json.loads(
        open(gh_config_file, 'r').read())['web']['app_secret']

    github_access_token_url = \
        'https://github.com/login/oauth/access_token?' + urlencode({
            'client_id': app_id,
            'client_secret': app_secret,
            'code': code,
            'redirect_uri': 'http://localhost:5001/github-callback',
            'state': state
        })
    h = httplib2.Http()

    (token_response, token_content) = h.request(
        github_access_token_url,
        method='POST',
        headers={'Accept': 'application/json'})
    if token_response.get('error') is not None:
        response = make_response(
            render_template('error.html', code=500,
                            message=token_response.get('error')),
            500
        )
        return response
    if 'access_token' not in json.loads(token_content):
        response = make_response(
            render_template(
                'error.html',
                code=401,
                message='Cannot connect to github, please try again later.'),
            401
        )
        return response

    login_session['github_access_token'] = json.loads(token_content)[
        'access_token']

    # Request user information from Oauth API
    # https://developer.github.com/apps/building-oauth-apps/authorizing-oauth-apps/#3-use-the-access-token-to-access-the-api
    github_api_url = 'https://api.github.com/user'
    auth_header = 'token ' + login_session['github_access_token']
    (user_response, user_content) = h.request(
        github_api_url,
        method='GET',
        headers={'Accept': 'application/json', 'Authorization': auth_header})
    user_result = json.loads(user_content)

    # If user has no visible email in their profile, authentication can't work
    if user_result['email'] is None:
        response = make_response(
            render_template(
                'error.html',
                code=401,
                message='Cannot get your email from Github, \
                    your email must be visible in your Github account.'),
            401
        )
        return response

    # Finally user is valid!
    login_session['name'] = user_result['name']
    login_session['email'] = user_result['email']
    login_session['picture'] = user_result['avatar_url']

    user_id = getUserID(user_result['email'])
    if not user_id:
        user_id = createUser(login_session)
        login_session['user_id'] = user_id
        flash('Welcome %s! First time!' % login_session['name'])
    else:
        login_session['user_id'] = user_id
        flash('Welcome back "%s"!' % login_session['name'])
    return redirect(url_for('showHome'))


def createUser(login_session):
    '''Creates a new user in database and returns its new id'''
    newUser = User(
        name=login_session['name'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo():
    '''Gets information from database of currently logged in user'''
    try:
        user_id = login_session['user_id']
        user = session.query(User).filter_by(id=user_id).one()
        return user
    except:
        return None


def getUserID(email):
    '''Gets user id by email'''
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def main():
    app.secret_key = 'my_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5001)


if __name__ == '__main__':
    try:
        main()
    finally:
        session.close()
        engine.dispose()
        print("session and db engine removed.")
