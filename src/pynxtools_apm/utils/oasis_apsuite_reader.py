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
"""Wrapping multiple parsers for vendor files with NOMAD Oasis/ELN/YAML metadata."""

import pathlib
from typing import Any, Dict

import flatdict as fd
import yaml
from ase.data import chemical_symbols

from pynxtools_apm.concepts.mapping_functors_pint import add_specific_metadata_pint
from pynxtools_apm.configurations.cameca_cfg import APM_CAMECA_TO_NEXUS


class NxApmNomadOasisCamecaParser:
    """Parse manually collected content from an IVAS / AP Suite YAML."""

    def __init__(self, file_path: str = "", entry_id: int = 1, verbose: bool = False):
        """Construct class"""
        print(f"Extracting data from IVAS/APSuite file: {file_path}")
        if pathlib.Path(file_path).name.endswith(".cameca"):
            self.file_path = file_path
        self.entry_id = entry_id if entry_id > 0 else 1
        self.verbose = verbose
        try:
            with open(self.file_path, "r", encoding="utf-8") as stream:
                self.yml = fd.FlatDict(yaml.safe_load(stream), delimiter="/")
                if self.verbose:
                    for key, val in self.yml.items():
                        print(f"key: {key}, value: {val}")
        except (FileNotFoundError, IOError):
            print(f"File {self.file_path} not found !")
            self.apsuite = fd.FlatDict({}, delimiter="/")
            return

    def parse_ranging_definitions(self, template: dict) -> dict:
        """Interpret human-readable ELN input to generate consistent composition table."""
        src = "sample/composition"
        if src in self.yml:
            if isinstance(self.yml[src], list):
                dct: Dict[Any, Any] = {}  # IMPLEMENT ME!
                prfx = f"/ENTRY[entry{self.entry_id}]/sample/chemical_composition"
                ion_id = 1
                for symbol in chemical_symbols[1::]:
                    # ase convention is that chemical_symbols[0] == "X"
                    # to enable using ordinal number for indexing
                    if symbol in dct:
                        if isinstance(dct[symbol], tuple) and len(dct[symbol]) == 2:
                            trg = f"{prfx}/ionID[ion{ion_id}]"
                            template[f"{trg}/chemical_symbol"] = symbol
                            template[f"{trg}/composition"] = dct[symbol][0]
                            if dct[symbol][1] is not None:
                                template[f"{trg}/composition_error"] = dct[symbol][1]
                            ion_id += 1
        return template

    def parse(self, template: dict) -> dict:
        """Copy data from self into template the appdef instance."""
        self.parse_ranging_definitions(template)
        identifier = [self.entry_id]
        add_specific_metadata_pint(
            APM_CAMECA_TO_NEXUS, self.apsuite, identifier, template
        )
        return template
