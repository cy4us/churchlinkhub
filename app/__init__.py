import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from sqlalchemy import inspect
# LoginManager
from flask_login import LoginManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = 'Please log in to access this page.'
bootstrap = Bootstrap(app)

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/churchlinkhub.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Churchlinkhub startup')

from app import routes, models, errors, api

import json
from app.models import Category, Link
with app.app_context():
    
    # check if db is ready - if not skip it
    insp = inspect(db.engine)
    if insp.has_table('user'):

    #db.create_all()
        app.logger.info("Start update procedure")
        
        # load the data into the database from the json file
        try:
            with open(app.config['JSON_PATH'],'r') as file:
                data = json.load(file)
        except:
            app.logger.info("File " + app.config['JSON_PATH'] + " not found")
            app.logger.info("Using fallback")

            data = '''
    {
        "links": [
            {
            "id": "https://www.jugendarbeit.online/jo",
            "category": "Kinder- und Jugendarbeit",
            "keywords": "Kinderarbeit, Jugendarbeit"
            },
            {
            "id": "https://www.mrjugendarbeit.com",
            "category": "Kinder- und Jugendarbeit",
            "keywords": "Kinderarbeit, Jugendarbeit, mrjugendarbeit"
            },
            {
            "id": "https://www.jugendleiter-blog.de",
            "category": "Kinder- und Jugendarbeit",
            "keywords": "Kinderarbeit, Jugendarbeit"
            },
            {
            "id": "https://www.freebibleimages.org",
            "category": "Kinder- und Jugendarbeit",
            "keywords": "Kinderarbeit, Jugendarbeit"
            },
            {
            "id": "https://connect.groupsenz.org/gruppenspiele",
            "category": "Kinder- und Jugendarbeit",
            "keywords": "Kinderarbeit, Jugendarbeit"
            },
            {
            "id": "https://www.youngstarswiki.org/de",
            "category": "Kinder- und Jugendarbeit",
            "keywords": "Kinderarbeit, Jugendarbeit, Jungschar"
            },
            {
            "id": "https://www.jungschar-echt-stark.de",
            "category": "Kinder- und Jugendarbeit",
            "keywords": "Kinderarbeit, Jugendarbeit, Jungschar"
            },
            {
            "id": "https://www.kirche-kunterbunt.de",
            "category": "Kinder- und Jugendarbeit",
            "keywords": "Kinderarbeit, Jugendarbeit"
            },
            {
            "id": "https://www.youtube.com/@SaddlebackKidsBerlin",
            "category": "Kinder- und Jugendarbeit",
            "keywords": "Kinderarbeit, Jugendarbeit, YouTube"
            },
            {
            "id": "https://mannaplace.de",
            "category": "Gottesdienstgestaltung",
            "keywords": "Gottesdienst, Gestaltung"
            },
            {
            "id": "https://www.kirche-weiningen.ch/fileadmin/user_upload/weiningen/Dateien/Dokumente/Theatersammlung/Theatersammlung-moderne-GD-bis-Okt-2019.pdf",
            "category": "Gottesdienstgestaltung",
            "keywords": "Gottesdienst, Gestaltung, PDF"
            },
            {
            "id": "https://www.mi-di.de/toolbox-gremienspiritualitaet",
            "category": "Kirchenleitung",
            "keywords": "Kirchenleitung, Leitung, Toolox"
            },
            {
            "id": "https://orangeleben.ch",
            "category": "Kirchenleitung",
            "keywords": "Kirchenleitung, Leitung"
            },
            {
            "id": "https://godline.de/material/",
            "category": "Kirchenleitung",
            "keywords": "Kirchenleitung, Leitung"
            },
            {
            "id": "https://de.alphalive.ch/try-alpha/",
            "category": "Kirchenleitung",
            "keywords": "Kirchenleitung, Leitung"
            },
            {
            "id": "https://biblehub.com",
            "category": "Bildung",
            "keywords": "Bildung, Bibel, Studium"
            },
            {
            "id": "https://bibleproject.visiomedia.org",
            "category": "Bildung",
            "keywords": "Bildung, Bibel, Video"
            },
            {
            "id": "https://www.practicingtheway.org",
            "category": "Bildung",
            "keywords": "Bildung"
            },
            {
            "id": "https://glaubendenken.net",
            "category": "Bildung",
            "keywords": "Bildung"
            },
            {
            "id": "https://worthaus.org",
            "category": "Bildung",
            "keywords": "Bildung"
            },
            {
            "id": "https://www.glaubeundgesellschaft.ch",
            "category": "Bildung",
            "keywords": "Bildung, Schweiz"
            }
        ]
    }
    ''' 
            data = json.loads(data)

        for link_info in data.get('links', []):

            category = Category.query.filter_by(category=link_info['category']).first()
            if category is None:
                app.logger.info("add new category: " + link_info['category'])
                category = Category(category=link_info['category'])
                db.session.add(category)
                db.session.commit()

            link = Link.query.filter_by(link=str(link_info['id'])).first()
            if link is None:
                app.logger.info("add new link: " + link_info['id'])
                link = Link(link=str(link_info['id']))
            link.id_category = category.category_id
            link.keywords=link_info['keywords']
            db.session.add(link)
            db.session.commit()

        app.logger.info("End update procedure")
    else:
        app.logger.info("Skipped import - db not ready")
