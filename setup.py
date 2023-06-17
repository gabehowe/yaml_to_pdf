from setuptools import setup, find_packages

setup(
    name='yaml_to_pdf',
    version='0.1.0',
    packages=find_packages(include=['yaml_to_pdf']),
    url='',
    license='',
    author='Gabriel Howe',
    author_email='',
    description='',
    setup_requires=['pytest-runner'],
    tests_require=['pytest==7.2.1'],
    test_suite='tests'
)
