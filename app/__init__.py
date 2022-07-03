from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_whooshee import Whooshee
from flask_admin import Admin
from flask_babelex import Babel

from app.utils import get_search_part
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = '请登录后使用此功能'
login.login_message_category = 'info'
mail = Mail(app)
whooshee = Whooshee(app)
# Whooshee.reindex()方法为数据重新编制丢失索引
whooshee.reindex()
admin = Admin(app, name='卓见管理系统', template_mode='bootstrap3')

babel = Babel(app)
app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'


def add_template_filters():
    """
    注册自定义模板验证器
    """
    app.add_template_filter(get_search_part)


from app.routes.index import *
from app.routes.book import *
from app.routes.user import *
from app.routes.admin import *
