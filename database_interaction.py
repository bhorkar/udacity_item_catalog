# -*- coding: utf-8 -*-
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import *


class Database_interaction:
    '''This module manages all connections with database.'''

    engine = create_engine(
        'sqlite:///ItemCatalog.db',
        connect_args={
            'check_same_thread': False})
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    def query_user_by_id(self, id):
        # Return user with given id from database.
        return self.session.query(User) \
            .filter_by(id=id) \
            .one()

    def create_user(self, login_session):
        # Try to create a new user.

        # Check if email already exists in DB.
        existing_user = self.get_user_id(login_session['email'])

        if existing_user:
            # If email exists, do not save new one.
            print (u'Current user already registered!')
            return existing_user

        # If email does not exist, save a new user.
        new_user = User(name=login_session['username'],
                        email=login_session['email'],
                        picture=login_session['picture'])
        self.session.add(new_user)
        self.session.commit()
        return self.get_user_id(login_session['email'])
    # backend codes with Users

    def createUser(login_session):
        newUser = User(
            username=login_session['username'],
            email=login_session['email'])
        session.add(newUser)
        session.commit()

        user = session.query(User).filter_by(
            email=login_session['email']).one()
        return user.id

    def getUserInfo(user_id):

        user = session.query(User).filter_by(id=user_id).one_or_none()
        print(user)
        return user

    def getUserID(email):

        try:
            user = session.query(User).filter_by(email=email).one()
            return user.id
        except BaseException:
            return None

    def query_items(self):
        return self.session.query(Item)

    def query_category(self):
        return self.session.query(Category)
