from flask import Flask,render_template
from controllers.database import db
from controllers.models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = 'thisissecretkey'
db.init_app(app)

with app.app_context():
    db.create_all()

    admin = User.query.filter_by(role = "admin").first()
    if not admin:
        admin = User(
            name = "admin",
            email = "admin@gmail.com",
            password = "admin123",
            role = "admin"
        )
        db.session.add(admin)
        db.session.commit()
    

    

from controllers.routes import *

if __name__ == '__main__':
    app.run(debug = True)
