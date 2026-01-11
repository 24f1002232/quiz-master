from controllers.database import db
from controllers.models import User
from werkzeug.security import generate_password_hash
from app import app

with app.app_context():
    admin = User.query.filter_by(email='admin@gmail.com').first()
    if admin:
        admin.password = generate_password_hash('admin123')
        db.session.commit()
        print('Admin password hashed.')
    else:
        print('Admin not found.')