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

from pynxtools_apm.examples.oasisb.oasisb_bibliography import (
    get_bibliographical_metadata,
)


def generate_oasis_specific_yaml(
    target_directory: str,
    project_name: str,
    row_idx: str,
    bibliography: dict,
    alias_to_original: dict[str, str] = {},
    write_yaml_file: bool = True,
    # openalex_metadata: fd.FlatDict = fd.FlatDict({}, delimiter="/"),
) -> str:
    eln_file_path = (
        f"{target_directory}{os.sep}{project_name}.{row_idx}.oasis.specific.yaml"
    )
    eln_data: dict = {}

    # eln_data["entry"] = {}
    eln_data["project"] = {}
    eln_data["project"]["name"] = project_name

    eln_data["citation"] = []
    data, article = get_bibliographical_metadata(bibliography, project_name)
    for entry, mapping in [
        (data, "Reference to the original dataset publication"),
        (
            article,
            "Reference to an article that the authors associated with the dataset publication",
        ),
    ]:
        if entry in bibliography and entry != "":
            if "author" in bibliography[entry] and "doi" in bibliography[entry]:
                cite_dict = {}
                cite_dict["author"] = f"{bibliography[entry]['author']}"
                cite_dict["description"] = mapping
                cite_dict["doi"] = f"{bibliography[entry]['doi']}"
                cite_dict["url"] = f"https://doi.org/{bibliography[entry]['doi']}"
                if "title" in bibliography[entry]:
                    cite_dict["title"] = f"{bibliography[entry]['title']}"

                eln_data["citation"].append(cite_dict)

    # file aliasing
    eln_data["file_path_aliasing"] = []
    for alias, original in alias_to_original.items():
        if alias != "" and original != "":
            # alias : the file with the hashed name e.g. {project_name}.{row_idx}.{col_idx}.
            # original : how the original authors called the files, except for in some cases
            # manual renaming that was required to e.g. unpack compression nests and
            # to resolve broken content, or to resolve naming ambiguities
            eln_data["file_path_aliasing"].append({"src": alias, "trg": original})

    # TODO openalex

    if write_yaml_file:
        with open(eln_file_path, "w") as fp:
            yaml.dump(eln_data, fp)
    if os.path.isfile(eln_file_path):
        return eln_file_path
    return ""
