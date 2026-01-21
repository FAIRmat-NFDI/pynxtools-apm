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

import os

import yaml

from pynxtools_apm.examples.oasisb_bibliography import get_bibliographical_metadata


def generate_oasis_specific_yaml(
    project_name: str,
    row_idx: str,
    file_path_prefix: str,
    bibliography: dict,
    write_yaml_file: bool = True,
) -> str:
    eln_file_path = f"{file_path_prefix}/{project_name}.{row_idx}.oasis.specific.yaml"  # eln_data.yaml"
    eln_data: dict = {}

    # eln_data["entry"] = {}

    eln_data["citation"] = []
    data, article = get_bibliographical_metadata(bibliography, project_name)
    for entry, note in [
        (data, "Reference to the original dataset publication"),
        (
            article,
            "Reference to an article that the authors associated with the dataset publication",
        ),
    ]:
        if entry in bibliography and entry != "":
            if "author" and "doi" in bibliography[entry]:
                cite_dict = {}
                cite_dict["authors"] = f"{bibliography[entry]['author']}"
                cite_dict["description"] = note
                cite_dict["doi"] = f"{bibliography[entry]['doi']}"
                cite_dict["url"] = f"https://doi.org/{bibliography[entry]['doi']}"

                eln_data["citation"].append(cite_dict)

    # TODO move this from here into generate_eln_data_yaml
    # eln_data["sample"] = {}
    # if isinstance(dirty_atom_types, str):
    #     clean_atom_types = [
    #         x.strip() for x in dirty_atom_types.replace("?", "").split(",") if x.strip()
    #     ]
    #     eln_data["sample"]["atom_types"] = ", ".join(clean_atom_types)

    if write_yaml_file:
        with open(eln_file_path, "w") as fp:
            yaml.dump(eln_data, fp)
    if os.path.isfile(eln_file_path):
        return eln_file_path
    return ""
