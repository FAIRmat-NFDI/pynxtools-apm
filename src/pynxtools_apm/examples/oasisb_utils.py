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


def snake_case_to_camel_case(snake_case: str) -> str:
    camel_case = ""
    for token in snake_case.split("_"):
        camel_case += token.capitalize()
    return camel_case


# print(snake_case_to_camel_case("usa_portland_wang"))
# print(snake_case_to_camel_case("usa_idaho_boise01"))


APT_MIME_TYPES = [
    ".csv",
    ".pos",
    ".epos",
    ".apt",
    ".ato",  # Rouen, GPM
    ".ops",
    ".env",  # Rouen, GPM
    ".rrng",
    ".rng",
    ".fig.txt",
    ".raw",  # Stuttgart M-TAP
    ".h5",  # Erlangen OXCART, pyccapt
    "range_.h5",  # Erlangen OXCART, pyccapt
    ".nxs",
    ".hdf",
    ".hdf5.xml",  # Imago legacy
]
CAMECA_ROOT_MIME_TYPES = [".str", ".rraw", ".rhit", ".root", ".hits"]
