from flask import Flask, render_template, request, flash, redirect, url_for
from form import LoginForm, RegisterForm, AddForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'development_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

IMAGE_DIR = './static/uploaded_images'
PDF_DIR = './static/uploaded_pdf'

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_PDF_EXTENSIONS = {'pdf'}

def allowed_img_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def allowed_pdf_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_PDF_EXTENSIONS


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))

class PostsDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aimsTowards = db.Column(db.String(100))
    description = db.Column(db.Text)
    author = db.Column(db.String(100))
    creationTime = db.Column(db.String(100))

class PostImagesDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.Text)
    creationTime = db.Column(db.String(100))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()

    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        login = User.query.filter_by(username=username, password=password).first()
        
        if login is None:
            flash("Invalid Credentials. Please Try again.", category="danger")
            return render_template("login.html", form = form)
        else:
            login_user(login)
            if current_user.is_authenticated:
                return redirect(url_for('home'))

    return render_template("login.html", form = form)


@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        register = User(username = username, password = password)
        
        if not form.validate_on_submit() :
            return render_template("register.html", form = form) 
        else:
            if User.query.filter_by(username=username).first():
                flash("Username is already taken", category="danger") 
                return render_template("register.html", form = form)
            else:
                db.session.add(register)
                db.session.commit()
                flash("Successfully registered", category="primary")
                return redirect(url_for("login"))

    return render_template("register.html", form = form) 

@app.route('/home', methods =['GET','POST'])
@login_required
def home():
    return render_template("home.html")

@app.route('/home/posts')
@login_required
def status():
    posts = db.session.query(PostsDB).all()
    posts = posts[::-1]
    return render_template("blogpoint.html", posts=posts)


@app.route('/home/images', methods = ['GET','POST'])
@login_required
def images():
    posts = db.session.query(PostImagesDB).all()
    image = os.listdir(IMAGE_DIR)
    return render_template("imagepoint.html", image = image, posts = posts )

@app.route('/home/pdfs', methods = ['GET', 'POST'])
@login_required
def PDFs():
    pdf = os.listdir(PDF_DIR)
    return render_template("pdfpoint.html", pdf = pdf)

@app.route('/add/status' , methods =['GET','POST'])
@login_required
def upload_status():
    form = AddForm()

    if request.method == 'POST' :
        aimsTowards = request.form.get('aimsTowards')
        description = request.form.get('description')
        author = request.form.get('author')
        created = datetime.now()
        creationTime = created.strftime(r"%d-%m-%Y %H:%M:%S")

        if (author == ''):
            author = "Anonymous"

        if (aimsTowards == ''):
            aimsTowards = "Anonymous"

        newPost = PostsDB(aimsTowards = aimsTowards , description = description, author = author , creationTime = creationTime, ) 
        db.session.add(newPost)
        db.session.commit()
        return redirect(url_for('status'))
    
    return render_template('uploadstatus.html', form=form)

@app.route('/add/pdf', methods=['GET','POST'])
@login_required
def upload_pdf():
    if request.method == "POST":

        pdffile = request.files['inputFile']        

        if not pdffile:
            flash('No file uploaded', category="danger")
            return redirect(request.url)

        if pdffile.filename == '':
            flash('No selected file', category="danger")
            return redirect(request.url)

        if allowed_pdf_file(pdffile.filename):
                
            created = datetime.now()
            createdTime = created.strftime(r"%d-%m-%Y_%H:%M:%S")

            pdfFileName = createdTime + "_" + pdffile.filename
            pdfpath = '{}/{}'.format(PDF_DIR, pdfFileName)
            pdffile.save(pdfpath)

            return redirect(url_for('PDFs'))

        else:
            flash("This type of file is not supported", category="danger")
            return redirect(request.url)


    return render_template("uploadpdf.html")

@app.route('/add/image', methods = ['POST', 'GET'])
@login_required
def upload_image():
    if request.method == "POST":

        imgfile = request.files['inputFile']

        if not imgfile:
            flash('No file uploaded', category="danger")
            return redirect(request.url)

        if imgfile.filename == '':
            flash('No selected file', category="danger")
            return redirect(request.url)

        if allowed_img_file(imgfile.filename):

            created = datetime.now()
            createdTime = created.strftime(r"%d-%m-%Y %H:%M:%S")

            newfilename = createdTime 
            imgpath = '{}/{}'.format(IMAGE_DIR, newfilename)
            imgfile.save(imgpath) 

            caption = request.form.get('caption')

            if (caption == ''):
                caption = '#CollegeConnect'

            newPost = PostImagesDB(caption = caption, creationTime = createdTime) 
            db.session.add(newPost)
            db.session.commit()
    
            return redirect(url_for('images'))

        else:
            flash("This type of file is not supported", category="danger")
            return redirect(request.url)

    return render_template('uploadimage.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index')) 

if __name__ == '__main__':
   db.create_all()
   app.run(debug = True)
