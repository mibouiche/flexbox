from flask_admin import Admin
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class
from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists
from flask import Flask, render_template, request, session, url_for
from werkzeug.utils import redirect
from models import db, User
from flask_mail import Mail, Message
import os
import uuid
from flask_admin.contrib.sqla import ModelView
from flask_admin import form
from markupsafe import Markup
from werkzeug.utils import secure_filename
from models import Product, Category

app = Flask(__name__, template_folder="templates/",
                      static_folder="templates/")
DB_URI = 'sqlite:///fashion.db'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'super secret key'
app.config['MAIL_SERVER']='smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'djamel.sbar@gmail.com'
app.config['MAIL_PASSWORD'] = '******'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['UPLOADED_IMAGES_DEST'] = 'templates/images/'
app.config['UPLOADED_IMAGES_URL'] = 'templates/images/'

admin_emai='djamelsbargoud'
admin_password='jesuisadmin'

mail = Mail()
mail.init_app(app)
sess = Session()
db.init_app(app)
images = UploadSet('images', IMAGES)

configure_uploads(app, (images))
patch_request_class(app, 16 * 1024 * 1024)

admin = Admin(app,template_mode='bootstrap3')
if not database_exists(DB_URI):
    with app.app_context():
        db.drop_all()
        db.create_all()
        for i in range(1, 10):
            db.session.add(Product(name=f"Robe {i}",size='XL',price=1500+(i*10)))
        db.session.add(Category(name=f"categorie de Robe {i}",size='XL',price=1500))
        db.session.add(User(name="Djamel"))
        db.session.add(User(name="Yahya"))
        db.session.commit()

"""
        route for frent end
"""
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        msg = Message(subject, sender=email,
                      recipients=['djamelsbargoud@gmail.com'],
                      body=" "+email+" vous a envoyé ce mesage   \n"+message
                      )
        mail.send(msg)

    return render_template('contact.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    sign = request.args.get('sign')
    if  request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == admin_emai and password == admin_password:
            session['user'] = admin_emai
            return redirect(url_for('admin.index'))
        user = User.query.filter(and_(User.email == email,
                                      User.password == password)).first()
        if sign=='in' and user!=None:
            session['user']=user.name
            return redirect(url_for('index'))
        elif sign=='up' and user==None:
            name = request.form['Name']
            phone = request.form['Phone']
            db.session.add(User(name=name,
                                password=password,
                                email=email,
                                phone=phone
                                ))
            db.session.commit()
            session['user'] = name
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('user', None)
   return redirect(url_for('login'))


@app.route('/category')
def category():
    cat = request.args.get('category')
    if cat :
        products = Product.query.join(Category).filter(Product.category_id == int(cat)).all()
        return render_template('gallery.html',products=products)
    category = Category.query.all()
    return render_template('category.html',categories=category)


@app.route('/gallery')
def gallery():
    products = Product.query.all()
    return render_template('gallery.html',products=products)


"""   admin part  """


def _logo_list_thumbnail(view, context, model, name):
     if not model.image_name:
            return ''

     return Markup(
          '<a href="../../images/{model.image_name}"><img src="../../images/{model.image_name} " style="width: 70px;"></a>'.format(
              model=model)
     )


class ProductView(ModelView):
    column_searchable_list = ('name', 'price','size',Category.name)
    column_exclude_list = ['categories',]
    form_excluded_columns = ['categories',]

    def is_accessible(self):
        return session.get('user') == admin_emai

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('index', next=request.url))

    column_formatters = {
        'image_name': _logo_list_thumbnail
    }

    form_extra_fields = {
        'image_name': form.ImageUploadField(
            'Image',
            base_path='templates/images/',
            url_relative_path='templates/images/',
        )
    }


class UserView(ModelView):
    def is_accessible(self):
        return session.get('user') == admin_emai

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('index', next=request.url))


class CategoryView(ModelView):
    inline_models = ['product', ]
    column_searchable_list = ('name', 'price','size')
    inline_models = (Product, dict(form_excluded_columns=['categories'],
                                   form_extra_fields={
                                       'image_name': form.ImageUploadField(
                                           'Image',
                                           base_path='templates/images/',
                                           url_relative_path='templates/images/',
                                       )
                                   }
                                   ),),
    column_formatters = {
        'image_name': _logo_list_thumbnail
    }
    def is_accessible(self):
        return session.get('user') == admin_emai

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('index', next=request.url))

    form_extra_fields = {
        'image_name': form.ImageUploadField(
            'Image',
            base_path='templates/images/',
            url_relative_path='templates/images/',
        )
    }



admin.add_view(UserView(User,db.session))
admin.add_view(CategoryView(Category,db.session))
admin.add_view(ProductView(Product,db.session))

if __name__ == '__main__':
    app.run(debug=True,port=8080)