from setuptools import find_packages, setup

setup(
    name='groupme-backup',
    version='1.0.0',
    author='William Jackson',
    author_email='william@subtlecoolness.com',
    packages=find_packages(),
    install_requires=['requests'],
    entry_points={
        'console_scripts': [
            'groupme_backup = groupme_backup.groupme_backup:main'
        ]
    }
)
