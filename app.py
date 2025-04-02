from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 模拟用户数据库
users = {}

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users and users[username] == password:
            return "登录成功！"
        else:
            return "用户名或密码错误，请重试。"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users:
            return "该用户名已存在，请选择其他用户名。"
        users[username] = password
        return "注册成功！请前往 <a href='/login'>登录</a>"
    return render_template('register.html')

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