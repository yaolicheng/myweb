from flask import Flask
from flask_socketio import SocketIO

# 创建一个 Flask 应用实例
app = Flask(__name__)

socketio = SocketIO(app)

# 创建一个路由，处理根路径的请求
@app.route('/')
def hello_world():
    return 'Hello, World!'

# 创建一个路由，处理 '/about' 路径的请求
@app.route('/about')
def about():
    return 'This is the about page.'

if __name__ == '__main__':
    #allow_unsafe_werkzeug = True 表示允许使用非安全的Werkzeug服务器，这样就可以让程序在后台运行了
    socketio.run(app,host='0.0.0.0', allow_unsafe_werkzeug=True)
