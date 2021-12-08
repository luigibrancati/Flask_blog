from datetime import datetime
from flask import Blueprint, flash, redirect,\
                  render_template, request, url_for
from myblog import db
from myblog.email_notifications import OpCommentNotificationEmailSender, TagNotificationEmailSender
from myblog.models import Post, Comment
from myblog.forms import EditProfileForm, CreatePostForm, EditPostForm,\
                         CreateCommentForm, EditCommentForm
from flask_login import login_required, current_user
from .utils import format_markdown, get_comment, get_post,\
                   get_user, get_all_comments, get_mentioned_users


bp = Blueprint('blog', __name__)


# Index page
@bp.route('/')
def index():
    """Render the main index."""
    posts = Post.query.order_by(Post.created_timestamp.desc()).all()
    return render_template('blog/index.html', posts=posts)


# Show user profile page
@bp.route('/user/<user_id>')
@login_required
def user(user_id):
    """Render the user profile."""
    user = get_user(user_id)
    posts = Post.query.filter_by(author=user).all()
    comments = Comment.query.filter_by(author=user).all()
    posts.sort(key=lambda p: p.created_timestamp, reverse=True)
    comments.sort(key=lambda c: c.created_timestamp, reverse=True)
    return render_template('blog/user.html', user=user, posts=posts,
                           comments=comments)


# Edit profile form
@bp.route('/edit_profile/<user_id>', methods=('GET', 'POST'))
@login_required
def edit_profile(user_id):
    """Edits the user profile."""
    form = EditProfileForm(current_user.username, current_user.email)
    user = get_user(user_id)
    if current_user.id != user.id:
        flash("You can only modify your own profile!")
        return redirect(url_for('blog.user', user_id=user.id))
    elif form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        # user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('blog.user',
                                user_id=user.id))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        # form.about_me.data = user.about_me
    return render_template('blog/edit_profile.html', user=user, form=form)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create new post."""
    form = CreatePostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    body=form.body.data,
                    author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post created.')
        return redirect(url_for('blog.index'))
    return render_template('blog/create_post.html', form=form, post=None)


@bp.route('/<int:post_id>/show_post', methods=('GET',))
def show_post(post_id):
    """Render a post thread."""
    post = get_post(post_id, check_author=False)
    post.body = format_markdown(post.body)
    comments = get_all_comments(post_id)
    comments.sort(key=lambda c: c.created_timestamp)
    for comment in comments:
        comment.body = format_markdown(comment.body)
    return render_template('blog/show_post.html', post=post, comments=comments)


@bp.route('/<int:post_id>/update', methods=('GET', 'POST'))
@login_required
def update(post_id):
    """Edit a post."""
    post = get_post(post_id)
    form = EditPostForm(post.title)
    if current_user != post.author:
        flash("You can't edit a post that is not yours!")
        return redirect(url_for('blog.show_post', post_id=post_id))
    elif form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.updated_timestmap = datetime.utcnow()
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for('blog.show_post', post_id=post_id))
    elif request.method == "GET":
        form.title.data = post.title
        form.body.data = post.body
    return render_template('blog/create_post.html', form=form, post=post)


@bp.route('/<int:post_id>/delete', methods=('POST',))
@login_required
def delete(post_id):
    """Delete a post."""
    post = get_post(post_id)
    comments = get_all_comments(post_id)
    db.session.delete(post)
    for comment in comments:
        db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('blog.index'))


@bp.route('/<int:post_id>/comment', methods=('GET', 'POST'))
@login_required
def comment(post_id):
    """Add a comment under a post. Also sends an email notification to original poster."""
    form = CreateCommentForm()
    post = get_post(post_id, check_author=False)
    post.body = format_markdown(post.body)
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, author=current_user,
                          original_post=post)
        db.session.add(comment)
        db.session.commit()
        flash('Comment created.')
        # Send mail notification to OP
        op = get_user(post.user_id)
        if comment.user_id != op.id:
            OpCommentNotificationEmailSender\
                .build_message(
                    url_for('blog.show_post', post_id=post.id, _external=True),
                    comment.id,
                    op,
                    current_user)\
                .send_mail()
        # Send emails to tagged users
        for user in get_mentioned_users(comment.body):
            TagNotificationEmailSender\
                .build_message(
                    url_for('blog.show_post', post_id=post.id, _external=True),
                    comment.id,
                    user,
                    current_user)\
                .send_mail()
        return redirect(url_for('blog.show_post', post_id=post_id))
    comments = get_all_comments(post_id)
    return render_template('blog/create_comment.html', form=form, post=post,
                           comments=comments, comment=None)


@bp.route('/<int:comment_id>/update_comment', methods=('GET', 'POST'))
@login_required
def update_comment(comment_id):
    """Update a comment under a post."""
    comment = get_comment(comment_id)
    post_id = comment.original_post.id
    form = EditCommentForm()
    if form.validate_on_submit():
        if current_user != comment.author:
            flash("You can't edit a comment that is not yours!")
            return redirect(url_for('blog.show_post', post_id=post_id))
        comment.body = form.body.data
        comment.updated_timestmap = datetime.utcnow()
        db.session.commit()
        flash('Your changes have been made.')
        return redirect(url_for('blog.show_post', post_id=post_id))
    elif request.method == "GET":
        form.body.data = comment.body
    post = get_post(post_id, check_author=False)
    post.body = format_markdown(post.body)
    comments = get_all_comments(post_id)
    return render_template('blog/create_comment.html', form=form, post=post,
                           comments=comments, comment=comment)


@bp.route('/<int:comment_id>/delete_comment', methods=('POST',))
@login_required
def delete_comment(comment_id):
    """Delete a comment."""
    comment = get_comment(comment_id)
    post_id = comment.original_post.id
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('blog.show_post', post_id=post_id))
