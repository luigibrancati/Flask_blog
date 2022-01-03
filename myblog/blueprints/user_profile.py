from flask import Blueprint, flash, redirect,\
                  render_template, request, url_for
from myblog import db
from myblog.models import Post, Comment
from myblog.forms import EditProfileForm
from flask_login import login_required, current_user
from ..utils import get_user


bp = Blueprint('user_profile', __name__)


# Show user profile page
@bp.route('/user/<user_id>')
@login_required
def user_profile(user_id):
    """Render the user profile."""
    user = get_user(user_id)
    posts = Post.query.filter_by(author=user).all()
    comments = Comment.query.filter_by(author=user).all()
    posts.sort(key=lambda p: p.created_timestamp, reverse=True)
    comments.sort(key=lambda c: c.created_timestamp, reverse=True)
    return render_template('blog/user_profile.html', user=user, posts=posts,
                           comments=comments)


# Edit profile form
@bp.route('/user/<user_id>/edit?changepic=<change_pic>', methods=('GET', 'POST'))
@bp.route('/user/<user_id>/edit', methods=('GET', 'POST'))
@login_required
def edit_user_profile(user_id, change_pic=False):
    """Edits the user profile."""
    form = EditProfileForm(current_user.username, current_user.email)
    user = get_user(user_id)
    if current_user.id != user.id:
        flash("You can only modify your own profile!")
        return redirect(url_for('user_profile.user_profile', user_id=user.id))
    elif form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        # user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user_profile.user_profile',
                                user_id=user.id))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        # form.about_me.data = user.about_me

    # Check if Change Pic button has been pressed
    if change_pic:
        return render_template('blog/edit_user_profile_changepic.html', user=user, form=form)
    return render_template('blog/edit_user_profile.html', user=user, form=form)
