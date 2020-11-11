from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr import db
from flaskr.models import User, Post, Comment
from flaskr.forms import EditProfileForm, CreatePostForm, EditPostForm
from flask_login import login_required, current_user
from datetime import datetime

bp = Blueprint('blog', __name__)

#index page
@bp.route('/')
def index():
    posts = Post.query.all()
    return render_template('blog/index.html', posts=posts)

#show user profile page
@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).all()
    return render_template('blog/user.html', user=user, posts=posts)

#edit profile form
@bp.route('/edit_profile/<username>', methods=('GET','POST'))
@login_required
def edit_profile(username):
    form = EditProfileForm(current_user.username)
    user = User.query.filter_by(username=username).first_or_404()
    if form.validate_on_submit():
        if current_user.id != user.id:
            flash("You can only modify your own profile!")
            return redirect(url_for('blog.user', username=username))
        user.username = form.username.data
        user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('blog.edit_profile', username=username))
    elif request.method == 'GET':
        form.username.data = user.username
        form.about_me.data = user.about_me
    return render_template('blog/edit_profile.html', user=user, form=form)

def get_post(post_id, check_author=True):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if check_author and post.author.id != current_user.id:
        abort(403)
    return post

def get_comment(comment_id, check_author=True):
    comment = Comment.query.filter_by(id=comment_id).first_or_404()
    if check_author and comment.author.id != current_user.id:
        abort(403)
    return comment

def get_comments(post_id):
    get_post(post_id,check_author=False)
    comments = Comment.query.filter_by(post_id=post_id).all()
    return comments

@bp.route('/create', methods=('GET','POST'))
@login_required
def create():
    form = CreatePostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post created.')
        return redirect(url_for('blog.index'))
    return render_template('blog/create.html', form=form, post=None)

@bp.route('/<int:post_id>/show_post', methods=('GET',))
@login_required
def show_post(post_id):
    post = get_post(post_id, check_author=False)
    comments = get_comments(post_id)
    return render_template('blog/show_post.html', post=post, comments=comments)

@bp.route('/<int:post_id>/update', methods=('GET','POST'))
@login_required
def update(post_id):
    post = Post.query.filter_by(id=post_id).first_or_404()
    form = EditPostForm(post.title)
    if form.validate_on_submit():
        if current_user != post.author:
            flash("You can't edit a post that is not yours!")
            return redirect(url_for('blog.show_post', post_id=post_id))
        post.title = form.title.data
        post.body = form.body.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for('blog.show_post', post_id=post_id))
    return render_template('blog/create.html', form=form, post=post)

@bp.route('/<int:post_id>/delete', methods=('POST',))
@login_required
def delete(post_id):
    post = get_post(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('blog.index'))

@bp.route('/<int:post_id>/comment', methods=('GET','POST'))
@login_required
def comment(post_id):
    post = get_post(post_id, check_author=False)

    if request.method == "POST":
        body = request.form['body']
        error = None

        if not body:
            error = 'Body is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO comments (post_id, body, author_id)'
                ' VALUES (?, ?, ?)',
                (post_id, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.show_post', post_id=post_id))
    
    comments = get_comments(post_id)
    return render_template('blog/comment.html', post=post, comments=comments, comment=None)

@bp.route('/<int:comment_id>/update_comment', methods=('GET','POST'))
@login_required
def update_comment(comment_id):
    comment = get_comment(comment_id)
    post_id = comment['post_id']

    if request.method == "POST":
        body = request.form['body']
        error = None

        if not body:
            error = 'Body is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE comments SET body=?'
                ' WHERE id=?',
                (body, comment_id)
            )
            db.commit()
            return redirect(url_for('blog.show_post', post_id=post_id))

    post = get_post(post_id, check_author=False)
    comments = get_comments(post_id)
    return render_template('blog/comment.html', post=post, comments=comments, comment=comment)

@bp.route('/<int:comment_id>/delete_comment', methods=('POST',))
@login_required
def delete_comment(comment_id):
    post_id = get_comment(comment_id)['post_id']
    db = get_db()
    db.execute('DELETE FROM comments WHERE id=?', (comment_id,))
    db.commit()
    return redirect(url_for('blog.show_post', post_id=post_id))
