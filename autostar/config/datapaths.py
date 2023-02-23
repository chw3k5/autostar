import os
import toml
"""
Star names Formatting
"""
try:
    from ref.star_names import star_name_format, optimal_star_name, star_name_preference, StringStarName, StarName,\
        star_letters, asterisk_names, asterisk_name_types
except ImportError:
    from autostar.config.default_star_names import star_name_format, optimal_star_name, star_name_preference, \
        StringStarName, StarName, star_letters, asterisk_names, asterisk_name_types

try:
    from ref.ref import star_names_dir
except ImportError:
    from autostar.config.default_star_names import star_names_dir

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
user_toml_ref = os.path.join(star_names_dir, "user.toml")
user_toml_local = os.path.join(config_dir, "user.toml")
user_toml_default = os.path.join(config_dir, "default.toml")
# If no user.toml file is found, copy the default.toml to be written
default_config = toml.load(user_toml_default)
if os.path.exists(user_toml_ref):
    # First look for a user.toml file installed in a package call "ref"
    user_toml = user_toml_ref
elif os.path.exists(os.path.join(config_dir, "user.toml")):
    # Then look for a user.toml file in the config directory
    user_toml = user_toml_local
else:
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
if not os.path.exists(ref_dir):
    os.mkdir(ref_dir)


def get_config_value(key):
    """if the user config file does not have all the keys, use the default config"""
    if key in user_config.keys():
        return user_config[key]
    else:
        return default_config[key]


# reference files name
sb_bad_star_name_ignore_filename = os.path.join(ref_dir, "bad_starname_ignore.csv")
sb_main_ref_filename = os.path.join(ref_dir, get_config_value('sb_main_ref_filename'))
sb_save_filename = os.path.join(ref_dir, get_config_value('sb_save_filename'))
sb_save_coord_filename = os.path.join(ref_dir, get_config_value('sb_save_coord_filename'))
sb_ref_filename = os.path.join(ref_dir, get_config_value('sb_ref_filename'))
tic_ref_filename = os.path.join(ref_dir, get_config_value('tic_ref_filename'))
annoying_names_filename = os.path.join(ref_dir, get_config_value("annoying_names_filename"))
popular_names_filename = os.path.join(ref_dir, get_config_value("popular_names_filename"))
exoplanet_archive_filename = os.path.join(ref_dir, get_config_value("exoplanet_archive_filename"))

# order does not matter, this is for contains value checking
sb_desired_names = set(get_config_value('sb_desired_names'))
nea_exo_star_name_columns = set(get_config_value('nea_exo_star_name_columns'))
nea_might_be_zero = set(get_config_value('nea_might_be_zero'))
nea_unphysical_if_zero_params = set(get_config_value('nea_unphysical_if_zero_params'))
# order matters for nea_requested_data_types_default
nea_requested_data_types_default = get_config_value('nea_requested_data_types_default')
