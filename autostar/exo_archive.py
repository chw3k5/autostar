import time
from typing import List
from urllib.request import urlretrieve

from autostar.simbad_names import nc
from autostar.table_read import ClassyReader
from autostar.simbad_query import SimbadLib, StarDict, handle_to_simbad, simbad_to_handle, get_single_name_data, \
    make_hypatia_handle
from autostar.config.datapaths import star_letters, star_name_format, asterisk_names, asterisk_name_types, \
    StringStarName, exoplanet_archive_filename, nea_exo_star_name_columns, nea_might_be_zero, \
    nea_unphysical_if_zero_params, nea_requested_data_types_default


def patch_for_exo_org_name(host_name_key):
    exo_org_name = host_name_key.replace("_", " ")
    if exo_org_name.lower() in nc.annoying_names:
        exo_org_name = nc.sb_names[exo_org_name.lower()]
    elif (exo_org_name[0].isdigit() and not (len(exo_org_name) > 4 and exo_org_name[:5] == "2MASS")) or \
            exo_org_name[:3].lower() in asterisk_names or exo_org_name[:2].lower() in asterisk_names or \
            (exo_org_name[0].lower() == 'v' and exo_org_name[1].isdigit()):
        star_names_dict = get_single_name_data(exo_org_name)
        name_found = False
        for asterisk_name_type in asterisk_name_types & set(star_names_dict.keys()):
            for star_id in star_names_dict[asterisk_name_type]:
                string_name = StringStarName((asterisk_name_type, star_id)).string_name
                if exo_org_name.lower() in string_name.lower():
                    nc.append(exo_org_name, string_name)
                    nc.write()
                    exo_org_name = string_name
                    name_found = True
                    break
            if name_found:
                break
        else:
            object_name = input("Enter the Simbad name for: " + exo_org_name)
            nc.append(exo_org_name, object_name)
            nc.write()
    elif "CoRoTID" == exo_org_name[:7]:
        exo_org_name = exo_org_name[:5] + exo_org_name[7:]
    return exo_org_name


class ExoPlanet:
    def __init__(self, exo_data):
        [setattr(self, planet_param, exo_data[planet_param])
         for planet_param in set(exo_data.keys()) - nea_exo_star_name_columns
         if exo_data[planet_param] != ""
         and not (exo_data[planet_param] == 0 and planet_param in nea_unphysical_if_zero_params)
         and not (planet_param == "pl_orbeccen" and exo_data[planet_param] == 0 and exo_data["pl_orbeccen"] == 0)]
        self.planet_params = set(self.__dict__.keys())


class ExoPlanetHost:
    def __init__(self, exo_planets_dict):
        self.hypatia_handle = None
        self.star_names_dict = None
        self.planet_letters = set()
        for pl_letter in exo_planets_dict.keys():
            self.__setattr__(pl_letter, ExoPlanet(exo_planets_dict[pl_letter]))
            self.planet_letters.add(pl_letter)

        # extract the star's names from the Exoplanet class and add those attributes to this class
        star_name_types = set()
        for planet_letter in self.planet_letters:
            star_name_types = nea_exo_star_name_columns & set(exo_planets_dict[planet_letter].keys())
            # these names are the small across all the exoplanet letters.
            break
        self.star_names_dict = StarDict()
        for exo_star_name in star_name_types:
            if exo_planets_dict[planet_letter][exo_star_name] != "":
                string_name = patch_for_exo_org_name(exo_planets_dict[planet_letter][exo_star_name])
                name_key, name_id = star_name_format(string_name)
                self.star_names_dict[name_key] = name_id

        # extract this star's parameters (radius, mass, distance associated errors) and add to this class
        stellar_params = {}
        for planet_letter in self.planet_letters:
            stellar_params_this_star = {param for param in self.__getattribute__(planet_letter).planet_params
                                        if param[:3] == "st_"}
            # make the stellar parameters dictionary
            for param in stellar_params_this_star - set(stellar_params.keys()):
                stellar_params[param] = self.__getattribute__(planet_letter).__getattribute__(param)
            # remove the stellar attributes from the planet class.
            [delattr(self.__getattribute__(planet_letter), param) for param in stellar_params_this_star]
            [self.__getattribute__(planet_letter).planet_params.remove(param) for param in stellar_params_this_star]
        # set the stellar attributes to this class if they are not zero, which is unphysical for mass, radius, dist
        for param in stellar_params.keys():
            value = stellar_params[param]
            if value != 0:
                self.__setattr__(param, value)

    def set_hypatia_handle_and_star_dict(self, hypatia_handle, star_names_dict):
        self.hypatia_handle, self.star_names_dict = hypatia_handle, star_names_dict


class AllExoPlanets:
    def __init__(self, simbad_lib: SimbadLib = None,
                 requested_data_types: List[str] = None,
                 refresh_data: bool = True,
                 verbose: bool = True,
                 ref_star_names_from_scratch: bool = True,
                 simbad_go_fast: bool = False):
        if simbad_lib is None:
            self.simbad_lib = SimbadLib(verbose=verbose, go_fast=simbad_go_fast)
        else:
            self.simbad_lib = simbad_lib
        if requested_data_types is None:
            requested_data_types = nea_requested_data_types_default
        self.requested_data_types = requested_data_types
        self.verbose = verbose
        self.ref_star_names_from_scratch = ref_star_names_from_scratch
        self.exo_ref_file = exoplanet_archive_filename
        if refresh_data:
            if self.verbose:
                print("  Getting the freshest exoplanet data!")
            self.refresh_ref()
            self.data_is_fresh = True
            time.sleep(1)
            if self.verbose:
                print("    ...data received.")
        else:
            self.data_is_fresh = False
            if self.verbose:
                print("  Using existing exoplanet data on the local machine.")
        if self.verbose:
            print("  Loading exoplanet data...")
        self.single_name_stars = None
        self.multi_name_stars = None
        self.refresh_simbad_ref_data = False
        raw_exo = ClassyReader(filename=self.exo_ref_file, delimiter=",", remove_str='\"')
        raw_exo_dict = {}
        self.exo_host_names = set()
        non_host_names = set(raw_exo.keys) - {"pl_letter"}
        for index, star_name in list(enumerate(raw_exo.hostname)):
            hypatia_handle = simbad_to_handle(patch_for_exo_org_name(star_name))
            pl_letter = raw_exo.pl_letter[index]
            data_line_dict = {key: raw_exo.__getattribute__(key)[index] for key in non_host_names}
            if hypatia_handle in self.exo_host_names:
                raw_exo_dict[hypatia_handle][pl_letter] = data_line_dict
            else:
                raw_exo_dict[hypatia_handle] = {pl_letter: data_line_dict}
                self.exo_host_names.add(hypatia_handle)

        [setattr(self, host_name, ExoPlanetHost({pl_letter: raw_exo_dict[host_name][pl_letter]
                                                 for pl_letter in raw_exo_dict[host_name].keys()}))
         for host_name in sorted(self.exo_host_names)]

        self.exo_letters = self.check_for_new_star_letters()
        self.load_reference_host_names()
        if verbose:
            print("    Exoplanet data is ready.")

    def refresh_ref(self):
        items_str = ",".join(self.requested_data_types)
        query_str = f'https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+{items_str}' +\
                    f'+from+ps&format=csv'

        urlretrieve(query_str, self.exo_ref_file)

    def check_for_new_star_letters(self):
        exo_letters = set()
        [[exo_letters.add(letter) for letter in self.__getattribute__(star_name).planet_letters]
         for star_name in self.exo_host_names]
        if exo_letters - star_letters != set():
            raise KeyError("Update needed for the star_letters in autostar.config.default_star_names.py to " +
                           "include the new exoplanet letters: " +
                           str(exo_letters - star_letters))
        return exo_letters

    def find_single_name_stars(self):
        self.single_name_stars = [xo.__getattribute__(star_name) for star_name in xo.exo_host_names
                                  if len(xo.__getattribute__(star_name).star_names) < 2]

    def find_multi_name_stars(self):
        self.multi_name_stars = [xo.__getattribute__(star_name) for star_name in xo.exo_host_names
                                 if len(xo.__getattribute__(star_name).star_names) > 1]

    def inspect(self):
        self.find_multi_name_stars()
        self.find_single_name_stars()
        print("Number of multi named stars:", len(self.multi_name_stars), " single named:", len(self.single_name_stars),
              '\nratio:', float(len(self.single_name_stars)) / float(len(self.multi_name_stars)))

    def load_reference_host_names(self):
        if self.verbose:
            print("  Getting Simbad names for exoplanet host stars...")
        len_host = len(self.exo_host_names)
        report_bin = int(len_host / 20)
        for index, host_name in enumerate(sorted(self.exo_host_names)):
            if self.verbose and index % report_bin == 0:
                print("      Getting name info for star:", "%30s" % handle_to_simbad(host_name),
                      " ", "%5s" % (index + 1), "of", "%5s" % len_host)
            single_host = self.__getattribute__(host_name)
            exo_star_names_dict = single_host.star_names_dict
            hypatia_handle, star_names_dict = self.simbad_lib.get_star_dict_with_star_dict(exo_star_names_dict)
            single_host.__setattr__("hypatia_handle", hypatia_handle)
            single_host.__setattr__("star_names_dict", star_names_dict)
        if self.verbose:
            print("    Exoplanet name data updated to include star names from Simbad")

    def get_data_from_star_name(self, star_name: str):
        # use simbad references to find what the hypatia_handle for this star should be
        hypatia_handle, _star_names_dict = self.simbad_lib.get_star_dict(star_name)
        if hypatia_handle in self.exo_host_names:
            return self.__getattribute__(hypatia_handle)
        else:
            if self.verbose:
                print(f"Star name {star_name} (hypatia_handle: {hypatia_handle}) not found in exoplanet data.")
            return None


if __name__ == "__main__":
    xo = AllExoPlanets(refresh_data=True, verbose=True, ref_star_names_from_scratch=True)
    # xo.inspect()
    xo.load_reference_host_names()
