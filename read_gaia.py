import os
import time
import numpy as np
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, Distance
from astroquery.gaia import Gaia
from autostar.table_read import row_dict
from ref import ref_dir, gaia_dr2_parallax_offset
from star_names import star_name_format, StarName, StringStarName
from autostar.simbad_query import SimbadLib, StarDict
from autostar.object_params import ObjectParams, set_single_param

deg_per_mas = 1.0 / (1000.0 * 60.0 * 60.0)


class GaiaLib:
    def __init__(self, simbad_lib=None, simbad_go_fast=False, verbose=True):
        self.verbose = verbose
        self.simbad_go_fast = simbad_go_fast
        self.max_dr_number = 2
        self.dr_numbers = list(range(1, self.max_dr_number + 1))
        self.gaia_name_types = set()
        for dr_number in self.dr_numbers:
            self.gaia_name_types.add("gaia dr" + str(dr_number))
            self.__setattr__('gaiadr' + str(dr_number) + "_ref",
                             GaiaRef(verbose=self.verbose, dr_number=dr_number))
        if simbad_lib is None:
            self.simbad_lib = SimbadLib(go_fast=self.simbad_go_fast, verbose=self.verbose)
        else:
            self.simbad_lib = simbad_lib

        self.gaia_query = GaiaQuery(verbose=self.verbose)

        self.object_params_to_trim = {"ra", "ra_error", 'dec', "dec_error", 'ref_epoch', "duplicated_source",
                                      "source_id"}

    def batch_update(self, dr_number, simbad_formatted_names_list):
        dr_number = int(dr_number)
        gaia_ref = self.__getattribute__('gaiadr' + str(dr_number) + "_ref")
        self.gaia_query.astroquery_source(simbad_formatted_name_list=simbad_formatted_names_list, dr_num=dr_number)
        gaia_star_ids = set(self.gaia_query.star_dict.keys())
        for gaia_star_id in gaia_star_ids:
            gaia_ref.add_ref({gaia_star_id}, self.gaia_query.star_dict[gaia_star_id])
        if gaia_star_ids != set():
            gaia_ref.save()

    def get_gaia_names_dict(self, hypatia_name):
        if isinstance(hypatia_name, dict) or isinstance(hypatia_name, StarDict):
            hypatia_handle, star_names_dict = self.simbad_lib.get_star_dict_with_star_dict(hypatia_name)
        else:
            hypatia_handle, star_names_dict = self.simbad_lib.get_star_dict(hypatia_name=hypatia_name)
        gaia_star_names_dict = {star_type: star_names_dict[star_type] for star_type in star_names_dict.keys()
                                if star_type in self.gaia_name_types}
        return hypatia_handle, gaia_star_names_dict

    def get_single_dr_number_data(self, gaia_hypatia_name):
        gaia_name_type, gaia_star_id = gaia_hypatia_name
        dr_number = int(gaia_name_type.replace("gaia dr", "").strip())
        gaia_ref = self.__getattribute__('gaiadr' + str(dr_number) + "_ref")
        test_output = gaia_ref.find(gaia_star_id=gaia_star_id)
        if test_output is not None:
            # This is the primary case, data is available in the reference file, and is returned
            return test_output
        else:
            # is data available on the ESA website?
            dr_number = int(gaia_name_type.lower().replace("gaia dr", "").strip())
            self.gaia_query.astroquery_source([StringStarName(StarName(gaia_name_type, gaia_star_id)).string_name],
                                              dr_num=dr_number)
            if gaia_star_id in self.gaia_query.star_dict.keys():
                # We found the data and can update the reference data so that it is found first next time
                gaia_params_dict = self.gaia_query.star_dict[gaia_star_id]
            else:
                # no data was found, we record this so that next time a search is not needed.
                gaia_params_dict = {}
            gaia_ref.add_ref({gaia_star_id}, gaia_params_dict)
            gaia_ref.save()
            gaia_ref.load()
            return self.get_single_dr_number_data(gaia_hypatia_name)

    def get(self, hypatia_name):
        hypatia_handle, gaia_star_names_dict = self.get_gaia_names_dict(hypatia_name)
        gaia_hypatia_names = []
        for gaia_name_type in gaia_star_names_dict.keys():
            for star_id in gaia_star_names_dict[gaia_name_type]:
                gaia_hypatia_names.append(StarName(gaia_name_type, star_id))
        return hypatia_handle, {gaia_hypatia_name: self.get_single_dr_number_data(gaia_hypatia_name)
                                for gaia_hypatia_name in gaia_hypatia_names}

    def convert_to_object_params(self, gaia_params_dicts):
        new_object_params = ObjectParams()
        for gaia_hypatia_name in gaia_params_dicts.keys():
            gaia_name_type, _gaia_star_id = gaia_hypatia_name
            dr_number = int(gaia_name_type.replace("gaia dr", "").strip())
            _gaia_ids, gaia_params_dict = gaia_params_dicts[gaia_hypatia_name]
            gaia_params_dict_keys = set(gaia_params_dict.keys())
            if 'parallax' in gaia_params_dict_keys:
                if dr_number == 2:
                    gaia_params_dict["parallax"] = gaia_params_dict["parallax"] + gaia_dr2_parallax_offset
                gaia_params_dict['dist'] = 1.0 / (float(gaia_params_dict['parallax']) * 0.001)
            ref_str = "Gaia Data Release " + str(dr_number)
            params_dicts = {}
            param_names_found = set()
            for param_key in gaia_params_dict_keys:
                if "_error" in param_key:
                    param_name = param_key.replace("_error", "")
                    if param_name not in param_names_found:
                        params_dicts[param_name] = {}
                        param_names_found.add(param_name)
                    # convert to make the error have the same units as the primary value
                    if "ra" in param_key or "dec" in param_key:
                        gaia_params_dict[param_key] = gaia_params_dict[param_key] * deg_per_mas
                    params_dicts[param_name]["err"] = gaia_params_dict[param_key]
                else:
                    if param_key not in param_names_found:
                        params_dicts[param_key] = {}
                        param_names_found.add(param_key)
                    params_dicts[param_key]['value'] = gaia_params_dict[param_key]
                    params_dicts[param_key]['ref'] = ref_str
                    if param_key in self.gaia_query.params_with_units:
                        params_dicts[param_key]['units'] = self.gaia_query.param_to_units[param_key]
            param_names = set(params_dicts.keys()) - self.object_params_to_trim
            if 'teff_val' in param_names:
                params_dicts["Teff"] = params_dicts["teff_val"]
                param_names.remove("teff_val")
                param_names.add("Teff")
            for param_name in param_names:
                new_object_params[param_name] = set_single_param(param_dict=params_dicts[param_name])
        return new_object_params

    def get_object_params(self, hypatia_name):
        hypatia_handle, gaia_params_dicts = self.get(hypatia_name)
        return hypatia_handle, self.convert_to_object_params(gaia_params_dicts=gaia_params_dicts)


class GaiaRef:
    def __init__(self, dr_number=2, verbose=False):
        self.dr_number = dr_number
        self.verbose = verbose
        self.ref_data = None
        self.gaia_name_type = "gaia dr" + str(self.dr_number)
        self.ref_file = os.path.join(ref_dir, "GaiaDR" + str(self.dr_number) + "_ref.csv")
        self.lookup = None
        self.available_ids = None

    def load(self):
        self.ref_data = []
        if os.path.exists(self.ref_file):
            read_ref = row_dict(filename=self.ref_file, key="name", delimiter=",", null_value="", inner_key_remove=True)
            for saved_names in read_ref.keys():
                star_ids = set()
                for simbad_formatted_gaia_name in saved_names.split("|"):
                    gaia_name_type, gaia_star_id = star_name_format(simbad_formatted_gaia_name)
                    star_ids.add(gaia_star_id)
                    if not gaia_name_type == self.gaia_name_type:
                        raise KeyError("Gaia Data Release," + str(self.gaia_name_type) + ", received:" +
                                       str(gaia_name_type))
                self.ref_data.append((star_ids, read_ref[saved_names]))

    def save(self):
        self.make_lookup()
        header_params = set()
        name_string_to_params = {}
        for star_ids, params in self.ref_data:
            header_params |= set(params.keys())
            star_names_string = ""
            for star_id in star_ids:
                hypatia_name = StarName(self.gaia_name_type, star_id)
                simbad_formatted_name = StringStarName(hypatia_name=hypatia_name).string_name
                star_names_string += simbad_formatted_name + "|"
            name_string_to_params[star_names_string[:-1]] = params
        header = "name,"
        sorted_header_params = sorted(header_params)
        for gaia_param in sorted_header_params:
            header += gaia_param + ","
        header = header[:-1] + "\n"
        body = []
        for output_string_name in sorted(name_string_to_params.keys()):
            params = name_string_to_params[output_string_name]
            row_data = output_string_name + ","
            params_this_row = set(params.keys())
            for param_name in sorted_header_params:
                if param_name in params_this_row:
                    row_data += str(params[param_name]) + ","
                else:
                    row_data += ","
            body.append(row_data[:-1] + "\n")
        with open(self.ref_file, 'w') as f:
            f.write(header)
            [f.write(row_data) for row_data in body]

    def add_ref(self, gaia_star_ids, params):
        if self.ref_data is None:
            self.load()
        self.ref_data.append((gaia_star_ids, params))

    def find(self, gaia_star_id):
        if self.lookup is None:
            self.make_lookup()
        if gaia_star_id in self.available_ids:
            return self.ref_data[self.lookup[gaia_star_id]]
        return None

    def make_lookup(self):
        if self.ref_data is None:
            self.load()
        self.lookup = {}
        self.available_ids = set()
        found_index = None
        for ref_index, (star_ids, params) in list(enumerate(self.ref_data)):
            for gaia_star_id in star_ids:
                if gaia_star_id not in self.available_ids:
                    self.available_ids.add(gaia_star_id)
                    self.lookup[gaia_star_id] = ref_index
                else:
                    found_index = self.lookup[gaia_star_id]
                    break
            if found_index is not None:
                # only add new types, do not overwrite
                print("Duplicate_data data found, removing duplicate and restarting the Gaia reference file tool:" +
                      " make_lookup")
                self.ref_data.pop(ref_index)
                # run this again with a duplicate entry removed.
                self.make_lookup()
                break


class GaiaQuery:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.gaia_dr1_data = None
        self.gaia_dr2_data = None

        self.astro_query_dr1_params = ["ra", "ra_error", "dec", "dec_error", "ref_epoch", "source_id", "parallax",
                                       "parallax_error",
                                       "pmra", "pmra_error", "pmdec", "pmdec_error", "duplicated_source",
                                       "phot_g_mean_flux", "phot_g_mean_flux_error", "phot_g_mean_mag"]
        self.astro_query_dr2_params = ["ra", "ra_error", "dec", "dec_error", "ref_epoch", "source_id",
                                       "parallax", "parallax_error",
                                       "pmra", "pmra_error", "pmdec", "pmdec_error", "duplicated_source",
                                       "phot_g_mean_flux", "phot_g_mean_flux_error",
                                       "phot_g_mean_mag",
                                       "radial_velocity", "radial_velocity_error",
                                       "teff_val"]
        self.param_to_units = {"ra": "degrees", "ra_error": "mas", 'dec': 'degrees', "dec_error": 'mas',
                               "ref_epoch": 'Julian Years', 'parallax': 'mas', "parallax_error": "mas",
                               "pmra": 'mas/year', "pmra_error": "mas/year",
                               "pmdec": 'mas/year', "pmdec_error": "mas/year",
                               "phot_g_mean_flux": "e-/s", "phot_g_mean_mag": 'mag',
                               "radial_velocity": "km/s", "teff_val": "K",
                               "dist": "[pc]", "dist_error": "[pc]"}
        self.params_with_units = set(self.param_to_units.keys())


    def astroquery_get_job(self, job, dr_num=2):
        while job._phase != "COMPLETED":
            time.sleep(1)
        raw_results = job.get_results()
        sources_dict = {}

        if dr_num == 1:
            query_params = self.astro_query_dr1_params
        elif dr_num == 2:
            query_params = self.astro_query_dr2_params
        else:
            raise KeyError("The given Gaia Data Release number " + str(dr_num) + " is not of the format.")

        for index in range(len(raw_results.columns["source_id"])):
            params_dict = {param: raw_results.columns[param][index] for param in query_params
                           if not np.ma.is_masked(raw_results.columns[param][index])}
            found_params = set(params_dict.keys())
            if {'ra', 'dec', 'pmra', 'pmdec', "ref_epoch"} - found_params == set():
                # if parallax is available, do a more precise calculation using the distance.
                if np.ma.is_masked(params_dict['parallax']) or params_dict['parallax'] < 0.0:
                    icrs = SkyCoord(ra=params_dict['ra'] * u.deg, dec=params_dict['dec'] * u.deg,
                                    pm_ra_cosdec=params_dict['pmra'] * u.mas / u.yr,
                                    pm_dec=params_dict['pmdec'] * u.mas / u.yr,
                                    obstime=Time(params_dict['ref_epoch'], format='decimalyear'))
                else:
                    icrs = SkyCoord(ra=params_dict['ra'] * u.deg, dec=params_dict['dec'] * u.deg,
                                    distance=Distance(parallax=params_dict['parallax'] * u.mas, allow_negative=False),
                                    pm_ra_cosdec=params_dict['pmra'] * u.mas / u.yr,
                                    pm_dec=params_dict['pmdec'] * u.mas / u.yr,
                                    obstime=Time(params_dict['ref_epoch'], format='decimalyear'))
                J2000 = icrs.apply_space_motion(Time(2000.0, format='decimalyear'))
                params_dict["ra_epochJ2000"] = J2000.ra.degree
                params_dict["dec_epochJ2000"] = J2000.dec.degree
                params_dict["ra_epochJ2000_error"] = params_dict["ra_error"]
                params_dict["dec_epochJ2000_error"] = params_dict["dec_error"]

            sources_dict[params_dict['source_id']] = {param: params_dict[param] for param in params_dict.keys()
                                                      if params_dict[param] != '--'}
        return sources_dict

    def astroquery_source(self, simbad_formatted_name_list, dr_num=2):
        list_of_sub_lists = []
        sub_list = []
        cut_index = len("Gaia DR# ")
        cut_name_list = [gaia_name[cut_index:] for gaia_name in simbad_formatted_name_list]
        for source_id in cut_name_list:
            if len(sub_list) == 500:
                list_of_sub_lists.append(sub_list)
                sub_list = [source_id]
            else:
                sub_list.append(source_id)
        list_of_sub_lists.append(sub_list)
        self.star_dict = {}
        for sub_list in list_of_sub_lists:
            job_text = "SELECT * FROM gaiadr" + str(dr_num) + ".gaia_source WHERE source_id=" + str(sub_list[0])
            if len(sub_list) > 1:
                for list_index in range(1, len(sub_list)):
                    job_text += " OR source_id=" + str(sub_list[list_index])
            job = Gaia.launch_job_async(job_text)
            
            sources_dict = self.astroquery_get_job(job, dr_num=dr_num)
            self.star_dict.update({(gaia_id_int,): sources_dict[gaia_id_int] for gaia_id_int in sources_dict.keys()})

    def astroquery_cone(self, ra_icrs, dec_icrs, radius_deg=1.0):
        # gaia_coord = convert_to_gaia_dr2_coord(ra_icrs, dec_icrs)

        job_text = "SELECT * FROM gaiadr2.gaia_source WHERE " +\
                   "CONTAINS(POINT('ICRS',gaiadr2.gaia_source.ra,gaiadr2.gaia_source.dec)," +\
                   "CIRCLE('ICRS'," + str(ra_icrs) + "," + str(dec_icrs) + "," + str(radius_deg) +"))=1;"

        job = Gaia.launch_job_async(job_text)
        sources_dict = self.astroquery_get_job(job)
        return sources_dict


if __name__ == "__main__":
    gl = GaiaLib(verbose=True)
    hypatia_handle, gaia_params = gl.get(hypatia_name="Gaia DR2 1016674048078637568")
    # gd.get_hip_star_gaia_data()