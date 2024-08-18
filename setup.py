from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='pyeasypay',
    version='0.2.3',
    author='nichind',
    author_email='nichinddev@gmail.com',
    description='Make money from your Python projects the easy way.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/nichind/pyeasypay',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'python-dotenv',
        'aiocryptopay',
        'AaioAPI',
        'requests',
        'sqlalchemy'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.8'
)
