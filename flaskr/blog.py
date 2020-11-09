from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id , title, body, created, author_id, username'
        ' FROM posts p JOIN users u ON p.author_id=u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

def get_post(post_id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM posts p JOIN users u ON p.author_id=u.id'
        ' WHERE p.id=?',
        (post_id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {post_id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

def get_comment(comment_id, check_author=True):
    comment = get_db().execute(
        'SELECT c.id, c.body, c.created, c.author_id, c.post_id, username'
        ' FROM comments c JOIN users u ON c.author_id=u.id'
        ' JOIN posts p ON c.post_id=p.id'
        ' WHERE c.id=?',
        (comment_id,)
    ).fetchone()

    if comment is None:
        abort(404, f"Comment id {comment_id} doesn't exist.")

    if check_author and comment['author_id'] != g.user['id']:
        abort(403)

    return comment

def get_comments(post_id):
    get_post(post_id)
    comments = get_db().execute(
        'SELECT c.id, c.body, c.created, c.author_id, c.post_id, username'
        ' FROM comments c JOIN users u ON c.author_id=u.id'
        ' JOIN posts p ON c.post_id=p.id'
        ' WHERE p.id=?',
        (post_id,)
    ).fetchall()

    return comments

@bp.route('/create', methods=('GET','POST'))
@login_required
def create():
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO posts (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html', post=None)

@bp.route('/<int:post_id>/show_post', methods=('GET',))
@login_required
def show_post(post_id):
    post = get_post(post_id)
    comments = get_comments(post_id)
    return render_template('blog/show_post.html', post=post, comments=comments)

@bp.route('/<int:post_id>/update', methods=('GET','POST'))
@login_required
def update(post_id):
    post = get_post(post_id)

    if request.method=="POST":
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE posts SET title=?, body=?'
                ' WHERE id=?',
                (title, body, post_id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
    
    return render_template('blog/create.html', post=post)

@bp.route('/<int:post_id>/delete', methods=('POST',))
@login_required
def delete(post_id):
    get_post(post_id)
    db = get_db()
    db.execute('DELETE FROM posts WHERE id=?', (post_id,))
    db.commit()
    return redirect(url_for('blog.index'))

@bp.route('/<int:post_id>/comment', methods=('GET','POST'))
@login_required
def comment(post_id):
    post = get_post(post_id)

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

    post = get_post(post_id)
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
