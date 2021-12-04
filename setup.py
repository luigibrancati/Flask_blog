from setuptools import setup, find_packages

with open('./requirements.txt') as file:
    reqs = file.readlines()
    reqs = [r.rstrip() for r in reqs]


config = {
    'name': 'myblog-lb',
    'version': '1.1.1a',
    'packages': find_packages(),
    'include_package_data': True,
    'zip_safe': False,
    'install_requires': reqs
}

setup(**config)
