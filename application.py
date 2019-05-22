from functools import wraps
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash  # noqa
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from db_setup import Base, CatalogItem, Category, User
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///ItemCatalog.db',connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in login_session:
            return redirect(url_for('showLogin'))
        return f(*args, **kwargs)
    return decorated_function


# --------------------------------------
# JSON APIs to show Catalog information
# --------------------------------------
@app.route('/api/v1/catalog.json')
def showCatalogJSON():
    """Returns JSON of all items in catalog"""
    items = session.query(CatalogItem).order_by(CatalogItem.id.desc())
    return jsonify(CatalogItems=[i.serialize for i in items])


@app.route(
    '/api/v1/categories/<int:category_id>/item/<int:catalog_item_id>/JSON')
def catalogItemJSON(category_id, catalog_item_id):
    """Returns JSON of selected item in catalog"""
    Catalog_Item = session.query(
        CatalogItem).filter_by(id=catalog_item_id).one()
    return jsonify(Catalog_Item=Catalog_Item.serialize)


@app.route('/api/v1/categories/JSON')
def categoriesJSON():
    """Returns JSON of all categories in catalog"""
    categories = session.query(Category).all()
    return jsonify(Categories=[r.serialize for r in categories])


# --------------------------------------
# CRUD for categories
# --------------------------------------
# READ - home page, show latest items and categories
@app.route('/')
@app.route('/categories/')
def showCatalog():
    """Returns catalog page with all categories and recently added items"""
    categories = session.query(Category).all()
    items = session.query(CatalogItem).order_by(CatalogItem.id.desc())
    quantity = items.count()
    if 'username' not in login_session:
        return render_template(
            'public_catalog.html',
            categories=categories, items=items, quantity=quantity)
    else:
        return render_template(
            'catalog.html',
            categories=categories, items=items, quantity=quantity)


# CREATE - New category
@app.route('/categories/new', methods=['GET', 'POST'])
@login_required
def newCategory():
    """Allows user to create new category"""
    if request.method == 'POST':
        print login_session
        if 'user_id' not in login_session and 'email' in login_session:
            login_session['user_id'] = getUserID(login_session['email'])
        newCategory = Category(
            name=request.form['name'],
            user_id=login_session['user_id'])
        session.add(newCategory)
        session.commit()
        flash("New category created!", 'success')
        return redirect(url_for('showCatalog'))
    else:
        return render_template('new_category.html')


# EDIT a category
@app.route('/categories/<int:category_id>/edit/', methods=['GET', 'POST'])
@login_required
def editCategory(category_id):
    """Allows user to edit an existing category"""
    editedCategory = session.query(
        Category).filter_by(id=category_id).one()
    if editedCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized!')}</script><body onload='myFunction()'>"  # noqa
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            flash(
                'Category Successfully Edited %s' % editedCategory.name,
                'success')
            return redirect(url_for('showCatalog'))
    else:
        return render_template(
            'edit_category.html', category=editedCategory)


# DELETE a category
@app.route('/categories/<int:category_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_id):
    """Allows user to delete an existing category"""
    categoryToDelete = session.query(
        Category).filter_by(id=category_id).one()
    if categoryToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized!')}</script><body onload='myFunction()'>"  # noqa
    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.name, 'success')
        session.commit()
        return redirect(
            url_for('showCatalog', category_id=category_id))
    else:
        return render_template(
            'delete_category.html', category=categoryToDelete)


# --------------------------------------
# CRUD for category items
# --------------------------------------
# READ - show category items
@app.route('/categories/<int:category_id>/')
@app.route('/categories/<int:category_id>/items/')
def showCategoryItems(category_id):
    """returns items in category"""
    category = session.query(Category).filter_by(id=category_id).one()
    categories = session.query(Category).all()
    creator = getUserInfo(category.user_id)
    items = session.query(
        CatalogItem).filter_by(
            category_id=category_id).order_by(CatalogItem.id.desc())
    quantity = items.count()
    return render_template(
        'catalog_menu.html',
        categories=categories,
        category=category,
        items=items,
        quantity=quantity,
        creator=creator)


# READ ITEM - selecting specific item show specific information about that item
@app.route('/categories/<int:category_id>/item/<int:catalog_item_id>/')
def showCatalogItem(category_id, catalog_item_id):
    """returns category item"""
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(
        CatalogItem).filter_by(id=catalog_item_id).one()
    creator = getUserInfo(category.user_id)
    return render_template(
        'catalog_menu_item.html',
        category=category, item=item, creator=creator)


# CREATE ITEM
@app.route('/categories/item/new', methods=['GET', 'POST'])
@login_required
def newCatalogItem():
    """return "This page will be for making a new catalog item" """
    categories = session.query(Category).all()
    if request.method == 'POST':
        addNewItem = CatalogItem(
            name=request.form['name'],
            description=request.form['description'],
            category_id=request.form['category'],
            user_id=login_session['user_id'])
        session.add(addNewItem)
        session.commit()
        flash("New catalog item created!", 'success')
        return redirect(url_for('showCatalog'))
    else:
        return render_template('new_catalog_item.html', categories=categories)


# UPDATE ITEM
@app.route(
    '/categories/<int:category_id>/item/<int:catalog_item_id>/edit',
    methods=['GET', 'POST'])
@login_required
def editCatalogItem(category_id, catalog_item_id):
    """return "This page will be for making a updating catalog item" """
    editedItem = session.query(
        CatalogItem).filter_by(id=catalog_item_id).one()
    if editedItem.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized!')}</script><body onload='myFunction()'>"  # noqa
    if request.method == 'POST':
        print (request.form)
        print (editedItem)
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category']:
            editedItem.category = request.form['category']
            print request.form['category']
        session.add(editedItem)
        session.commit()
        flash("Catalog item updated!", 'success')
        return redirect(url_for('showCatalog'))
    else:
        categories = session.query(Category).all()
        return render_template(
            'edit_catalog_item.html',
            categories=categories,
            item=editedItem)


# DELETE ITEM
@app.route(
    '/categories/<int:category_id>/item/<int:catalog_item_id>/delete',
    methods=['GET', 'POST'])
@login_required
def deleteCatalogItem(category_id, catalog_item_id):
    """return "This page will be for deleting a catalog item" """
    itemToDelete = session.query(
        CatalogItem).filter_by(id=catalog_item_id).one()
    if itemToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized!')}</script><body onload='myFunction()'>"  # noqa
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Catalog Item Successfully Deleted', 'success')
        return redirect(url_for('showCatalog'))
    else:
        return render_template(
            'delete_catalog_item.html', item=itemToDelete)


# --------------------------------------
# Login Handling
# --------------------------------------

# Login route, create anit-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(
            string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    print ("showing login page")
    return render_template('login_user.html', STATE=state)




# CONNECT - Google login get token
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if not create new user
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '  # noqa
    flash("you are now logged in as %s" % login_session['username'], 'success')
    print "done!"
    return output



# User helper functions
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def createUser(login_session):
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    print login_session
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            if 'gplus_id' in login_session:
                del login_session['gplus_id']
            if 'credentials' in login_session:
                del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        if 'username' in login_session:
            del login_session['username']
        if 'email' in login_session:
            del login_session['email']
        if 'picture' in login_session:
            del login_session['picture']
        if 'user_id' in login_session:
            del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.", 'success')
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in", 'danger')
        return redirect(url_for('showCatalog'))






@app.route('/logout')

def logout_user():

    login_session.clear()

    return redirect(url_for('login_user'))





@app.route('/login/<provider>', methods=['POST'])

def login_process(provider):

    if provider == 'google':

        token = request.data

        return authorize_google(token)



    return abort(404)





def authorize_google(auth_code):

    """authorize google sign in"""

    try:

        # Upgrade the authorization code into a credentials object

        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')

        oauth_flow.redirect_uri = 'postmessage'

        credentials = oauth_flow.step2_exchange(auth_code)

    except FlowExchangeError as ex:

        response = make_response(

            json.dumps('Failed to upgrade the authorization code.'), 401)

        response.headers['Content-Type'] = 'application/json'

        return response



    # Check that the access token is valid.

    access_token = credentials.access_token

    url = (

        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %

        access_token)

    h = httplib2.Http()

    result = json.loads(h.request(url, 'GET')[1])



    # If there was an error in the access token info, abort.

    if result.get('error') is not None:

        response = make_response(json.dumps(result.get('error')), 500)

        response.headers['Content-Type'] = 'application/json'

        return response



    # # Verify that the access token is used for the intended user.

    # gplus_id = credentials.id_token['sub']

    # if result['user_id'] != gplus_id:

    #     response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)

    #     response.headers['Content-Type'] = 'application/json'

    #     return response



    # # Verify that the access token is valid for this app.

    # if result['issued_to'] != CLIENT_ID:

    #     response = make_response(json.dumps("Token's client ID does not match app's."), 401)

    #     response.headers['Content-Type'] = 'application/json'

    #     return response



    # stored_credentials = login_session.get('credentials')

    # stored_gplus_id = login_session.get('gplus_id')

    # if stored_credentials is not None and gplus_id == stored_gplus_id:

    #     response = make_response(json.dumps('Current user is already connected.'), 200)

    #     response.headers['Content-Type'] = 'application/json'

    #     return response



    # Get user info

    h = httplib2.Http()

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"

    params = {'access_token': credentials.access_token, 'alt': 'json'}

    answer = requests.get(userinfo_url, params=params)



    data = answer.json()



    name = data['name']

    picture = data['picture']

    print (picture)

    email = data['email']



    # see if user exists, if it doesn't make a new one

    session = DBSession()

    user = session.query(User).filter_by(email=email).first()

    if not user:

        user = User(username=name, picture=picture, email=email)

        session.add(user)

        session.commit()

    session.close()



    login_session['email'] = user.email

    login_session['username'] = user.username

    login_session['user_id'] = user.id
    login_session['provider'] = 'google' 



    return make_response('success', 200)




if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
