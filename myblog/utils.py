from markdown import markdown
from markdown.extensions import fenced_code, codehilite
from myblog.models import Post, Comment, User
from werkzeug.exceptions import abort
from flask_login import current_user


def format_markdown(text: str) -> str:
    return markdown(text,
                    extensions=[fenced_code.makeExtension(),
                                codehilite.makeExtension(user_pygments=True)])


def get_post(post_id: str, check_author=True) -> Post:
    """Gets a post by post id."""
    post = Post.query.filter_by(id=post_id).first_or_404()
    if check_author and post.author.id != current_user.id:
        abort(403)
    return post


def get_comment(comment_id: str, check_author=True) -> Comment:
    """Get a comment by comment id."""
    comment = Comment.query.filter_by(id=comment_id).first_or_404()
    if check_author and comment.author.id != current_user.id:
        abort(403)
    return comment


def get_user(user_id: str) -> User:
    return User.query.filter_by(id=user_id).first_or_404()


def get_all_comments(post_id: str) -> list[Comment]:
    """Get all comments under a post."""
    get_post(post_id, check_author=False)
    comments = Comment.query.filter_by(post_id=post_id)\
        .order_by(Comment.timestamp.desc()).all()
    return comments
