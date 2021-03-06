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
       #return render_template('wallet.html', address=request.form['privateKey'], account_balance=0) 
       return wallet(request.form['privateKey'])


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
        'seller_address':'0xDE73bf7Bc4D099A166B7b8711E3Daa80B4458B5c'},
        {'item_name': 'Coconut',
        'price': '300',
        'quantity': '140',
        'seller_address':'0x4158d0DE0DAAF01FA022DB154183361CC9d2923A'},
        {'item_name': 'Banana',
        'price': '50',
        'quantity': '20',
        'seller_address':'0xDE73bf7Bc4D099A166B7b8711E3Daa80B4458B5c'},
        {'item_name': 'Wheat',
        'price': '30',
        'quantity': '40',
        'seller_address':'0x4158d0DE0DAAF01FA022DB154183361CC9d2923A'},
        {'item_name': 'Rice',
        'price': '300',
        'quantity': '700',
        'seller_address':'0xf67a6388F62aD660505cDd63e0558CF1f68c0d9a'},
        {'item_name': 'Tomato',
        'price': '20',
        'quantity': '60',
        'seller_address':'0x4158d0DE0DAAF01FA022DB154183361CC9d2923A'},
        {'item_name': 'Pig',
        'price': '2000',
        'quantity': '2',
        'seller_address':'0x4158d0DE0DAAF01FA022DB154183361CC9d2923A'},
        {'item_name': 'Cow',
        'price': '3000',
        'quantity': '2',
        'seller_address':'0x4158d0DE0DAAF01FA022DB154183361CC9d2923A'},
        {'item_name': 'Piglets',
        'price': '1800',
        'quantity': '5',
        'seller_address':'0x4158d0DE0DAAF01FA022DB154183361CC9d2923A'},
        {'item_name': 'Wheat',
        'price': '30',
        'quantity': '40',
        'seller_address':'0x4158d0DE0DAAF01FA022DB154183361CC9d2923A'},]

    return render_template('marketplace.html', items=items)

@app.route('/product/<item>')
def product(item):
    print(item)
    return render_template('product.html', item=item)

@app.route('/wallet')
def wallet(private_key):
    #derive the address by the private key
    address="0xe106213eC2Fc640Bd534d85C27E67A9A24D22c37"
    transactions = [
        {"transaction_no" : 1,
        "address_from" : address,
        "address_to" : "0x504D76514A4eea2DcAF34fb5f528D997665674a7",
        "amount": 10},
        {"transaction_no" : 2,
        "address_from" : address,
        "address_to" : "0xF244106080e54cA451368f2Bde3eefEe14C3d04a",
        "amount": 10},
        {"transaction_no" : 3,
        "address_from" : address,
        "address_to" : "0x504D76514A4eea2DcAF34fb5f528D997665674a7",
        "amount": 10},
        {"transaction_no" : 4,
        "address_from" : address,
        "address_to" : "0xF244106080e54cA451368f2Bde3eefEe14C3d04a",
        "amount": 10},
        {"transaction_no" : 5,
        "address_from" : address,
        "address_to" : "0x1D19478C8CFf983D8b00ffAe15bd3747Bc76cEdD",
        "amount": 10},
        {"transaction_no" : 6,
        "address_from" : address,
        "address_to" : "0xF244106080e54cA451368f2Bde3eefEe14C3d04a",
        "amount": 10}
    ]
    return render_template('wallet.html', transactions=transactions, private_key=private_key, account_balance=10, address=address)