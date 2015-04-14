from flask import Flask
from flask_login import LoginManager
from taplist import login, views
from taplist.session import RedisSessionInterface

app = Flask(__name__)
app.config.from_object('config')
app.debug=True

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.session_interface = RedisSessionInterface()

@login_manager.user_loader
def load_user(name):
    user = login.BarUser(name)
    return user

app.add_url_rule('/<location>/entry', view_func=views.entry, methods=['GET', 'POST'])
app.add_url_rule('/<location>/scroll', view_func=views.scroll, methods=['GET'])
app.add_url_rule('/<location>/json', view_func=views.get_json, methods=['GET'])
app.add_url_rule('/<location>/edit', view_func=views.editlist, methods=['GET', 'POST'])
app.add_url_rule('/<location>', view_func=views.bars)
app.add_url_rule('/<location>/', view_func=views.bars)
app.add_url_rule('/login', view_func=views.login, methods=['GET', 'POST'])
app.add_url_rule('/logout', view_func=views.logout)
app.add_url_rule('/', view_func=views.index)
