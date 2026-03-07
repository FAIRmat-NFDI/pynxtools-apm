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
"""Implement NeXus-specific groups and fields to document software and versions used."""

from typing import Any

import flatdict as fd
from ifes_apt_tc_data_modeling.utils.versioning import (
    get_ifes_apt_tc_data_modeling_version,
)
from pynxtools.dataconverter.helpers.versioning import get_pynxtools_version

from pynxtools_apm.concepts.mapping_functors_pint import add_specific_metadata_pint
from pynxtools_apm.utils.versioning import PYNX_APM_NAME, PYNX_APM_VERSION

APM_PYNX_TO_NEXUS: dict[str, Any] = {
    "prefix_trg": "/ENTRY[entry*]/profiling",
    "prefix_src": "",
    "use": [
        ("programID[program1]/program", PYNX_APM_NAME),
        ("programID[program1]/program/@version", PYNX_APM_VERSION),
        ("programID[program2]/program", "pynxtools"),
        ("programID[program2]/program/@version", get_pynxtools_version()),
        ("programID[program3]/program", "ifes_apt_tc_data_modeling"),
        (
            "programID[program3]/program/@version",
            get_ifes_apt_tc_data_modeling_version(),
        ),
    ],
}


class NxApmAppDef:
    """Add NeXus NXapm application definition specific contextualization."""

    def __init__(self, entry_id: int = 1):
        self.entry_id = entry_id

    def parse(self, template: dict) -> dict:
        """Parse application definition."""
        add_specific_metadata_pint(
            APM_PYNX_TO_NEXUS, fd.FlatDict({}, delimiter="/"), [self.entry_id], template
        )
        return template
