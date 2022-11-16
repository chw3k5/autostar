from setuptools import setup, find_packages


setup(name='autostar',
      version='0.1.0',
      description='Auto-updating datafiles from astronomy databases.',
      author='Caleb Wheeler',
      author_email='chw3k5@gmail.com',
      packages=find_packages(),
      url="https://github.com/chw3k5/autostar",
      python_requires='>3.7',
      install_requires=['numpy',
                        'astropy',
                        'astroquery',
                        'toml']
      )
