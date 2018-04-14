from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))
    text = db.Column(db.String(150))
    deleted = db.Column(db.Boolean)

    def __init__(self, title, text):
        self.text = text
        self.title = title
        self.deleted = False


@app.route('/blog')
def index():
    if request.args != {}:
        blog_query = request.args.get('id')
        blog_id = Blog.query.get(blog_query)
        return render_template('single-blog.html', blog_id=blog_id)

    blogs = Blog.query.filter_by(deleted=False).all()
    return render_template('blog.html', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def add_blog():
    title_error = ''
    text_error = ''

    if request.method == 'POST':
        title_name = request.form['title']
        text_name = request.form['text']
        
        if title_name == "":
            title_error = "Please enter a title"
        if text_name == "":
            text_error = "Please enter some text"

        if not title_error and not text_error:
            new_blog = Blog(title_name, text_name)
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








   