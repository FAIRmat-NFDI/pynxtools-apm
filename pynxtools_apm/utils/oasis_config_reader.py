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
"""Load deployment-specific quantities."""

import flatdict as fd
import yaml

from pynxtools_apm.config.oasis_cfg import (
    APM_OASIS_TO_NEXUS_CFG,
    APM_PARAPROBE_EXAMPLE_TO_NEXUS_CFG,
)
from pynxtools_apm.concepts.mapping_functors import (
    variadic_path_to_specific_path,
)


class NxApmNomadOasisConfigurationParser:
    """Parse deployment specific configuration."""

    def __init__(self, file_path: str, entry_id: int, verbose: bool = False):
        print(
            f"Extracting data from deployment-specific configuration file: {file_path}"
        )
        if (
            file_path.rsplit("/", 1)[-1].endswith(".oasis.specific.yaml")
            or file_path.endswith(".oasis.specific.yml")
        ) and entry_id > 0:
            self.entry_id = entry_id
            self.file_path = file_path
            with open(self.file_path, "r", encoding="utf-8") as stream:
                self.yml = fd.FlatDict(yaml.safe_load(stream), delimiter="/")
                if verbose:
                    for key, val in self.yml.items():
                        print(f"key: {key}, val: {val}")
        else:
            self.entry_id = 1
            self.file_path = ""
            self.yml = {}

    def parse_various(self, template: dict) -> dict:
        """Copy data from configuration applying mapping functors."""
        identifier = [self.entry_id]
        for tpl in APM_OASIS_TO_NEXUS_CFG:
            if isinstance(tpl, tuple) and len(tpl) >= 2:
                if tpl[1] != "ignore":
                    trg = variadic_path_to_specific_path(tpl[0], identifier)
                    if len(tpl) == 2:
                        # nxpath, value to use directly
                        template[trg] = tpl[1]
                    if len(tpl) == 3:
                        # nxpath, modifier, value, modifier (function) evaluates value to use
                        if (tpl[1] == "load_from") and (tpl[2] in self.yml):
                            template[trg] = self.yml[tpl[2]]
        return template

    def parse_reference_frames(self, template: dict) -> dict:
        """Copy data from configuration applying mapping functors."""
        identifier = [self.entry_id]
        trg = variadic_path_to_specific_path("/ENTRY[entry*]/coordinate_system_set/COORDINATE_SYSTEM[coordinate_system]", identifier)
        template[f"{trg}/alias"] = "Following the idea of McStas that the z-axis points along the direction of an ion leaving the apex along the longest direction of the specimen."
        template[f"{trg}/type"] = "cartesian"
        template[f"{trg}/handedness"] = "right_handed"
        template[f"{trg}/x_direction"] = "Direction 1 that is perpendicular to the z_direction for a right_handed cartesian"
        template[f"{trg}/x_alias"] = "x-axis"
        template[f"{trg}/y_direction"] = "Direction 2 that is perpendicular to the xaxis_direction and the z_direction for a right_handed cartesian"
        template[f"{trg}/y_alias"] = "y-axis"
        template[f"{trg}/z_direction"] = "Direction of an ion travelling hypothetically exactly along the assumed axis that is parallel to the longest direction of the specimen."
        template[f"{trg}/z_alias"] = "z-axis"
        template[f"{trg}/origin"] = "E.g. a characteristic point e.g. initial apex or center of the base of the specimen or something else."
        return template

    def parse(self, template: dict) -> dict:
        """Copy data from configuration applying mapping functors."""
        self.parse_various(template)
        self.parse_reference_frames(template)
        return template
