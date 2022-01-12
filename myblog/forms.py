from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField,\
                    BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email,\
                               EqualTo, Length
from myblog.models import User, Post
from myblog.config import POST_MAX_LEN, BODY_MIN_LEN


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    register = SubmitField('Register')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password',
                              validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        try:
            User.validate_username_static(username.data)
        except AssertionError:
            raise ValidationError("Usernames cannot contain spaces or special characters.")
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError("Please use a different email address.")


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    # about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        try:
            User.validate_username_static(username.data)
        except AssertionError:
            raise ValidationError("Usernames cannot contain spaces or special characters.")
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        if email.data != self.original_email:
            email = User.query.filter_by(email=self.email.data).first()
            if email is not None:
                raise ValidationError("Please use a different email.")


class CreatePostForm(FlaskForm):
    title = StringField('Title',
                        validators=[DataRequired(), Length(min=0, max=120)])
    body = TextAreaField('Body',
                         validators=[DataRequired(), Length(min=0, max=POST_MAX_LEN)])
    submit = SubmitField('Submit')

    def validate_title(self, title):
        post = Post.query.filter_by(title=title.data).first()
        if post is not None:
            raise ValidationError("Please use a different title.")

    def validate_body(self, body):
        if len(body.data) < BODY_MIN_LEN:
            raise ValidationError("Body must be at least 50 characters long.")


class EditPostForm(CreatePostForm):
    def __init__(self, original_title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_title = original_title

    def validate_title(self, title):
        if title.data != self.original_title:
            super().validate_title(title)


class CreateCommentForm(FlaskForm):
    body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditCommentForm(CreateCommentForm):
    pass
