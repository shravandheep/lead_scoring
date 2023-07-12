import os
from setuptools import setup, find_packages
from setuptools.command import install 


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


from distutils.core import setup
from distutils.command.clean import clean
from distutils.command.install import install

class MyInstall(install):

    # Calls the default run command, then deletes the build area
    # (equivalent to "setup clean --all").
    def run(self):
        install.run(self)
        c = clean(self.distribution)
        c.all = True
        c.finalize_options()
        c.run()

setup(
    name='lead_scoring',
    version='0.1.0',
    author="Shravan Dheep",
    author_email="shravan@madstreetden.com",
    description="A Lead scoring logic",
    long_description="Lead scoring go zzzzzz",
    license="MIT",
    keywords="lead scoring",

    packages=find_packages(exclude='dist'),
    classifiers=[],
    python_requires='>=3'
)

#     cmdclass={'install': MyInstall}
