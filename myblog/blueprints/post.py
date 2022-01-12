from datetime import datetime
from flask import Blueprint, flash, redirect,\
                  render_template, request, url_for
from myblog import db
from myblog.models import Post
from myblog.forms import CreatePostForm, EditPostForm
from flask_login import login_required, current_user
from ..utils import format_markdown, get_post, get_all_comments


bp = Blueprint('post', __name__)


@bp.route('/create_post', methods=('GET', 'POST'))
@login_required
def create_post():
    """Create new post."""
    form = CreatePostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            body=form.body.data,
            private=form.private.data,
            author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash('Post created.')
        return redirect(url_for('index.index'))
    return render_template('blog/create_post.html', form=form, post=None)


@bp.route('/post/<int:post_id>', methods=('GET',))
def show_post(post_id):
    """Render a post thread."""
    post = get_post(post_id, check_author=False)
    post.body = format_markdown(post.body)
    comments = get_all_comments(post_id)
    comments.sort(key=lambda c: c.created_timestamp)
    for comment in comments:
        comment.body = format_markdown(comment.body)
    return render_template('blog/show_post.html', post=post, comments=comments)


@bp.route('/post/<int:post_id>/edit', methods=('GET', 'POST'))
@login_required
def edit_post(post_id):
    """Edit a post."""
    post = get_post(post_id)
    form = EditPostForm(post.title)
    if current_user != post.author:
        flash("You can't edit a post that is not yours!")
        return redirect(url_for('post.show_post', post_id=post_id))
    elif form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.private = form.private.data
        post.updated_timestmap = datetime.utcnow()
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for('post.show_post', post_id=post_id))
    elif request.method == "GET":
        form.title.data = post.title
        form.body.data = post.body
        form.private.data = post.private
    return render_template('blog/create_post.html', form=form, post=post)


@bp.route('/post/<int:post_id>/delete', methods=('POST',))
@login_required
def delete_post(post_id):
    """Delete a post."""
    post = get_post(post_id)
    comments = get_all_comments(post_id)
    db.session.delete(post)
    for comment in comments:
        db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('index.index'))
