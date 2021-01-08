from flask import Flask,render_template,flash, redirect,url_for,session,logging,request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from flask_login import UserMixin
from datetime import datetime
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ksadjfk213kjfw8ejq3u8jf78342hrjskljf3k4jf983fkaj984j3qflkajfkljk3984jlkfzjdfklu4irbvjh87eryt[ihskdnfgkjahq3984tyqu'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login_page'

class User (db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    avatar_path = db.Column(db.String())
    bio = db.Column(db.String(300))

class Articles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    creator_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Articles %r>' % self.id

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/")
def index():
    posts = Articles.query.order_by(Articles.date).all()

    return render_template('index.html', articles=list(reversed(posts)))

@app.route("/profile/<username>")
@login_required
def get_profile(username):
    if username == current_user.username:
        return render_template('my_profile.html', user = current_user, creator=True)
    else:
        user = User.query.get(username)
        return render_template('profile.html', user = user)

@app.route("/posts")
def get_posts():
    posts = Articles.query.order_by(Articles.date).all()

    return render_template('posts.html', articles= list(reversed(posts)))

 
@app.route('/post/<id>')
def get_post(id):
    post = Articles.query.filter_by(id=id).first()
    return render_template('post.html', post = post)

@app.route('/post/<id>/del')
def post_del(id):
    post = Articles.query.get_or_404(id)

    try:
        if post.creator_id == current_user.id:
            db.session.delete(post)
            db.session.commit()
        else:
            return redirect('/posts')
        return redirect('/posts')
    except:
        return 'При удалении произошла ошибка'
    return render_template('post.html', post = post)

@app.route("/create-article", methods=['GET', 'POST'])
#@login_required
def create_article():
    if request.method == 'POST':
        title = request.form.get('title')
    
        text = request.form.get('text')
        intro = text[0:100]
        new_article = Articles(title=str(title), intro=intro, text=text, creator_id = current_user.id)
        db.session.add(new_article)
        db.session.commit()
        return redirect('/posts')
    else:
        return render_template('create-aricle.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    login = request.form.get('user')
    password = request.form.get('pass')

    if login and password:
        user = User.query.filter_by(username=login).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            return redirect('/')

        else:
            flash('Не верны Логин/Пароль')
    else:
        pass
    return render_template('login.html', filename='css/styles.css')


@app.route('/register', methods=['GET', 'POST'])
def register():
    login = request.form.get('user')
    password = request.form.get('pass')
    password2 = request.form.get('pass2')

    if request.method == 'POST':
        if not (login or password or password2):
            flash('Пожалуйста, заполните все поля!')
        elif login == '':
            flash('Пожалуйста, заполните все поля!')
        elif password != password2:
            flash('Пароли не совпадают!')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(username=login, password=hash_pwd)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login_page'))

    return render_template('regisetr_form.html')

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('login_page'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404
'''
@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form['user']).first()
        if user and check_password_hash(user.password, request.form['pass']):
            userlogin = UserLogin().create(user)
            #login_user(userlogin)
            return redirect(url_for('test', alias='234213'))
 
        flash("Неверная пара логин/пароль", "error")
 
    return render_template("login.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        session.pop('_flashes', None)
        if len(request.form['user']) > 4 and len(request.form['email']) > 4 \
            and len(request.form['pass']) > 4 and request.form['pass'] == request.form['pass2']:
            hash = generate_password_hash(request.form['pass'])
            res = User(username = request.form['user'], email = request.form['email'], password = hash)
            try:
                db.session.add(res)
                db.session.commit()
            except:
                return 'ERROR'
            if res:
                flash("Вы успешно зарегистрированы", "success")
                print('НОВАЯ РЕГИСТРАЦИЯ ДЕБИЛ')
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")
 
    return render_template("regisetr_form.html")
'''

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)