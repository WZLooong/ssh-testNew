from flask import Flask, render_template, request, redirect, url_for
# 问题可能是由于 mysql-connector-python 库未安装导致的
# 可以使用以下命令安装该库
# pip install mysql-connector-python
import mysql.connector

app = Flask(__name__)

# 连接到 MySQL 数据库
mydb = mysql.connector.connect(
    host="localhost",
    user="wzlooong",
    password="88888888",
    database="toolAPP"
)
mycursor = mydb.cursor()

# 模拟工具数据库
tools = []

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # 查询数据库验证用户信息
        sql = "SELECT * FROM users WHERE username = %s AND password = %s"
        val = (username, password)
        mycursor.execute(sql, val)
        user = mycursor.fetchone()
        if user:
            return "登录成功！"
        else:
            return "用户名或密码错误，请重试。"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # 检查用户名是否已存在
        sql = "SELECT * FROM users WHERE username = %s"
        val = (username,)
        mycursor.execute(sql, val)
        user = mycursor.fetchone()
        if user:
            return "该用户名已存在，请选择其他用户名。"
        # 插入新用户信息
        sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
        val = (username, password)
        mycursor.execute(sql, val)
        mydb.commit()
        return "注册成功！请前往 <a href='/login'>登录</a>"
    return render_template('register.html')

# 工具信息录入页面
@app.route('/tool/add', methods=['GET', 'POST'])
def add_tool():
    if request.method == 'POST':
        tool_name = request.form.get('tool_name')
        model = request.form.get('model')
        specification = request.form.get('specification')
        quantity = request.form.get('quantity')
        manufacturer = request.form.get('manufacturer')
        purchase_date = request.form.get('purchase_date')
        storage_location = request.form.get('storage_location')
        status = '可用'  # 默认状态为可用

        tool = {
            'tool_name': tool_name,
            'model': model,
            'specification': specification,
            'quantity': quantity,
            'manufacturer': manufacturer,
            'purchase_date': purchase_date,
            'storage_location': storage_location,
            'status': status
        }
        tools.append(tool)
        return "工具信息录入成功！"
    return render_template('add_tool.html')

# 工具分类检索页面
@app.route('/tool/search', methods=['GET'])
def search_tool():
    keyword = request.args.get('keyword')
    category = request.args.get('category')

    if keyword:
        results = [tool for tool in tools if keyword in tool['tool_name'] or keyword in tool['model']]
    elif category:
        # 这里可以根据具体的分类逻辑进行筛选
        results = tools  # 暂时返回所有工具，需要根据实际情况实现分类筛选
    else:
        results = tools

    return render_template('search_tool.html', tools=results)

# 工具状态更新页面
@app.route('/tool/update_status', methods=['GET', 'POST'])
def update_tool_status():
    if request.method == 'POST':
        tool_name = request.form.get('tool_name')
        new_status = request.form.get('new_status')

        for tool in tools:
            if tool['tool_name'] == tool_name:
                tool['status'] = new_status
                return "工具状态更新成功！"
        return "未找到该工具，请检查工具名称。"
    return render_template('update_status.html')

# 注册页面
@app.route('/register_page')
def register_page():
    return render_template('register.html')

# 登录页面
@app.route('/login_page')
def login_page():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)