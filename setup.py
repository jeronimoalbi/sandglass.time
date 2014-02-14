from setuptools import find_packages
from setuptools import setup


setup(
    name='sandglass.time',
    version='0.1.0',
    packages=find_packages(),
    namespace_packages=['sandglass'],
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'pyramid==1.4.3',
        'pyramid_tm==0.7',
        'pyramid_mailer==0.13',
        'waitress==0.8.8',
        'sqlalchemy==0.9.1',
        'zope.sqlalchemy',
        'zope.component==4.1.0',
        # Forms/data handling
        'colander',
        # Translations extraction support
        'Babel',
        'lingua',
        # Documentation support
        'Sphinx',
        # Date/time and TZ support
        'dateutils',
        'pytz',
        # Command line support
        'cement',
    ],
    entry_points={
        'paste.app_factory': [
            'main = sandglass.time.main:make_wsgi_app',
        ],
        'console_scripts': [
            'sandglass = sandglass.time.command:main',
        ],
    },
    paster_plugins=['pyramid'],
    message_extractors={
        'sandglass/time': [
            ('**.py', 'lingua_python', None),
            ('tests/**', 'ignore', None),
            ('locales/**', 'ignore', None),
        ],
    },
    test_suite='sandglass.time.tests',
)
