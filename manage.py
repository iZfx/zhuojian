from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import app, db

manager = Manager(app)

# 用Migrate将app和db绑定
# 第一个参数是flask实例，第二个参数SQLAlchemy实例
Migrate(app, db)

# 添加迁移脚本的命令到manager中
# manager是Flask-Script的实例，这条语句在flask-Script中添加一个db命令
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
