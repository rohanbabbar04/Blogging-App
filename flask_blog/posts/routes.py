from flask import redirect, render_template, url_for, abort, flash, Blueprint, request
from flask_login import login_required, current_user
from flask_blog import db, bcrypt
from flask_blog.models import Post
from flask_blog.posts.forms import PostForm

posts = Blueprint('posts', __name__)


@posts.route('/posts/new', methods=['POST', 'GET'])
@login_required
def create_post():
    nav_image = None
    if current_user.is_authenticated:
        nav_image = current_user.image_file
    form = PostForm()
    if form.validate_on_submit():
        post1 = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post1)
        db.session.commit()
        flash('Your post has been created !', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', legend="Create Post", form=form, nav_image=nav_image)


@posts.route('/posts/<int:post_id>')
@login_required
def post(post_id):
    nav_image = None
    if current_user.is_authenticated:
        nav_image = current_user.image_file
    post1 = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post1, nav_image=nav_image)


@posts.route('/posts/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    nav_image = None
    if current_user.is_authenticated:
        nav_image = current_user.image_file
    post1 = Post.query.get_or_404(post_id)
    if post1.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post1.title = form.title.data
        post1.content = form.content.data
        db.session.commit()
        flash("Your post has been updated", 'success')
        return redirect(url_for('posts.post', post_id=post1.id))
    elif request.method == 'GET':
        form.title.data = post1.title
        form.content.data = post1.content
    return render_template('create_post.html', legend='Update Post', title='Update Post', form=form,
                           nav_image=nav_image)


@posts.route('/posts/<int:post_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post1 = Post.query.get_or_404(post_id)
    if post1.author != current_user:
        abort(403)
    db.session.delete(post1)
    db.session.commit()
    flash('Your Post has been deleted', 'success')
    return redirect(url_for('main.home'))
