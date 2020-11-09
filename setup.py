from setuptools import setup, find_packages

config = {
    'name': 'flaskr-lb',
    'version': '1.0.2a',
    'packages': find_packages(),
    'include_package_data': True,
    'zip_safe': False,
    'install_requires': ['flask',]
}

setup(**config)
