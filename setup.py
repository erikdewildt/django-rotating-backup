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
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
