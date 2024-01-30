from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='package',
    author="casperliuliuliu",
    packages=find_packages(),
    description='A brief description of the usage',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/casperliuliuliu/Wordee',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    ],
    install_requires=required,
)