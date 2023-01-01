from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager, login_user, logout_user, login_required

from forms import LoginForm

app = Flask(__name__)

UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/uploads/')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///internet_shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOADS_PATH
app.config['MAX_CONTENT_LENGHT'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

db = SQLAlchemy(app)


SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)

from flask_login import UserMixin
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(50), index=True, unique=True)
  email = db.Column(db.String(150), unique=True, index=True)
  password_hash = db.Column(db.String(150))
  joined_at = db.Column(db.DateTime(), default=datetime.utcnow, index=True)

  def set_password(self, password):
        self.password_hash = generate_password_hash(password)

  def check_password(self,password):
      return check_password_hash(self.password_hash,password)

  def __repr__(self):
      return '<User %r>' % self.username


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.Text)
    price = db.Column(db.Integer)
    free_size = db.Column(db.String)
    how = db.Column(db.Integer)
    img = db.Column(db.Text)

    def __repr__(self):
        return '<Product %r>' % self.id


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        free_size = request.form.get('free_size')
        how = request.form.get('how')

        def allowed_file(filename):
            return '.' in filename and \
                filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            img = join('/static/uploads/', filename)

            products = Products(name=name, description=description, price=price,
                                free_size=free_size, how=how, img=img)

        try:
            db.session.add(products)
            db.session.commit()
            return redirect('/')
        except:
            return render_template('products.html')
    else:
        products = Products.query.all()
        return render_template('products.html', db=products)


@app.route('/<int:id>', methods=['GET'])
def details(id):
    products = Products.query.get(id)

    return render_template('details.html', db=products)


@app.route("/<int:id>/update", methods=["GET", "POST"])
@login_required
def update_products(id):
    products = Products.query.get(id)
    if request.method == 'POST':
        products.name = request.form.get('name')
        products.description = request.form.get('description')
        products.price = request.form.get('price')
        products.free_size = request.form.get('free_size')
        products.how = request.form.get('how')

        def allowed_file(filename):
            return '.' in filename and \
                filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            img = join('/static/uploads/', filename)

            products.img = img


        try:
            db.session.commit()
            return redirect('/')
        except:
            return render_template('404.html')
    else:
        return render_template('admin_update.html', products=products)


@app.route("/<int:id>/delete")
@login_required
def delete_products(id):
    products = Products.query.get(id)
    try:
        filename = '.' + str(products.img)
        print(filename)
        os.remove(filename)
        db.session.delete(products)
        db.session.commit()
    finally:
        return render_template("products.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            next = request.args.get("next")
            return redirect(next or url_for('products'))
        flash('Invalid email address or Password.')
    return render_template('login.html', form=form)


@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('products'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html')


@app.errorhandler(401)
def not_found_error(error):
    return render_template('404.html')


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('404.html')


if __name__ == '__main__':
    app.run(debug=True, port=8080)