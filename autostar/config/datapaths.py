import os
import toml
"""
Star names Formatting
"""
try:
    from ref.star_names import star_name_format, optimal_star_name, star_name_preference, StringStarName, StarName
except ImportError:
    from autostar.config.default_star_names import star_name_format, optimal_star_name, star_name_preference, \
        StringStarName, StarName

"""
Directory information of the autostar package
"""
# the directory the contains this file
config_dir = os.path.dirname(os.path.realpath(__file__))
# the directory that contains the config directory, i.e. the autostar module root
autostar_dir = os.path.dirname(config_dir)
# packages_dir is the directory that contains the autostar directory, in which other packages are installed
packages_dir = os.path.dirname(autostar_dir)

"""
Looking for a configuration toml file (user.toml), or creating one from the default. 
"""
user_toml_ref = os.path.join(packages_dir, "ref", "user.toml")
user_toml_local = os.path.join(config_dir, "user.toml")
user_toml_default = os.path.join(config_dir, "default.toml")
if os.path.exists(user_toml_ref):
    # First look for a user.toml file installed in a package call "ref"
    user_toml = user_toml_ref
elif os.path.exists(os.path.join(config_dir, "user.toml")):
    # Then look for a user.toml file in the config directory
    user_toml = user_toml_local
else:
    # If no user.toml file is found, copy the default.toml to be written
    default_config = toml.load(user_toml_default)
    # use location of the autostar package
    reference_data_dir = os.path.join(autostar_dir, "reference")
    default_config['reference_data_dir'] = reference_data_dir
    # save the default config to the config directory
    with open(user_toml_local, 'w') as f:
        toml.dump(default_config, f)
    user_toml = user_toml_local

# Load the user.toml file
user_config = toml.load(user_toml)

# set the file paths for import in other files
ref_dir = user_config['reference_data_dir']

sb_bad_star_name_ignore_filename = os.path.join(ref_dir, "bad_starname_ignore.csv")
sb_main_ref_filename = os.path.join(ref_dir, user_config['sb_main_ref_filename'])
sb_save_filename = os.path.join(ref_dir, user_config['sb_save_filename'])
sb_save_coord_filename = os.path.join(ref_dir, user_config['sb_save_coord_filename'])
sb_ref_filename = os.path.join(ref_dir, user_config['sb_ref_filename'])
tic_ref_filename = os.path.join(ref_dir, user_config['tic_ref_filename'])
sb_desired_names = set(user_config['sb_desired_names'])
