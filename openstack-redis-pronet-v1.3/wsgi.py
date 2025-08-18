# wsgi.py
from flask import Flask
from config.settings import Config
from models import db
from auth import auth
from dashboard import dashboard
from flask_login import LoginManager
from flask_mail import Mail
from flask_session import Session

mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)
    Session(app)
    login_manager.init_app(app)

    app.register_blueprint(auth)
    app.register_blueprint(dashboard)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)