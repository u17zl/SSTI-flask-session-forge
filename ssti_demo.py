# coding:utf8

import uuid
from flask import Flask, request, make_response, session,render_template, url_for, redirect, render_template_string

app = Flask(__name__)
app.config['SECRET_KEY']='Hello World!'

@app.route('/')
def index():
    
    app.logger.info(request.cookies)
    try:
        username=session['username']
        return render_template("index.html",username=username)
    except Exception:
    
        return """<form action="%s" method='post'>
            <input type="text" name="username" required>
            <input type="password" name="password" required>
            <input type="submit" value="登录">
            </form>""" %url_for("login")

@app.route("/content/", methods=['GET'])
def content():
    content = request.args.get("content")
    return render_template_string(content)

@app.route("/login/", methods=['POST'])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    app.logger.info(username)
    if username.strip():
        if username=="admin" and password!=str(uuid.uuid4()):
            return "login failed"
        app.logger.info(url_for('index'))
        resp = make_response(redirect(url_for("index")))
        session['username']=username
        return resp
    else:
        return "login failed"

@app.errorhandler(404)
def page_not_found(e):
    template='''
        {%% block body %%}
        <div class="center-content error">
        <h1>Oops! That page doesn't exist.</h1>
        <h3>%s</h3>
        </div>
        {%% endblock %%}
    '''%(request.url)
    return render_template_string(template),404

@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for("index")))
    session.pop('username')
    return resp

if __name__ == "__main__":
    
    app.run(port=8999, debug=True)

