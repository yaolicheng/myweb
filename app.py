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
#密钥，必须设置，否则在调用login_user时会报错RuntimeError: The session is unavailable because no secret key was set.  Set the secret_key on the application to something unique and secret.
app.secret_key='HCRkCYX6fiSQUdx8T3BlbkFJF2Xa1MIChij9TiBd0I7O'

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


# 创建一个路由，处理 '/about' 路径的请求
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/reg')
def reg():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    phone = request.form['phonenumber']
    birthday = request.form['birthday']
    sex = request.form['sex']

    session = Session()

    sql = text('insert into myweb.myuser(username,pwd,email,phonenumber,sex,birthday) values(:user,:pwd,:email,:phone,:sex,:birthday);')
    data = {"user": username, "pwd": password,"email":email,"phone":phone,"sex":sex,"birthday":birthday}
    session.execute(sql, data)
    #必须要commit才能完成更新的正式提交
    session.commit()
    session.close()
    
    return render_template('regsuccess.html')

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
        #要获取所有记录，然后判断rows的长度来判断，只用result.returns_rows是无法正确判断是否有结果的
        rows = result.fetchall()
        session.close()
        # 检查结果是否为空
        if len(rows)>0:
            # 结果集非空
            user = User(username)
            login_user(user)
            return redirect(url_for('mycount'))
        else:
            # 结果集为空
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


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



# 创建一个路由，处理 '/edit' 路径的请求
@app.route('/edit')
def edit():
    if current_user.is_authenticated:
        return render_template('editpage.html', user=current_user)
    else:
        return redirect(url_for('login'))

#获取指定用户的blog
def getimagesandcontent(user=None):
    session = Session()
    if user:
        #必须用text格式化，否则无法执行
        sql = text('SELECT myimage, mycontent,logid,username,starcount,commentcount,blogdate FROM myblogs where username = :user ORDER BY blogdate DESC  LIMIT 10')
        data ={"user":user}
        result = session.execute(sql,data)
    else:
        sql = text('SELECT myimage, mycontent,logid,username,starcount,commentcount,blogdate FROM myblogs  ORDER BY blogdate DESC  LIMIT 10')
        result = session.execute(sql)
    encoded_images = []
    contents = []
    logids=[]
    unames=[]
    stars=[]
    comcounts=[]
    bdates=[]


    for data in result:
        # 对每个图像数据进行Base64编码
        if data[0]:
            encoded_image = base64.b64encode(data[0]).decode('utf-8')
        else:
            encoded_image = None
        encoded_images.append(encoded_image)
        contents.append(data[1])
        logids.append(data[2])
        unames.append(data[3])
        stars.append(data[4])
        comcounts.append(data[5])
        bdates.append(data[6])
    # 最后，记得关闭连接
    session.close()

    # 将数据和编码后的图像组合成一个列表，便于前台读取
    data_and_images = list(zip(contents, encoded_images,logids,unames,stars,comcounts,bdates))
    return data_and_images

#获取日志信息
def getblogdetail(blogid):
    session = Session()
        #必须用text格式化，否则无法执行
    sql = text('SELECT myimage, mycontent,logid,username,starcount,commentcount,blogdate FROM myblogs where logid = :logid ')
    data ={"logid":blogid}
    result = session.execute(sql,data)
   
    data_and_images = []


    for data in result:
        # 对每个图像数据进行Base64编码
        if data[0]:
            encoded_image = base64.b64encode(data[0]).decode('utf-8')
        else:
            encoded_image = None
        data_and_images.append(encoded_image)
        data_and_images.append(data[1])
        data_and_images.append(data[2])
        data_and_images.append(data[3])
        data_and_images.append(data[4])
        data_and_images.append(data[5])
        data_and_images.append(data[6])
    # 最后，记得关闭连接
    session.close()

    return data_and_images

#获取指定的blog
def getbolgcomments(blogid):
    session = Session()
    
    #必须用text格式化，否则无法执行
    sql = text('SELECT commentid, username,mycomment,comdate FROM blogcomments where logid = :logid ORDER BY comdate DESC')
    data ={"logid":blogid}
    result = session.execute(sql,data)
    
    comids =[]
    unames=[]
    comments = []
    comdates=[]


    for data in result:
     
        comids.append(data[0])
        unames.append(data[1])
        comments.append(data[2])
        comdates.append(data[3])
    # 最后，记得关闭连接
    session.close()

    # 将数据和编码后的图像组合成一个列表，便于前台读取
    datas = list(zip(comids, unames,comments,comdates))
    return datas

# 路由：显示数据
@app.route('/')
def index():
    # 将数据和编码后的图像组合成一个列表，便于前台读取
    data_and_images = getimagesandcontent()
    return render_template('index.html', data_and_images =data_and_images)

#我的账户信息
@app.route('/mycount')
def mycount():
    if current_user.is_authenticated:
        data_and_images = getimagesandcontent(current_user.username)
        return render_template('mycount.html', user=current_user,data_and_images =data_and_images)
    else:
        return redirect(url_for('login'))

#添加评论
@app.route('/addcomment', methods=['POST'])
def addcomment():

    if current_user.is_authenticated:
        username = request.form['username']
        blogid = request.form['blogid']
        comment = request.form['comment']

        session = Session()

        sql = text('insert into myweb.blogcomments(logid,username,mycomment) values(:blodid,:user,:comment)')
        data = {"user": username, "blodid": blogid,"comment":comment}
        session.execute(sql, data)
        sql = text('update myweb.myblogs set commentcount = commentcount +1 where logid = :blodid')
        data = { "blodid": blogid}
        session.execute(sql, data)
        #必须要commit才能完成更新的正式提交
        session.commit()
        session.close()
    
        return redirect(url_for('blogdetail',blogid=blogid))
    else:
        return redirect(url_for('login'))

#显示某条blog的信息
@app.route('/bdetail/<int:blogid>')
def blogdetail(blogid):

    if current_user.is_authenticated:
        #获取此记录的详细信息，然后获取它的评论，一起传递给blogdetail.html
        data_and_images = getblogdetail(blogid)
        datas = getbolgcomments(blogid)
        # 返回删除后的页面或重定向到其他页面
        return render_template('blogdetail.html', user=current_user,data_and_images =data_and_images,comments=datas)
    else:
        return redirect(url_for('login'))

#加星功能实现
@app.route('/addstar/<int:blogid>')
def addstar(blogid):

    if current_user.is_authenticated:
        #获取设置star数加1
        session = Session()
        #首先判断此用户是否已点过加星
        sql = text("SELECT 1 FROM starusers where username = :user and logid= :blogid ")
        data = {"user": current_user.username, "blogid": blogid}
        result = session.execute(sql,data)
        #要获取所有记录，然后判断rows的长度来判断，只用result.returns_rows是无法正确判断是否有结果的
        rows = result.fetchall()
        if len(rows)==0:
            sql = text('update myblogs set starcount=starcount+1 where logid =:blogid')
            data = {"blogid": blogid}
            session.execute(sql, data)
            #记录谁加的星
            sql = text('insert into  starusers(logid,username) values(:blogid,:username)')
            data = {"blogid": blogid,"username":current_user.username}
            session.execute(sql, data)
            #必须要commit才能完成更新的正式提交
            session.commit()
        session.close()
        return redirect(url_for('blogdetail',blogid=blogid))
    else:
        return redirect(url_for('login'))
#删除某条日志
@app.route('/delete/<int:blogid>')
def delete_blog(blogid):
    if current_user.is_authenticated:
        # 在这里执行删除操作，使用 blogid 参数来确定要删除的博客
        session = Session()
        sql = text('delete from starusers where logid =:blogid')
        data = {"blogid": blogid}
        session.execute(sql, data)
        sql = text('delete from blogcomments where logid =:blogid')
        data = {"blogid": blogid}
        session.execute(sql, data)
        sql = text('delete from myblogs where logid =:blogid and username=:username')
        data = {"blogid": blogid,"username":current_user.username}
        session.execute(sql, data)
        #必须要commit才能完成更新的正式提交
        session.commit()
        session.close()
        # 返回删除后的页面或重定向到其他页面
        return redirect(url_for('mycount'))
    else:
        return redirect(url_for('login'))
    

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' in request.files:
        image = request.files['image']
        content = request.form['content']
        keywords = request.form['keywords']
        if image.filename != '':#有图片的日志
            #保存到数据中
            print("image.filename != ")
            image_binary = image.read()
            session = Session()

            sql = text('insert into myweb.myblogs(username,keywords,mycontent,myimage) values(:user,:keywords,:content,:image)')
            data = {"image": image_binary, "user": current_user.username, "keywords":keywords, "content":content}
            session.execute(sql, data)
            #必须要commit才能完成更新的正式提交
            session.commit()
            session.close()

            #image.save('uploads/' + image.filename)
            return redirect(url_for('mycount'))
        else:#没有图片的日志
            print("没有图片的日志 ")
            session = Session()
            sql = text('insert into myweb.myblogs(username,keywords,mycontent) values(:user,:keywords,:content)')
            data = { "user": current_user.username, "keywords": keywords, "content":content}
            session.execute(sql, data)
            #必须要commit才能完成更新的正式提交
            session.commit()
            session.close()
            return redirect(url_for('mycount'))
    return 'Image upload failed.'

if __name__ == '__main__':
    #allow_unsafe_werkzeug = True 表示允许使用非安全的Werkzeug服务器，这样就可以让程序在后台运行了
    socketio.run(app,host='0.0.0.0', allow_unsafe_werkzeug=True)
