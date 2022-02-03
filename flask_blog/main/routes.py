from flask import render_template, request, Blueprint
from flask_login import current_user
from flask_blog.models import Post, User
from flask_blog.main.forms import SearchForm

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
@main.route('/home', methods=['GET', 'POST'])
def home():
    form = SearchForm()
    nav_image = None
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=5)
    if form.validate_on_submit():
        posts = Post.query.filter(Post.title.contains(form.string.data) | Post.content.contains(form.string.data)) \
            .order_by(Post.date_posted.desc()) \
            .paginate(page=page, per_page=5)
    if current_user.is_authenticated:
        nav_image = current_user.image_file
        print(nav_image)
    users = User.query.all()
    return render_template('home.html', posts=posts, nav_image=nav_image, users=users, form=form)


@main.route('/about', methods=['POST', 'GET'])
def about():
    return render_template('about.html', title='About')
