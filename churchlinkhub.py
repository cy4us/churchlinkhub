# Übernommen und z.T. angepasst
from app import app, db
from app.models import User, Category, Link

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Category': Category, 'Link': Link}

