# Flask_blog
A small blog developed in python using Flask https://flask.palletsprojects.com/en/1.1.x/tutorial/

In this branch a new database system is used, based on the ORM package Flask-sqlalchemy and Flask-migrate to migrate databases. A login manager using flask-login is also used. All according to https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

The final website is hosted on http://lbranco93.pythonanywhere.com/ just for fun

## How to run this blog

To start the app, first run the following commands
```
$ flask db init
```
in order to instantiate the database. Then run
```
$ flask run
```
in order to run the blog in your local machine.