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
        'cornice==0.16.2',
        'waitress==0.8.8',
        'sqlalchemy==0.9.1',
        # Request unittest support
        'WebTest==2.0.11',
        # Translations extraction support
        'Babel==1.3',
        'lingua==1.3',
    ],
    entry_points={
        'paste.app_factory': [
            'main = sandglass.time.main:run_wsgi',
        ]
    },
    paster_plugins=['pyramid'],
    message_extractors={
        'sandglass/time': [
            ('**.py', 'lingua_python', None),
            ('locales/**', 'ignore', None),
        ],
    },
)
