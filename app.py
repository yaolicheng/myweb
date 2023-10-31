from flask import Flask

# 创建一个 Flask 应用实例
app = Flask(__name__)

# 创建一个路由，处理根路径的请求
@app.route('/')
def hello_world():
    return 'Hello, World!'

# 创建一个路由，处理 '/about' 路径的请求
@app.route('/about')
def about():
    return 'This is the about page.'

if __name__ == '__main__':
    # 启动应用，监听端口 5000
    app.run()
