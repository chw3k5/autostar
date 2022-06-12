import os
from ref.ref import ref_dir
from star_names import star_name_format, StringStarName


class NameCorrection:
    def __init__(self, auto_load=True):
        self.path = os.path.join(ref_dir, "name_correction.psv")
        self.annoying_names = None
        self.sb_names = None
        if auto_load:
            self.load()

    def load(self):
        self.annoying_names = set()
        self.sb_names = {}
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                first_line = True
                for line in f.readlines():
                    if first_line:
                        first_line = False
                    else:
                        line = line.strip()
                        if line != "":
                            name, simbad_name = line.split("|")
                            self.annoying_names.add(name)
                            self.sb_names[name] = simbad_name
        else:
            with open(self.path, 'w') as f:
                f.write("name,simbad\n")

    def write(self):
        with open(self.path, 'w') as f:
            f.write("name|simbad\n")
            for name in sorted(self.sb_names.keys()):
                f.write(str(name).lower() + "|" + str(self.sb_names[name]) + "\n")
        self.load()

    def append(self, name, simbad_name):
        if name in self.sb_names.keys():
            if simbad_name != self.sb_names[name]:
                self.sb_names[name] = simbad_name
                self.write()
        else:
            self.annoying_names.add(name)
            self.annoying_names.add(name)
            self.sb_names[name] = simbad_name
            with open(self.path, 'a') as f:
                f.write(str(name).lower() + "," + str(self.sb_names[name]) + "\n")


nc = NameCorrection()


def verify_starname(test_object_name):
    object_name = None
    # This is catch for star names that are annoying that were previously found and recorded
    if test_object_name.lower() in nc.annoying_names:
        test_object_name = nc.sb_names[test_object_name.lower()]
    # try to format the name
    try:
        hypatia_name = star_name_format(test_object_name)
    except ValueError:
        object_name = input("Enter the Simbad name for: " + test_object_name)
        hypatia_name = star_name_format(object_name)
        nc.append(test_object_name, object_name)
    if object_name is None:
        object_name = StringStarName(hypatia_name).string_name
    return object_name, hypatia_name
