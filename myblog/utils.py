from markdown import markdown
from markdown.extensions import fenced_code, codehilite, tables, Extension
from markdown.inlinepatterns import InlineProcessor
import markdown_katex
from myblog.models import Post, Comment, User
from flask import url_for
from werkzeug.exceptions import abort
from flask_login import current_user
import re
import xml.etree.ElementTree as etree


class TagProcessor(InlineProcessor):

    def handleMatch(self, m, data) -> tuple:
        user = User.query.filter_by(username=m.group(2)).first()
        if user:
            el = etree.Element('tag')
            el.append(etree.Element('a'))
            el.find('a').text = m.group(2)
            el.find('a').set('href', url_for('blog.user', user_id=user.id))
            return el, m.start(0), m.end(0)
        return None, None, None


class TagExtension(Extension):

    def extendMarkdown(self, md):
        DEL_PATTERN = r'(@)(\w+)'  # like @user
        md.inlinePatterns.register(TagProcessor(DEL_PATTERN, md), 'tag', 175)


def format_markdown(text: str) -> str:
    return markdown(text,
                    extensions=[fenced_code.makeExtension(),
                                codehilite.makeExtension(user_pygments=True),
                                tables.makeExtension(),
                                markdown_katex.makeExtension(),
                                TagExtension()])


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


def get_all_comments(post_id: str) -> list:
    """Get all comments under a post."""
    get_post(post_id, check_author=False)
    comments = Comment.query.filter_by(post_id=post_id)\
        .order_by(Comment.created_timestamp.desc()).all()
    return comments


def get_mentioned_users(comment_text: str) -> list:
    mention_regex = '@[0-9a-zA-Z]+'
    user_names = [m[1:] for m in re.compile(mention_regex).findall(comment_text)]
    tagged_users = [User.query.filter_by(username=un).first() for un in user_names]
    return [tu for tu in tagged_users if tu]
