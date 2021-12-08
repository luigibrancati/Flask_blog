from setuptools import setup, find_packages

with open('./requirements.txt') as file:
    reqs = file.readlines()
    reqs = [r.rstrip() for r in reqs]


setup(
    name='myblog-lb',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=reqs
)
