from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object('config')
app.debug=True

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from app import views, login

@login_manager.user_loader
def load_user(name):
    user = login.BarUser(name)
    return user
