from flask import Blueprint, render_template
from myblog.models import Post


bp = Blueprint('index', __name__)


# Index page
@bp.route('/')
def index():
    """Render the main index."""
    posts = Post.query.order_by(Post.created_timestamp.desc()).all()
    return render_template('blog/index.html', posts=posts)
