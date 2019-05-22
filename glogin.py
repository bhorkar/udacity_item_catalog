import json

import httplib2
import requests
from flask import request, redirect, url_for, flash, make_response, jsonify
from flask import session as login_session
from oauth2client.client import AccessTokenCredentials
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets
import database_interaction
from db_setup import * 

class Google_connect():
    '''Class that handles login through google account.'''
    db = database_interaction.Database_interaction()
   # output = prefabs.login_output.Login_output()
    CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web'][
        'client_id']

    def __init__(self):
        pass


    #for the new google auth process.
    def authorize_google(self,auth_code):
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
        session = self.db.session
        user = session.query(User).filter_by(email=email).first()
        if not user:
            user = User(username=name, picture=picture, email=email)
            session.add(user)
            session.commit()
        session.close()


        login_session['email'] = user.email
        login_session['username'] = user.username
        login_session['user_id'] = user.id
        login_session['picture'] = user.picture
        login_session['provider'] = 'google'
        flash("you are now logged in as %s" % login_session['username'], 'success')

        return make_response('success', 200)
    def disconnect(self):
        if 'provider' in login_session:
            if login_session['provider'] == 'google':
                self.gdisconnect()
                if 'credentials' in login_session:
                    del login_session['credentials']
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
            flash("You were not logged in")
            return redirect(url_for('showCatalog'))

    def gdisconnect(self):
        # only disconnect a connected user
        credentials = login_session.get('credentials')
        if credentials is None:
            response = make_response(
                json.dumps('Current user not connected.'), 401)
            response.headers['Content-type'] = 'application/json'
            return response
        # execute HTTP GET request to revoke current token
        access_token = credentials.access_token
        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token  # noqa
        h = httplib2.Http()
        result = h.request(url, 'GET')[0]

        if result['status'] == '200':
            # reset the user's session
            del login_session['credentials']
            del login_session['gplus_id']
            del login_session['username']
            del login_session['email']
            del login_session['picture']

            response = make_response(json.dumps('Successfully disconnected.'), 200)
            response.headers['Content-Type'] = 'application/json'
            return response

        else:
            # token given is invalid
            response = make_response(
                json.dumps('Failed to revoke token for given user.'), 400)
            response.headers['Content-Type'] = 'application/json'
            return response

