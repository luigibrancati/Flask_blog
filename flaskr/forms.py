from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from flaskr.models import User, Post, Comment

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', 
            validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError("Please use a different email address.")

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0,max=140)])
    submit = SubmitField('Submit')
    
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm,self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError("Please use a different username.")

class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=0, max=120)])
    body = TextAreaField('Body', validators=[DataRequired(), Length(min=0, max=1000)])
    submit = SubmitField('Submit')
    
    def validate_title(self, title):
        post = Post.query.filter_by(title=title.data).first()
        if post is not None:
            raise ValidationError("Please use a different title.")

class EditPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=0, max=120)])
    body = TextAreaField('Body', validators=[DataRequired(), Length(min=0, max=1000)])
    submit = SubmitField('Submit')

    def __init__(self, original_title, *args, **kwargs):
        super(EditPostForm,self).__init__(*args, **kwargs)
        self.original_title = original_title

    def validate_title(self, title):
        if title.data != self.original_title:
            post = Post.query.filter_by(title=self.title.data).first()
            if post is not None:
                raise ValidationError("Please use a different title.")

class CreateCommentForm(FlaskForm):
    body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditCommentForm(FlaskForm):
    body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Submit')
