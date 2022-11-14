import os

# this is the default that is used if the ref.py file is not found for a given installation
# directory information in the Hypatia Database
star_names_dir = os.path.dirname(os.path.realpath(__file__))
base_dir, _ = star_names_dir.rsplit("autostar", 1)


working_dir = os.path.join(base_dir, "autostar")
ref_dir = os.path.join(working_dir, "load", "reference_data")
abundance_dir = os.path.join(working_dir, "load", 'abundance_data')
data_products_dir = os.path.join(working_dir, "load", "data_products")
star_data_output_dir = os.path.join(working_dir, "load", "data_products", "star_data_output")
plot_dir = os.path.join(working_dir, "plots", 'output')
pickle_nat = os.path.join(data_products_dir, "pickle_nat.pkl")
pickle_out = os.path.join(data_products_dir, "pickle_output_star_data.pkl")

# for the simbad Query Class
sb_save_file_name = os.path.join(working_dir, "load", "reference_data", "simbad_query_data.pkl")
sb_save_coord_file_name = os.path.join(working_dir, "load", "reference_data", "simbad_coord_data.pkl")
sb_ref_file_name = os.path.join(working_dir, "load", "reference_data", "simbad_ref_data.txt")
sb_desired_names = {"2mass", "gaia dr2", "gaia dr1", "hd", "cd", "tyc", "hip", "gj", "hr", "bd", "ids", "tres", "gv",
                    "ngc", "bps", "ogle", "xo", 'kepler', "k2", "*", "**", "v*", "name", 'wds', 'hats'}
sb_bad_star_name_ignore = os.path.join(working_dir, "load", "reference_data", "bad_starname_ignore.csv")
sb_main_ref_file_name = os.path.join(working_dir, "load", "reference_data", "simbad_main_ref_data.csv")

