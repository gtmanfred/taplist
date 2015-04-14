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

app.add_url_rule('/<location>/entry', view_func=views.Entry.as_view('entry'), methods=['GET', 'POST', 'PUT'])
app.add_url_rule('/<location>/scroll', view_func=views.Scroll.as_view('scroll'), methods=['GET'])
app.add_url_rule('/<location>/json', view_func=views.Json.as_view('get_json'), methods=['GET'])
app.add_url_rule('/<location>/edit', view_func=views.Edit.as_view('editlist'), methods=['GET', 'POST'])
app.add_url_rule('/<location>/', view_func=views.BarLists.as_view('bars'))
app.add_url_rule('/login', view_func=views.Login.as_view('login'), methods=['GET', 'POST'])
app.add_url_rule('/logout', view_func=views.Logout.as_view('logout'))
app.add_url_rule('/', view_func=views.Index.as_view('index'))
