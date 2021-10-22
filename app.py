from enum import unique
from os import name
from re import template
from flask import Flask, render_template, url_for, redirect, request, session
from flask.helpers import flash
from flask.templating import render_template_string
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.elements import literal_column
from sqlalchemy.sql.functions import current_user, user
from datetime import datetime


msg = 'Invalid Username or Password.'
app = Flask(__name__)
app.config['SECRET_KEY'] = "S3cr3t"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_SECURE"] = True	
Session(app)

#database
db = SQLAlchemy(app)
class Users(db.Model):
   id = db.Column('uid', db.Integer, primary_key = True)
   user = db.Column(db.String(50), unique = True)
   passwd = db.Column(db.String(50))
   
   def __repr__(self):
        return 'user ' + str(self.user)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text(200), nullable=False)
    author = db.Column(db.String(20), nullable=False, default='N/A')
    date_post = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return 'Post ' + str(self.id)

#Routing Paths
@app.route('/')
def index():
    if not session.get("name"):
        return render_template('login.html')
    else:
         return redirect('home')

@app.route('/home')
def home():
    if session.get("name"):
        name1 = session["name"]       
        return render_template('home.html', name=name1)
    else:
        return redirect('login')

#Registeration
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        Username = request.form.get('user')
        Password = request.form.get('pass')
        u = Users.query.filter_by(user=Username).first()
        if u != Username:
            reg = Users(user=Username, passwd=Password)
            db.session.add(reg)
            db.session.commit()
            return redirect('/')
        else:
            flash('Usename Alreay Exist!')
            return redirect('reg')

#posting
@app.route('/spost', methods=['GET','POST'])
def process():
    if request.method == 'POST':
        name1 = session["name"]
        t = request.form.get('title')
        c = request.form.get('content')
        post = Posts(title=t, content=c, author=name1)
        db.session.add(post)
        db.session.commit()
        flash("Post Published.")
        return redirect('posts')

#deleting post
@app.route('/posts/delete/<int:id>')
def delete(id):
    name1 = session["name"]
    if name1 == 'admin':
        post = Posts.query.get_or_404(id)
        db.session.delete(post)
        db.session.commit()
        flash("Post was Deleted Successfully")
        return redirect('/posts')
    else:
        flash('Admin users only allowed to delete the Post')
        return redirect('/posts')

#editing post
@app.route('/posts/edit/<int:id>', methods=['POST', 'GET'])
def edit(id):
    post = Posts.query.get_or_404(id)
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        db.session.commit()
        flash('Changes were Updated')
        return redirect('/posts')
    else:
        name1 = session["name"]
        return render_template('editpost.html', post=post, name=name1)


#registration
@app.route('/reg')
def reg():
        return render_template('register.html')

#Login Validation
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method =='GET':
        return render_template('login.html')
    else:
        pass
        if request.method == 'POST':
            u = request.form.get('uname')
            p = request.form.get('psw')
            try:
                user_db = Users.query.filter_by(user=u).first().user
                pass_db = Users.query.filter_by(user=u).first().passwd
                if user_db == u and pass_db == p:
                    session['name'] = u
                    flash('Logged In as ' + u +'!')
                    return redirect(url_for('home'))
                else:
                    flash("Invalid Username or Password!")
                    return redirect('login')

            except (RuntimeError, TypeError, NameError, AttributeError):
                flash('Invalid Username or Password')
                return redirect('login')

#oldone[validation]
            '''user_db = Users.query.filter_by(user=u).first()
            pass_db = Users.query.filter_by(user=u).first().passwd
            if user_db == u and pass_db == p:
                session['name'] = u
                flash('Logged In as ' + u +'!')
                return redirect(url_for('home'))
            else:
                flash("Invalid Username or Password!")
                return redirect('login')
        else:
            flash("Invalid Username or Password!")
            return redirect('login')'''


#changepassword
@app.route('/cpassword')
def cpassword():
    if session.get("name"):
        name1 = session["name"]       
        return render_template('cpassword.html', name=name1)
    else:
        return redirect('login.html')

#password change
@app.route('/change', methods=['GET', 'POST'])
def change():
    if request.method == 'POST':
        #user = Users.query.get_or_404(id)
        if session.get("name"):
            user1 = session["name"]
            p = request.form.get('pass')        
            cp = request.form.get('cpass')
            if p == cp:
                u =Users.query.filter_by(user=user1).first()
                u.passwd = p
                db.session.commit()
                flash('Password Changed Successfully')
                return redirect('/logout')
            else:
                flash('Password Do not Match.')
                return redirect('/cpassword')
    else:
        flash('POST request Method Only Allowed')
        return redirect('/cpassword')

''''
#password change
@app.route('/change', methods=['GET', 'POST'])
def change():
    if request.method == 'POST':
        user1 = session["name"]
        users = Users.query.get_or_404(user1)
        p = request.form.get('pass')        
        cp = request.form.get('cpass')
        if p == cp:
            users.passwd = p
            db.session.commit()
            flash('Password Changed Successfully')
            return redirect('/cpassword')
        else:
            flash('Password Do not Match.')
            return redirect('/cpassword')
    else:
        flash('POST request Method Only Allowed')
        return redirect('/cpassword')'''

#renderingname
@app.route('/getname')
def getname():
    if session.get("name"):
        name1 = session["name"]
        return render_template('printname.html', name=name1)
    else:
        return redirect('login.html')

@app.route('/name/getname', methods=['GET', 'POST'])
def name1():
    name1 = session["name"]
    if request.method == 'POST':
        user_in = request.form.get('pname')
        template = f'Hello {user_in}!'
        out = render_template_string(template)
        return render_template('printname.html', pname=out, name=name1)
    else:
        return render_template('printname.html')
    

#postupdate
@app.route('/posts')
def posts():
    if session.get("name"):
        name1 = session["name"]       
        all_posts = Posts.query.order_by(Posts.date_post).all()
        return render_template('posts.html', post=all_posts, name=name1)
        #return render_template('posts.html', name=name1)
    else:
        return redirect('/login')

#Contactus Page
@app.route('/contact')
def contact():
    if session.get("name"):
        name1 = session["name"]       
        return render_template('contact.html', name=name1)
    else:
        return redirect('/login')

@app.route('/contactus', methods=['POST', 'GET'])
def contactus():
    if session.get("name"):
        name1 = session["name"]
        if request.method == 'POST':
            my_name = request.form.get('name')
            comment = request.form.get('comment')
            #return render_template('contact.html', myname=my_name, comment=comment, name=name1)
            return (my_name, comment)
        else:
            return redirect('contact')
    else:
        return redirect('/login')

@app.route('/search', methods=['GET'])
def cont():
    query = request.args
    print(query)
    print(query['query'])
    return query['query']


#logout function
@app.route("/logout")
def logout():
    session["name"] = None
    flash("Logged Out")
    return redirect("/")


    

if __name__  == '__main__':
    app.run(debug=True)


