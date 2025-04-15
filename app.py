from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import mysql.connector
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# 数据库连接函数
def get_db():
    return mysql.connector.connect(
        host="39.106.150.70",
        user="ToolAPP",
        password="88888888",
        database="ToolAPP"
    )

# 登录功能增强
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误')
    return render_template('login.html')

# 工具添加功能更新
@app.route('/tool/add', methods=['GET', 'POST'])
def add_tool():
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO tools (
                    tool_name, model, specification, total_quantity,
                    manufacturer, purchase_date, category_id, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                request.form['tool_name'],
                request.form['model'],
                request.form['specification'],
                request.form['quantity'],
                request.form['manufacturer'],
                request.form['purchase_date'],
                request.form.get('category_id'),
                '可用'
            ))
            db.commit()
            flash('工具添加成功')
        except Exception as e:
            db.rollback()
            flash(f'添加失败: {str(e)}')
            
    # 获取分类列表
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tool_categories")
    categories = cursor.fetchall()
    
    return render_template('add_tool.html', categories=categories)

# 工具搜索功能增强
@app.route('/tool/search')
def search_tool():
    keyword = request.args.get('keyword')
    category_id = request.args.get('category_id')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    query = "SELECT * FROM tools WHERE 1=1"
    params = []
    
    if keyword:
        query += " AND (tool_name LIKE %s OR model LIKE %s)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])
        
    if category_id:
        query += " AND category_id = %s"
        params.append(category_id)
        
    cursor.execute(query, params)
    tools = cursor.fetchall()
    
    # 获取分类列表
    cursor.execute("SELECT * FROM tool_categories")
    categories = cursor.fetchall()
    
    return render_template('search_tool.html', tools=tools, categories=categories)

# 添加权限检查装饰器
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] != role:
                flash('您没有权限访问此页面')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 添加借出功能
@app.route('/tool/borrow', methods=['GET', 'POST'])
def borrow_tool():
    if request.method == 'POST':
        try:
            mycursor.execute("""
                INSERT INTO borrow_records (
                    tool_id, user_id, quantity, borrow_date, 
                    due_date, reason, tool_status_before, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                request.form['tool_id'],
                session.get('user_id'),
                request.form['quantity'],
                datetime.now(),
                datetime.now() + timedelta(days=int(request.form['borrow_days'])),
                request.form['reason'],
                '可用',
                '待审批'
            ))
            mydb.commit()
            flash('借出申请已提交')
        except Exception as e:
            mydb.rollback()
            flash(f'借出失败: {str(e)}')
        return redirect(url_for('borrow_tool'))
    
    mycursor.execute("SELECT id, tool_name FROM tools WHERE status = '可用'")
    tools = mycursor.fetchall()
    return render_template('borrow_tool.html', tools=tools)

# 添加审批功能
@app.route('/approve/<int:record_id>', methods=['POST'])
@role_required('admin')
def approve_borrow(record_id):
    action = request.form.get('action')
    try:
        if action == 'approve':
            mycursor.execute("""
                UPDATE borrow_records SET 
                    status = '已借出',
                    tool_status_after = '借出',
                    approver_id = %s
                WHERE id = %s
            """, (session.get('user_id'), record_id))
        else:
            mycursor.execute("""
                UPDATE borrow_records SET 
                    status = '已拒绝',
                    tool_status_after = '可用',
                    approver_id = %s
                WHERE id = %s
            """, (session.get('user_id'), record_id))
        mydb.commit()
        flash('审批操作成功')
    except Exception as e:
        mydb.rollback()
        flash(f'审批失败: {str(e)}')
    return redirect(url_for('approval_list'))

# 添加审批列表
@app.route('/approvals')
def approval_list():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT br.*, t.tool_name, u.username 
        FROM borrow_records br
        JOIN tools t ON br.tool_id = t.id
        JOIN users u ON br.user_id = u.id
        WHERE br.status = '待审批'
    """)
    records = cursor.fetchall()
    return render_template('approval_list.html', records=records)

# 添加归还功能
@app.route('/tool/return/<int:record_id>', methods=['GET', 'POST'])
def return_tool(record_id):
    if request.method == 'POST':
        try:
            db = get_db()
            cursor = db.cursor()
            
            # 检查工具当前状态
            cursor.execute("""
                SELECT t.status FROM borrow_records br
                JOIN tools t ON br.tool_id = t.id
                WHERE br.id = %s
            """, (record_id,))
            current_status = cursor.fetchone()[0]
            
            if current_status != '借出':
                flash('该工具当前不可归还')
                return redirect(url_for('my_borrowings'))
            
            # 更新归还记录
            cursor.execute("""
                UPDATE borrow_records SET 
                    return_date = %s,
                    status = '已归还',
                    tool_status_after = %s,
                    return_condition = %s,
                    damage_description = %s,
                    remarks = %s
                WHERE id = %s
            """, (
                datetime.now(),
                request.form['return_status'],
                request.form['condition'],
                request.form.get('damage_description', ''),
                request.form.get('remarks', ''),
                record_id
            ))
            
            # 根据归还状态更新工具状态
            new_status = '可用' if request.form['return_status'] == '完好' else '维修中'
            cursor.execute("""
                UPDATE tools SET status = %s
                WHERE id = (SELECT tool_id FROM borrow_records WHERE id = %s)
            """, (new_status, record_id))
            
            db.commit()
            flash('工具已成功归还')
        except Exception as e:
            db.rollback()
            flash(f'归还失败: {str(e)}')
        return redirect(url_for('my_borrowings'))
    
    # 获取借出记录详情
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT br.*, t.tool_name, t.status as tool_status
        FROM borrow_records br
        JOIN tools t ON br.tool_id = t.id
        WHERE br.id = %s
    """, (record_id,))
    record = cursor.fetchone()
    
    return render_template('return_tool.html', record=record)

# 添加我的借出记录
@app.route('/my_borrowings')
def my_borrowings():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT br.*, t.tool_name 
        FROM borrow_records br
        JOIN tools t ON br.tool_id = t.id
        WHERE br.user_id = %s
        ORDER BY br.borrow_date DESC
    """, (session.get('user_id'),))
    records = cursor.fetchall()
    return render_template('my_borrowings.html', records=records)

# 添加所有借出记录查询（管理员）
@app.route('/all_borrowings')
@role_required('admin')
def all_borrowings():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT br.*, t.tool_name, u.username 
        FROM borrow_records br
        JOIN tools t ON br.tool_id = t.id
        JOIN users u ON br.user_id = u.id
        ORDER BY br.borrow_date DESC
    """)
    records = cursor.fetchall()
    return render_template('all_borrowings.html', records=records)

if __name__ == '__main__':
    app.run(debug=True)