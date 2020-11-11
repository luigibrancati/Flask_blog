from setuptools import setup, find_packages

config = {
    'name': 'flaskr-lb',
    'version': '1.1.1a',
    'packages': find_packages(),
    'include_package_data': True,
    'zip_safe': False,
    'install_requires': ['flask','flask-wtf','flask-login','flask-sqlalchemy','flask-migrate','email-validator']
}

setup(**config)
