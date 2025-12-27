#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging

import yaml
from pycountry import countries


def snake_case_to_camel_case(snake_case: str) -> str:
    camel_case = ""
    for token in snake_case.split("_"):
        camel_case += token.capitalize()
    return camel_case


# print(snake_case_to_camel_case("usa_portland_wang"))
# print(snake_case_to_camel_case("usa_idaho_boise01"))


def export_to_yaml(fpath: str, lookup_dict: dict):
    """Write content of lookup_dict to yaml file."""
    with open(fpath, "w") as fp:
        yaml.dump(lookup_dict, fp, default_flow_style=False, width=float("inf"))


def is_valid_alpha3(code: str) -> bool:
    try:
        return countries.get(alpha_3=code.upper()) is not None
    except KeyError:
        return False


APT_MIME_TYPES = [
    # common
    ".pos",
    ".epos",
    ".apt",
    ".ato",  # Rouen, GPM
    ".csv",
    # ranging definitions
    ".env",  # Rouen, GPM
    ".rrng",
    ".rng",
    ".fig.txt",
    # mixed mode and more exotic stuff
    ".h5",  # Erlangen OXCART raw, ranging, and reconstruction, pyccapt
    ".hdf",
    ".hdf5",  # Cameca HDF5 from Materials Data Facility
    # ".xml",  # Imago legacy
    ".analysis",
    ".analysisset",
    ".nxs",  # NeXus/HDF5
    ".raw",  # Stuttgart M-TAP
    ".ops",  # legacy 3DAP, PoSAP
]
CAMECA_ROOT_MIME_TYPES = [".str", ".rraw", ".rhit", ".hits", ".root"]


DEFAULT_LOGGER_NAME = "convert_legacy_data"
logger = logging.getLogger(DEFAULT_LOGGER_NAME)
ffmt = "%(levelname)s %(asctime)s %(message)s"
tfmt = "%Y-%m-%dT%H:%M:%S.%z"  # .%f%z"
formatter = logging.Formatter(ffmt, tfmt)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
