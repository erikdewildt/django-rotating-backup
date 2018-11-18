import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-rotating-backup',
    version='0.0.1',
    author='erik.de.wildt',
    author_email='erik.de.wildt@gmail.com',
    description="A simple Django app to conduct rotating backups of the Django database and media files.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://www.github.com/erikdewildt/django_rotating_backup",
    packages=find_packages(),
    license='GNU GENERAL PUBLIC LICENSE',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.x',
        'Framework :: Django :: 2.x',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU GENERAL PUBLIC LICENSE',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.x',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
