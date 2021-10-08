from setuptools import setup, find_packages

requirements = [
        'Connexion==1.4.2',
        'Flask==1.1.2',
        'minio==5.0.10',
        'ga4gh-dos-schemas==0.4.2',
        'jsonschema==3.2.0',
        'pysam==0.16.0.1',
        'sqlalchemy==1.3.18'
]

setup(
    author="Jackson Zheng",
    author_email="j75zheng@edu.uwaterloo.ca",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="CanDIG htsget API that follows the htsget standard",
    install_requires=requirements,
    include_package_data=True,
    keywords='htsget_app',
    name='htsget_app',
    packages=find_packages(include=['htsget_server']),
    url="https://github.com/CanDIG/htsget_app",
    version='0.1.3'
)
