from flask import Flask, request
from flask_socketio import SocketIO
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from flask import Flask, render_template
import base64



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


# 创建一个路由，处理 '/edit' 路径的请求
@app.route('/edit')
def edit():
    return render_template('editpage.html')


# 路由：显示数据
@app.route('/display_data')
def display_data():
    session = Session()

    sql = text('SELECT myimage, mycontent FROM myblogs')
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

    # 将数据和编码后的图像组合成一个列表
    data_and_images = list(zip(contents, encoded_images))


    return render_template('index.html', data_and_images =data_and_images)


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
