from flask import render_template, flash, redirect, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import or_
from app import app, db
from app.forms import LoginForm, RegistrationForm, SearchForm
from app.models import User, Link, Category

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = SearchForm()
    if form.validate_on_submit():
        keyword = form.search.data
        app.logger.debug("Search started with word " + keyword)

        # Füge Filterbedingungen für Schlüsselwörter und Link hinzu
        links = Link.query.filter(or_(
            Link.keywords.ilike(f'%{keyword}%'),
            Link.link.ilike(f'%{keyword}%')
        )).all()

    else:
        links = Link.query.all()
    return render_template('index.html', title='Home', form=form, links=links)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        app.logger.info(user)
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
