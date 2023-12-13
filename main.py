from flask import render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath
import os
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms import LoginForm
from log import Email

from app import *
from databases import *


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

        products = Products(name=name, description=description, price=price,
                            free_size=free_size, how=how)
        try:
            db.session.add(products)
            db.session.commit()
            return redirect('/')
        except Exception as body:
            Email().sender(body)
            return render_template('clientPages/products.html')
    else:
        collection = []
        json_product = {}
        product = Products.query.all()
        for i in product:
            json_product['id'] = i.id
            json_product['name'] = i.name
            json_product['description'] = i.description
            json_product['price'] = i.price
            json_product['free_size'] = i.free_size
            json_product['how'] = i.how
            json_product['img'] = i.img
            json_product['img1'] = i.img1
            json_product['img2'] = i.img2
            json_product['img3'] = i.img3
            json_product['img4'] = i.img4
            json_product['img5'] = i.img5
            json_product['img6'] = i.img6
            collection.append(json_product)
            json_product = {}

        return render_template('clientPages/products.html', data=json_product)


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
        except Exception as body:
            Email().sender(body)
            return render_template('errorPages/404.html')
    else:
        return render_template('adminPages/admin_update.html', products=products)


@app.route("/<int:id>/delete")
@login_required
def delete_products(id):
    products = Products.query.get(id)
    try:
        filename = '/home/denysend/Lending' + products.img
        os.remove(filename)
        db.session.delete(products)
        db.session.commit()
    except Exception as body:
        Email().sender(body)
    finally:
        return render_template("clientPages/products.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        try:
            if form.validate_on_submit():
                user = User.query.filter_by(email=form.email.data).first()
                if user is not None and user.check_password(form.password.data):
                    login_user(user)
                    next = request.args.get("next")
                    return redirect(next or url_for('products'))
                flash('Invalid email address or Password.')
            return render_template('adminPages/login.html', form=form)
        except Exception as body:
            Email().sender(body)
            return redirect(url_for('products'))
    else:
        return render_template('adminPages/login.html', form=form)


@app.route('/admin')
@login_required
def admin():
    return render_template('adminPages/admin.html')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('products'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errorPages/404.html')


@app.errorhandler(401)
def not_found_errorr(error):
    return render_template('errorPages/404.html')


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errorPages/404.html')


if __name__ == '__main__':
    app.run()