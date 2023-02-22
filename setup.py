import os
from setuptools import setup, find_packages


# the user default config file that users use as a template to create their own config file
config_dir = os.path.join('autostar', 'config')
default_toml_path = os.path.join(config_dir, 'default.toml')
ref_dir = os.path.join('autostar', 'reference')
name_correction_path = os.path.join(ref_dir, 'name_correction.psv')

setup(name='autostar',
      version='0.1.3',
      description='Auto-updating datafiles from astronomy databases.',
      author='Caleb Wheeler',
      author_email='chw3k5@gmail.com',
      packages=find_packages(),
      url="https://github.com/chw3k5/autostar",
      data_files=[
          (config_dir, [default_toml_path]),
          (ref_dir, [name_correction_path]),
                  ],
      include_package_data=True,
      python_requires='>3.7',
      install_requires=['numpy',
                        'astropy',
                        'astroquery',
                        'toml'])
