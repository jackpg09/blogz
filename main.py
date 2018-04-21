from flask import Flask, request, redirect, render_template, session, flash 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))
    text = db.Column(db.String(150))
    deleted = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, text, owner):
        self.text = text
        self.title = title
        self.deleted = False
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'list_blogs', 'index', 'signup',]
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    accts = User.query.all()
    return render_template('index.html', accts=accts)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash('Logged in', 'success')
            print(session)
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        if username == '' or password == '' or verify == '':
            flash('One or more fields are blank.', 'error')
            return redirect('/signup')
        if len(username) < 3 or len(username) > 20 or (" " in username):
            flash('Invalid username', 'error')
            return redirect('/signup')
        if existing_user:
            flash('Username already exists.', 'error')
            return redirect('/signup')
        if len(password) < 3 or len(password) > 20 or (" " in password):
            flash('Invalid password', 'error')
            return redirect('/signup')
        if verify != password:
            flash('Password does not match.', 'error')
            return redirect('/signup')
        
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template('signup.html')

@app.route('/blog')
def list_blogs():

    blog_query = request.args.get('id')
    if blog_query:
        blog_id = Blog.query.get(blog_query)
        return render_template('single-blog.html', blog_id=blog_id)

    user_query = request.args.get('user')
    if user_query:
        user_id = Blog.query.get(user_query)
        blogs = Blog.query.filter_by(owner=user_id)
        return render_template('single-user.html', user_id=user_id, blogs=blogs)

    blogs = Blog.query.filter_by(deleted=False).all()
    return render_template('blog.html', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def add_blog():
    title_error = ''
    text_error = ''

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        title_name = request.form['title']
        text_name = request.form['text']
        
        if title_name == "":
            title_error = "Please enter a title"
        if text_name == "":
            text_error = "Please enter some text"

        if not title_error and not text_error:
            new_blog = Blog(title_name, text_name, owner)
            db.session.add(new_blog)
            db.session.commit()
            new_id = new_blog.id 
            return redirect('/blog?id={0}'.format(new_id))
            
        return render_template('submit.html', error1=title_error, error2=text_error)

    return render_template('submit.html')


@app.route('/delete', methods=['POST'])
def delete_blog():
    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    blog.deleted = True
    db.session.add(blog)
    db.session.commit()

    return redirect('/blog')

if __name__ == '__main__':
    app.run()








   