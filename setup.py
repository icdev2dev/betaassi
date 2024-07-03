from setuptools import setup, find_packages

setup(
    name='betaassi',
    version='0.1.1',  
    author='icdev2dev',
    author_email='icdev2dev@gmail.com',
    description='A Python package to facilitate building applications with OpenAI, including session handling and server functionalities.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/icdev2dev/betaassi',  
    project_urls={
        "Bug Tracker": "https://github.com/icdev2dev/betaassi/issues",
    },
    license='MIT',  # Or any other license you prefer
    packages=find_packages(where='src'),  # assuming your code is in src
    package_dir={'': 'src'},
    

    install_requires=[
    'annotated-types>=0.6.0',
    'anyio>=4.3.0',
    'certifi',
    'distro>=1.9.0',
    'exceptiongroup>=1.2.0',
    'h11>=0.14.0',
    'httpcore>=1.0.2',
    'httpx>=0.25.2',
    'idna>=3.6',
    'openai>=1.23.2',
    'pydantic>=2.7.0',
    'pydantic_core>=2.18.1',
    'sniffio>=1.3.0',
    'tqdm>=4.66.1',
    'typing_extensions>=4.11.0'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',  
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.7',
    keywords='openai api, session handling, async server',  # Add some relevant keywords

    entry_points={
        'console_scripts': [
            'betaassi-server=openai_session_server.server:main',
        ],
    },
    
)

