from datetime import datetime
from flask import Blueprint, flash, redirect,\
                  render_template, request, url_for,\
                  current_app
from myblog import db
from myblog.models import Post
from myblog.forms import CreatePostForm, EditPostForm
from flask_login import login_required, current_user
from ..utils import format_markdown, get_post, get_all_comments
from werkzeug.exceptions import abort


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
        current_app.logger.info("New post created")
        db.session.add(post)
        db.session.commit()
        current_app.logger.info(f"Post {post.id} pushed to database")
        current_app.logger.info(f"Post {post.id} has been created by user {current_user.id}")
        flash('Post created.')
        return redirect(url_for('index.index'))
    return render_template('blog/create_post.html', form=form, post=None)


@bp.route('/post/<int:post_id>', methods=('GET',))
def show_post(post_id):
    """Render a post thread."""
    with current_app.app_context():
        post = get_post(post_id)
        is_admin = (current_user.email in current_app.config["ADMINS"])
        if post.private and current_user != post.author:
            return render_template('error/404.html')
        post.body = format_markdown(post.body)
        comments = get_all_comments(post_id)
        comments.sort(key=lambda c: c.created_timestamp)
        for comment in comments:
            comment.body = format_markdown(comment.body)
        return render_template('blog/show_post.html', post=post, comments=comments, is_admin=is_admin)


@bp.route('/post/<int:post_id>/edit', methods=('GET', 'POST'))
@login_required
def edit_post(post_id):
    """Edit a post."""
    with current_app.app_context():
        post = get_post(post_id)
        is_admin = (current_user.email in current_app.config["ADMINS"])
        if current_user == post.author or is_admin:
            form = EditPostForm(post.title)
            if form.validate_on_submit():
                post.title = form.title.data
                post.body = form.body.data
                post.private = form.private.data
                post.updated_timestmap = datetime.utcnow()
                db.session.commit()
                current_app.logger.info(f"Post {post.id} has been edited by user {current_user.id}")
                flash("Your changes have been saved.")
                return redirect(url_for('post.show_post', post_id=post_id))
            elif request.method == "GET":
                form.title.data = post.title
                form.body.data = post.body
                form.private.data = post.private
            return render_template('blog/create_post.html', form=form, post=post)
        else:
            current_app.logger.warning(f"User {current_user.id} attempted editing post {post.id}, but was bounced back")
            abort(403)


@bp.route('/post/<int:post_id>/delete', methods=('POST',))
@login_required
def delete_post(post_id):
    """Delete a post."""
    with current_app.app_context():
        post = get_post(post_id)
        is_admin = (current_user.email in current_app.config["ADMINS"])
        if current_user == post.author or is_admin:
            for comment in get_all_comments(post_id):
                db.session.delete(comment)
            db.session.delete(post)
            db.session.commit()
            current_app.logger.info(f"Post {post.id} has been deleted by user {current_user.id}")
            return redirect(url_for('index.index'))
        else:
            current_app.logger.warning(f"User {current_user.id} attempted deleting post {post.id}, but was bounced back")
            abort(403)
