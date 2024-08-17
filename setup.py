from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='easypay',
    version='0.0.1',
    author='nichind',
    author_email='nichinddev@gmail.com',
    description='Make money from your Python projects the easy way.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/nichind/easypay',
    packages=find_packages(),
    install_requires=[''],
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    project_urls={
        'Documentation': 'https://github.com/nichind/ScreenColor'
    },
    python_requires='>=3.8'
)
