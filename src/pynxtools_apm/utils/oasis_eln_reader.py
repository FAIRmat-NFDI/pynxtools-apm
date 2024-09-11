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

import flatdict as fd
import yaml
import pathlib

from ase.data import chemical_symbols
from pynxtools_apm.config.eln_cfg import (
    APM_ENTRY_TO_NEXUS,
    APM_SAMPLE_TO_NEXUS,
    APM_SPECIMEN_TO_NEXUS,
    APM_INSTRUMENT_STATIC_TO_NEXUS,
    APM_INSTRUMENT_DYNAMIC_TO_NEXUS,
    APM_RANGE_TO_NEXUS,
    APM_RECON_TO_NEXUS,
    APM_WORKFLOW_TO_NEXUS,
    APM_USER_TO_NEXUS,
    APM_IDENTIFIER_TO_NEXUS,
)

from pynxtools_apm.utils.parse_composition_table import parse_composition_table
from pynxtools_apm.concepts.mapping_functors import add_specific_metadata


class NxApmNomadOasisElnSchemaParser:
    """Parse eln_data.yaml dump file content generated from a NOMAD Oasis YAML.

    This parser implements a design where an instance of a specific NOMAD
    custom schema ELN template is used to fill pieces of information which
    are typically not contained in files from technology partners
    (e.g. pos, epos, apt, rng, rrng, ...). Until now, this custom schema and
    the NXapm application definition do not use a fully harmonized vocabulary.
    Therefore, the here hardcoded implementation is needed which maps specifically
    named pieces of information from the custom schema instance on named fields
    in an instance of NXapm

    The functionalities in this ELN YAML parser do not check if the
    instantiated template yields an instance which is compliant with NXapm.
    Instead, this task is handled by the generic part of the dataconverter
    during the verification of the template dictionary.
    """

    def __init__(self, file_path: str, entry_id: int, verbose: bool = False):
        print(f"Extracting data from ELN file: {file_path}")
        if (
            pathlib.Path(file_path).name.endswith("eln_data.yaml")
            or pathlib.Path(file_path).name.endswith("eln_data.yml")
        ) and entry_id > 0:
            self.entry_id = entry_id
            self.file_path = file_path
            with open(self.file_path, "r", encoding="utf-8") as stream:
                self.yml = fd.FlatDict(yaml.safe_load(stream), delimiter="/")
                if verbose:
                    for key, val in self.yml.items():
                        print(f"key: {key}, value: {val}")
        else:
            self.entry_id = 1
            self.file_path = ""
            self.yml = {}

    def parse_entry(self, template: dict) -> dict:
        identifier = [self.entry_id]
        add_specific_metadata(APM_ENTRY_TO_NEXUS, self.yml, identifier, template)
        return template

    def parse_sample(self, template: dict) -> dict:
        identifier = [self.entry_id]
        add_specific_metadata(APM_SAMPLE_TO_NEXUS, self.yml, identifier, template)
        return template

    def parse_sample_composition(self, template: dict) -> dict:
        """Interpret human-readable ELN input to generate consistent composition table."""
        src = "sample/composition"
        if src in self.yml:
            if isinstance(self.yml[src], list):
                dct = parse_composition_table(self.yml[src])

                prfx = f"/ENTRY[entry{self.entry_id}]/sample/chemical_composition"
                unit = "at.-%"  # the assumed default unit
                if "normalization" in dct:
                    if dct["normalization"] in [
                        "%",
                        "at%",
                        "at-%",
                        "at.-%",
                        "ppm",
                        "ppb",
                    ]:
                        unit = "at.-%"
                        template[f"{prfx}/normalization"] = "atom_percent"
                    elif dct["normalization"] in ["wt%", "wt-%", "wt.-%"]:
                        unit = "wt.-%"
                        template[f"{prfx}/normalization"] = "weight_percent"
                    else:
                        return template
                ion_id = 1
                for symbol in chemical_symbols[1::]:
                    # ase convention is that chemical_symbols[0] == "X"
                    # to enable using ordinal number for indexing
                    if symbol in dct:
                        if isinstance(dct[symbol], tuple) and len(dct[symbol]) == 2:
                            trg = f"{prfx}/ionID[ion{ion_id}]"
                            template[f"{trg}/chemical_symbol"] = symbol
                            template[f"{trg}/composition"] = dct[symbol][0]
                            template[f"{trg}/composition/@units"] = unit
                            if dct[symbol][1] is not None:
                                template[f"{trg}/composition_error"] = dct[symbol][1]
                                template[f"{trg}/composition_error/@units"] = unit
                            ion_id += 1
        return template

    def parse_specimen(self, template: dict) -> dict:
        identifier = [self.entry_id]
        add_specific_metadata(APM_SPECIMEN_TO_NEXUS, self.yml, identifier, template)
        return template

    def parse_instrument_static(self, template: dict) -> dict:
        identifier = [self.entry_id]
        add_specific_metadata(
            APM_INSTRUMENT_STATIC_TO_NEXUS, self.yml, identifier, template
        )
        return template

    def parse_instrument_dynamic(self, template: dict) -> dict:
        identifier = [self.entry_id]
        add_specific_metadata(
            APM_INSTRUMENT_DYNAMIC_TO_NEXUS, self.yml, identifier, template
        )
        return template

    def parse_pulser_source(self, template: dict) -> dict:
        """Copy data into the (laser)/source section of the pulser."""
        # additional laser-specific details only relevant when the laser was used
        if "instrument/pulser/pulse_mode" in self.yml:
            if self.yml["instrument/pulser/pulse_mode"] == "voltage":
                return template

        src = "instrument/pulser/laser_source"
        if src in self.yml.keys():
            if isinstance(self.yml[src], list):
                if all(isinstance(entry, dict) for entry in self.yml[src]) is True:
                    laser_id = 1
                    # custom schema delivers a list of dictionaries...
                    for ldct in self.yml[src]:
                        trg_sta = (
                            f"/ENTRY[entry{self.entry_id}]/measurement/"
                            f"instrument/pulser/SOURCE[source{laser_id}]"
                        )
                        if "name" in ldct:
                            template[f"{trg_sta}/name"] = ldct["name"]
                        quantities = ["wavelength"]
                        for qnt in quantities:
                            if ("value" in ldct[qnt]) and ("unit" in ldct[qnt]):
                                template[f"{trg_sta}/{qnt}"] = ldct[qnt]["value"]
                                template[f"{trg_sta}/{qnt}/@units"] = ldct[qnt]["unit"]

                        trg_dyn = (
                            f"/ENTRY[entry{self.entry_id}]/measurement/"
                            f"event_data_apm_set/EVENT_DATA_APM[event_data_apm]/"
                            f"instrument/pulser/SOURCE[source{laser_id}]"
                        )
                        quantities = ["power", "pulse_energy"]
                        for qnt in quantities:
                            if isinstance(ldct[qnt], dict):
                                if ("value" in ldct[qnt]) and ("unit" in ldct[qnt]):
                                    template[f"{trg_dyn}/{qnt}"] = ldct[qnt]["value"]
                                    template[f"{trg_dyn}/{qnt}/@units"] = ldct[qnt][
                                        "unit"
                                    ]
                        laser_id += 1
                    return template
        print("WARNING: pulse_mode != voltage but no laser details specified!")
        return template

    def parse_user(self, template: dict) -> dict:
        """Copy data from user section into template."""
        src = "user"
        if src in self.yml:
            if isinstance(self.yml[src], list):
                if all(isinstance(entry, dict) for entry in self.yml[src]) is True:
                    user_id = 1
                    # custom schema delivers a list of dictionaries...
                    for user_dict in self.yml[src]:
                        if user_dict == {}:
                            continue
                        identifier = [self.entry_id, user_id]
                        add_specific_metadata(
                            APM_USER_TO_NEXUS,
                            fd.FlatDict(user_dict),
                            identifier,
                            template,
                        )
                        if "orcid" not in user_dict:
                            continue
                        add_specific_metadata(
                            APM_IDENTIFIER_TO_NEXUS,
                            fd.FlatDict(user_dict),
                            identifier,
                            template,
                        )
                        user_id += 1
        return template

    def parse_range(self, template: dict) -> dict:
        identifier = [self.entry_id]
        add_specific_metadata(APM_RANGE_TO_NEXUS, self.yml, identifier, template)
        return template

    def parse_recon(self, template: dict) -> dict:
        identifier = [self.entry_id]
        add_specific_metadata(APM_RECON_TO_NEXUS, self.yml, identifier, template)
        return template

    def parse_workflow(self, template: dict) -> dict:
        identifier = [self.entry_id]
        add_specific_metadata(APM_WORKFLOW_TO_NEXUS, self.yml, identifier, template)
        return template

    def parse(self, template: dict) -> dict:
        """Copy data from self into template the appdef instance."""
        self.parse_entry(template)
        self.parse_sample(template)
        self.parse_sample_composition(template)
        self.parse_specimen(template)
        self.parse_instrument_static(template)
        self.parse_instrument_dynamic(template)
        self.parse_pulser_source(template)
        self.parse_user(template)
        self.parse_range(template)
        self.parse_recon(template)
        self.parse_workflow(template)
        return template
