from flask import render_template, request, redirect, url_for, flash, session
from testapp.func import get_db, id2name
from testapp import app
from contextlib import contextmanager
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from inspect import getmembers, isfunction
import inspect
import importlib.util
from pathlib import Path
import sys
from datetime import timedelta

'''@app.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        g.user = db.execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()'''

app.secret_key = 'user'
app.permanent_session_lifetime = timedelta(hours=8)

@app.route('/')
def mainpage():
    return render_template('testapp/mainpage.html')

@app.route('/gym/login', methods=('GET','POST'))
def gym_login():
    if request.method == 'GET':
        if "user" in session:
            return redirect(url_for('gym_mainpage'))
        return render_template('testapp/gym/login.html')

    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error_message = None

        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM "gym_login" WHERE name=%s', (username,))
                user = cur.fetchone()

        print(user)

        if user is None:
            error_message = 'Incorrect username or password.'
        elif not check_password_hash(user['pass'], password):
            error_message = 'Incorrect username or password.'

        if error_message is not None:
            flash(error_message, category='alert alert-danger')
            return redirect(url_for('gym_login'))

        session.clear()
        session.permanent = True
        session['user'] = user['id']
        return redirect(url_for('gym_mainpage'))


@app.route('/gym/submit', methods=('GET','POST'))
def gym_submit():

    if request.method == 'GET':
        if "user" in session:
            return redirect(url_for('gym_mainpage'))
        return render_template('testapp/gym/submit.html')

    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error_message = None

        with get_db() as conn:
            with conn.cursor() as cur:
                
                if not username:
                    error_message = 'ユーザー名の入力は必須です'
                elif not password:
                    error_message = 'パスワードの入力は必須です'
                else:
                    cur.execute('SELECT name FROM gym_login WHERE name = %s', (username,))
                    if cur.fetchone() is not None:
                        error_message = 'ユーザー名 {} はすでに使用されています'.format(username)

                if error_message is not None:
                    flash(error_message, category='alert alert-danger')
                    return redirect(url_for('gym_submit'))

                cur.execute(
                    'INSERT INTO gym_login (name, pass) VALUES (%s, %s)',
                    (username, generate_password_hash(password))
                )
                conn.commit()

        flash('ユーザー登録が完了しました。登録した内容でログインしてください', category='alert alert-info')
        return redirect(url_for('gym_login'))
    

@app.route('/gym/logout')
def gym_logout():
    session.pop("user", None)
    return redirect(url_for("gym_login"))


@app.route('/gym/mainpage', methods =['GET', 'POST'])
def gym_mainpage():
    if "user" in session:
        user = session["user"] 
        username = id2name(user)

        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM gym_projects WHERE gym_id = %s', (user,))
                projects = cur.fetchall()
                print(projects)

        if request.method == 'GET':
            return render_template('testapp/gym/mainpage.html', user=user, username=username, projects=projects)
        
        elif request.method == 'POST':
    
            r1 = request.form['project_name']
            r2 = request.form['description']
            r3 = request.form['project_type']
            r4 = request.form.get('tie_breaker')
            r5 = request.form['limit_people']
            r6 = request.form['deadline']
            r7 = request.form['schedule']

            print(r1, r2, r3, r4, r5, r6, r7)

            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO gym_projects
                        (gym_id, project_name, description, project_type, tie_breaker, limit_people, deadline, schedule)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        RETURNING id
                        """,
                        (session["user"], r1, r2, r3, r4, r5, r6, r7)
                    )
                    project_info = cur.fetchone()
                    conn.commit()

            flash('プロジェクト情報を更新しました', category='alert alert-info')
            return redirect(url_for('gym_projects', project_id=project_info['id'], project_info=project_info))
        
    else:
        return redirect(url_for("gym_login"))
    

@app.route('/gym/projects/<project_id>', methods =['GET', 'POST'])
def gym_projects(project_id):

    if request.method == 'GET':
        checker = None
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM gym_projects WHERE id = %s and gym_id = %s', (project_id, session["user"]))
                checker = cur.fetchone()

        if "user" in session:
            if checker is not None:
                user = session["user"]
                username = id2name(user)
                print(checker)
                return render_template('testapp/gym/project.html', user=user, username=username, project_info=checker)
            else:
                flash('アクセス権限がありません', category='alert alert-danger')
                return redirect(url_for('gym_error'))
        else:
            return redirect(url_for("gym_login"))
        
    elif request.method == 'POST':
        pass
    

@app.route('/gym/error')
def gym_error():
    return render_template('testapp/gym/error.html')