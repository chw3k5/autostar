from typing import NamedTuple, Union, Optional
from autostar.simbad_query import StarDict


# params_format_dict "lower": "desired"
params_format_dict = {"teff": "Teff"}


def format_key(key):
    key_str = str(key)
    key_lower = key_str.lower()
    if key_lower in params_format_dict.keys():
        return params_format_dict[key_lower]
    return key_lower


class ObjectParams(StarDict):
    def __setitem__(self, key, value):
        key = format_key(key)
        if not self.__contains__(key):
            if isinstance(value, set):
                self.data[key] = value
            elif isinstance(value, SingleParam):
                self.data[key] = {value}
            else:
                raise ValueError("SingleParam tuple or set is required")
        if isinstance(value, set):
            self.data[key] |= value
        elif isinstance(value, SingleParam):
            self.data[key].add(value)
        else:
            raise ValueError("SingleParam tuple or set is required")

    def update_single_ref_source(self, ref_str, params_dict):
        new_param_dict = {}
        for param_name in params_dict.keys():
            new_param_dict["value"] = params_dict[param_name]
            new_param_dict['ref'] = ref_str
            self.data[str(param_name)] = set_single_param(new_param_dict)


class SingleParam(NamedTuple):
    """ Represents all the attributes for a single parameter value."""
    value: Union[float, int, str]
    err: Optional[Union[float, int, str]] = None
    ref: Optional[str] = None
    units: Optional[str] = None
    notes: Optional[str] = None


def set_single_param(param_dict=None, value=None, err=None, units=None, ref=None, notes=None):
    if param_dict is not None:
        keys = set(param_dict.keys())
        if "value" in keys:
            internal_param_dict = {}
            for param_key in SingleParam._fields:
                if param_key in keys:
                    internal_param_dict[param_key] = param_dict[param_key]
                else:
                    internal_param_dict[param_key] = None
            return SingleParam(value=internal_param_dict["value"],
                               err=internal_param_dict['err'],
                               units=internal_param_dict['units'],
                               ref=internal_param_dict['ref'],
                               notes=internal_param_dict['notes'])
    elif value is not None:
        return SingleParam(value=value, err=err, units=units, ref=ref, notes=notes)
    raise ValueError("A key named 'value' is needed to set a parameter")

