from flask import Blueprint, render_template
from myblog.models import Post
from ..utils import is_admin

bp = Blueprint('index', __name__)


# Index page
@bp.route('/')
def index():
    """Render the main index."""
    posts = Post.query.filter_by(private=False).order_by(Post.created_timestamp.desc()).all()
    return render_template('blog/index.html', posts=posts, is_admin=is_admin())
