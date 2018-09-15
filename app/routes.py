import pickle
import json
import os
import threading
from threading import Thread
from datetime import datetime, timedelta
from base64 import b64encode
from uuid import uuid4
from config import Config
from operator import attrgetter
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, desc
from flask import render_template, flash, redirect, url_for, request, Flask
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.exceptions import HTTPException
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)

@app.before_first_request
def create_database():
    db.create_all()
    db.session.commit()

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/') 
@app.route('/index', methods=['GET', 'POST'])
def index():    
    return render_template("index.html", title='Home Page')
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
       return render_template('login.html', title='Access Wallet')
    if request.method == "POST":
        #gets the private key to be derived
       return request.form['privateKey']


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username, current_user.email)
    if request.method == 'POST':
        if form.validate_on_submit():   
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Your changes have been saved.')
            return redirect(url_for('edit_profile'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/marketplace')
def marketplace():
    #get items through database or something
    items = [
        {'item_name': 'Rice',
        'price': '20',
        'quantity': '50',
        'seller_address':'0xf67a6388F62aD660505cDd63e0558CF1f68c0d9a'},
        {'item_name': 'Wheat',
        'price': '30',
        'quantity': '40',
        'seller_address':'0x4158d0DE0DAAF01FA022DB154183361CC9d2923A'},
        {'item_name': 'Mango',
        'price': '10',
        'quantity': '10',
        'seller_address':'0xDE73bf7Bc4D099A166B7b8711E3Daa80B4458B5c'}]
    return render_template('marketplace.html', items=items)
