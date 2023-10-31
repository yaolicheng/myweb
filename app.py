from flask import Flask
from flask_socketio import SocketIO
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text



# 创建一个 Flask 应用实例
app = Flask(__name__)

socketio = SocketIO(app)

# 创建一个数据库连接引擎并使用连接池
engine = create_engine("mysql+mysqlconnector://root:yy116@localhost/myweb")

# 创建一个 Session 类，它将使用连接池管理数据库连接
Session = sessionmaker(bind=engine)



# 创建一个路由，处理根路径的请求
@app.route('/')
def hello_world():
    # 创建一个 Session 实例
    session = Session()

    outline = ''

    # 现在你可以使用 session 对象执行数据库操作
    query = text("SELECT * FROM test")
    result = session.execute(query)
    for row in result:
        outline+=(row[0])+' '
        outline+=(row[1])+' '
        outline+=(row[2])+' '

    # 最后，记得关闭连接
    session.close()
    return outline #'hello world'

# 创建一个路由，处理 '/about' 路径的请求
@app.route('/about')
def about():
    return 'This is the about page.'

if __name__ == '__main__':
    #allow_unsafe_werkzeug = True 表示允许使用非安全的Werkzeug服务器，这样就可以让程序在后台运行了
    socketio.run(app,host='0.0.0.0', allow_unsafe_werkzeug=True)
