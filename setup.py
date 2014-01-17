from setuptools import find_packages
from setuptools import setup

from sandglass.time import __version__


setup(
    name='sandglass.time',
    version=__version__,
    packages=find_packages(),
    namespace_packages=['sandglass'],
    zip_safe=False,
    install_requires=[
        'pyramid==1.4.3',
        'pyramid_tm==0.7',
        'pyramid_mailer==0.13',
        'cornice==0.16.2',
        'waitress==0.8.8',
        'sqlalchemy==0.9.1',
        'WebTest==2.0.11',
    ],
    entry_points={
        'paste.app_factory': [
            'main = sandglass.time.main:run_wsgi',
        ]
    },
    paster_plugins=['pyramid'],
)
