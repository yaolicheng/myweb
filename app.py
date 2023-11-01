from flask import Flask, request
from flask import redirect, url_for
from flask_socketio import SocketIO
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from flask import Flask, render_template
import base64

from flask_login import LoginManager
from flask_login import login_user, current_user
from flask_login import logout_user
from flask_login import UserMixin



# 创建一个 Flask 应用实例
app = Flask(__name__)

app.secret_key='your_secret_key_here'

socketio = SocketIO(app)

#在UserMixin 中有属性 is_active等
class User(UserMixin):
    username:str
    password:str
    email:str
    sex:str
    birthday:str
    def __init__(self, user_id):
        self.username = user_id

    def get_id(self):
        return str(self.username)
    


# 创建一个数据库连接引擎并使用连接池
engine = create_engine("mysql+mysqlconnector://root:yy116@localhost/myweb")

# 创建一个 Session 类，它将使用连接池管理数据库连接
Session = sessionmaker(bind=engine)

#登录服务
login_manager = LoginManager()

#设置登录视图的端点，这个方法必须要定义并实现，否则会报错
@login_manager.user_loader
def load_user(user_name):
    return User(user_name)

login_manager.init_app(app)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        #数据库检查
        # 创建一个 Session 实例
        session = Session()
        # 现在你可以使用 session 对象执行数据库操作
        query = text("SELECT 1 FROM myuser where username = :user and pwd= :pwd and status =1")
        data = {"user": username, "pwd": password}
        result = session.execute(query,data)
        print(result.returns_rows)
        # 检查结果是否为空
        if result.returns_rows>0:
            # 结果集非空
            user = User(username)
            login_user(user)
            session.close()
            return redirect(url_for('index'))
        else:
            session.close()
            # 结果集为空
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


# 创建一个路由，处理根路径的请求
@app.route('/hello_world')
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


# 创建一个路由，处理 '/edit' 路径的请求
@app.route('/edit')
def edit():
    return render_template('editpage.html')

#获取制定用户的blog
def getimagesandcontent(user):
    session = Session()
    #必须用text格式化，否则无法执行
    sql = text('SELECT myimage, mycontent,username,starcount,commentcount,blogdate FROM myblogs where username = :user ORDER BY blogdate DESC  LIMIT 10')
    data ={"user":user}
    result = session.execute(sql,data)
    encoded_images = []
    contents = []


    for data in result:
        # 对每个图像数据进行Base64编码
        if data[0]:
            encoded_image = base64.b64encode(data[0]).decode('utf-8')
        else:
            encoded_image = None
        encoded_images.append(encoded_image)
        contents.append(data[1])
    # 最后，记得关闭连接
    session.close()

    # 将数据和编码后的图像组合成一个列表，便于前台读取
    data_and_images = list(zip(contents, encoded_images))
    return data_and_images

# 路由：显示数据
@app.route('/')
def index():
    
    session = Session()
    #必须用text格式化，否则无法执行
    sql = text('SELECT myimage, mycontent,username,starcount,commentcount,blogdate FROM myblogs ORDER BY blogdate DESC  LIMIT 10')
    result = session.execute(sql)
    encoded_images = []
    contents = []


    for data in result:
        # 对每个图像数据进行Base64编码
        if data[0]:
            encoded_image = base64.b64encode(data[0]).decode('utf-8')
        else:
            encoded_image = None
        encoded_images.append(encoded_image)
        contents.append(data[1])
    # 最后，记得关闭连接
    session.close()

    # 将数据和编码后的图像组合成一个列表，便于前台读取
    data_and_images = list(zip(contents, encoded_images))


    return render_template('index.html', data_and_images =data_and_images)

#我的账户信息
@app.route('/mycount')
def mycount():
    if current_user.is_authenticated:
        data_and_images = getimagesandcontent(current_user.username)
        return render_template('mycount.html', user=current_user,data_and_images =data_and_images)
    else:
        return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' in request.files:
        image = request.files['image']
        blogid = request.form['blogid']
        if image.filename != '':
            #保存到数据中
            image_binary = image.read()
            session = Session()

            sql = text('UPDATE myblogs SET myimage = :image  WHERE logid =:blogid')
            data = {"image": image_binary, "blogid": blogid}
            session.execute(sql, data)
            #必须要commit才能完成更新的正式提交
            session.commit()

            #image.save('uploads/' + image.filename)
            return 'Image uploaded successfully!'
    return 'Image upload failed.'

if __name__ == '__main__':
    #allow_unsafe_werkzeug = True 表示允许使用非安全的Werkzeug服务器，这样就可以让程序在后台运行了
    socketio.run(app,host='0.0.0.0', allow_unsafe_werkzeug=True)
