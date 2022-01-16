from datetime import datetime
from flask import Blueprint, flash, redirect,\
                  render_template, request, url_for,\
                  current_app
from myblog import db
from myblog.email_notifications import OpCommentNotificationEmailSender, TagNotificationEmailSender
from myblog.models import Comment
from myblog.forms import CreateCommentForm, EditCommentForm
from flask_login import login_required, current_user
from ..utils import format_markdown, get_comment, get_post,\
                   get_user, get_all_comments, get_mentioned_users
from smtplib import SMTPAuthenticationError

bp = Blueprint('comment', __name__)


@bp.route('/comment/<int:post_id>', methods=('GET', 'POST'))
@login_required
def create_comment(post_id):
    """Add a comment under a post. Also sends an email notification to original poster."""
    form = CreateCommentForm()
    post = get_post(post_id, check_author=False)
    post.body = format_markdown(post.body)
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, author=current_user,
                          original_post=post)
        current_app.logger.info(f"New comment created")
        db.session.add(comment)
        db.session.commit()
        current_app.logger.info(f"Comment {comment.id} pushed to database")
        current_app.logger.info(f"Comment {comment.id} has been created by user {current_user.id}")
        flash('Comment created.')
        # Send mail notification to OP
        op = get_user(post.user_id)
        try:
            current_app.logger.info(f"Sending notifications")
            if comment.user_id != op.id:
                current_app.logger.info(f"Sending notification to OP")
                OpCommentNotificationEmailSender\
                    .build_message(
                        url_for('post.show_post', post_id=post.id, _external=True),
                        comment.id,
                        op,
                        current_user)\
                    .send_mail()
            # Send emails to tagged users
            current_app.logger.info(f"Sending notifications to tagged users")
            for user in get_mentioned_users(comment.body):
                TagNotificationEmailSender\
                    .build_message(
                        url_for('post.show_post', post_id=post.id, _external=True),
                        comment.id,
                        user,
                        current_user)\
                    .send_mail()
        except SMTPAuthenticationError as e:
            current_app.logger.error("Not able to send notifications.\nError: {e}")
        return redirect(url_for('post.show_post', post_id=post_id))
    comments = get_all_comments(post_id)
    return render_template('blog/create_comment.html', form=form, post=post,
                           comments=comments, comment=None)


@bp.route('/comment/<int:comment_id>/edit', methods=('GET', 'POST'))
@login_required
def edit_comment(comment_id):
    """Update a comment under a post."""
    comment = get_comment(comment_id)
    post_id = comment.original_post.id
    form = EditCommentForm()
    if form.validate_on_submit():
        if current_user != comment.author:
            flash("You can't edit a comment that is not yours!")
            return redirect(url_for('post.show_post', post_id=post_id))
        comment.body = form.body.data
        comment.updated_timestmap = datetime.utcnow()
        db.session.commit()
        current_app.logger.info(f"Comment {comment.id} has been edited by user {current_user.id}")
        flash('Your changes have been made.')
        return redirect(url_for('post.show_post', post_id=post_id))
    elif request.method == "GET":
        form.body.data = comment.body
    post = get_post(post_id, check_author=False)
    post.body = format_markdown(post.body)
    comments = get_all_comments(post_id)
    return render_template('blog/create_comment.html', form=form, post=post,
                           comments=comments, comment=comment)


@bp.route('/comment/<int:comment_id>/delete', methods=('POST',))
@login_required
def delete_comment(comment_id):
    """Delete a comment."""
    comment = get_comment(comment_id)
    post_id = comment.original_post.id
    db.session.delete(comment)
    db.session.commit()
    current_app.logger.info(f"Comment {comment.id} has been deleted by user {current_user.id}")
    return redirect(url_for('post.show_post', post_id=post_id))
