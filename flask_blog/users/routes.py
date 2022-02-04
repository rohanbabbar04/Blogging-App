from flask import request, abort, redirect, flash, render_template, Blueprint, url_for
from flask_login import current_user, login_user, login_required, logout_user
from flask_blog.models import User, Post
from flask_blog import bcrypt, db
from flask_blog.users.forms import LoginForm, RegistrationForm, RequestResetForm, RequestResetPassword, \
    UpdateProfileForm
from flask_blog.users.utils import save_image, sendResetEmail


users = Blueprint('users', __name__)


@users.route('/login', methods=['POST', 'GET'])
def login():
    print(request.args)
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash("Login Unsuccessful!", 'danger')
        return redirect(url_for('main.home'))
    return render_template('login.html', form=form, title='Login')


@users.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('UTF-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Successfully registered : {form.username.data}!", 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', form=form, title='Register')


@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        sendResetEmail(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route('/reset_token/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("This is an invalid or expired token", 'warning')
        return redirect(url_for('users.reset_request'))
    form = RequestResetPassword()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        flash("You password has been updated, you can now login", 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', form=form, title='Reset Password')


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateProfileForm()
    nav_image = None
    if current_user.is_authenticated:
        nav_image = current_user.image_file
    if form.validate_on_submit():
        if form.profile_pic.data:
            picture_file = save_image(form.profile_pic.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your details have been updated', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', form=form, image_file=image_file, nav_image=nav_image)


@users.route('/users/<string:username>')
@login_required
def user_post(username):
    nav_image = None
    if current_user.is_authenticated:
        nav_image = current_user.image_file
    page = request.args.get('page', 1, type=int)
    print(page)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user) \
        .order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=4)
    return render_template('users_post.html', posts=posts, user=user, nav_image=nav_image)
