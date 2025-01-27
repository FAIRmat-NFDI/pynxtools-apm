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
import re

import flatdict as fd
import numpy as np
import yaml
from ase.data import chemical_symbols
from ifes_apt_tc_data_modeling.nexus.nx_ion import NxField, NxIon
from ifes_apt_tc_data_modeling.utils.definitions import (
    MAX_NUMBER_OF_ATOMS_PER_ION,
    MAX_NUMBER_OF_ION_SPECIES,
)
from ifes_apt_tc_data_modeling.utils.utils import create_nuclide_hash

from pynxtools_apm.concepts.mapping_functors_pint import add_specific_metadata_pint
from pynxtools_apm.configurations.cameca_cfg import APM_CAMECA_TO_NEXUS
from pynxtools_apm.utils.load_ranging import add_unknown_iontype


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
            self.yml = fd.FlatDict({}, delimiter="/")
            return

    def parse_event_statistics(self, template: dict) -> dict:
        """Interpret event statistics resulting from hit-finding algorithm."""
        event_type_names = ["Golden", "Incomplete", "Multiple", "Partials", "Records"]
        vals = []
        for evn_name in event_type_names:
            vals.append(f"fTotalEvent{evn_name}")

        if all(val in self.yml for val in vals):
            trg = f"/ENTRY[entry{self.entry_id}]/atom_probe/hit_finding/"
            template[f"{trg}hit_quality_types"] = str(
                [evn_name.lower() for evn_name in event_type_names]
            )
            cnts = np.zeros((5,), np.uint64)
            for idx, evn_name in enumerate(event_type_names):
                cnts[idx] = self.yml[f"fTotalEvent{evn_name}"]
            template[f"{trg}total_hit_quality"] = cnts
        return template

    def parse_versions(self, template: dict) -> dict:
        """Interpret Cameca-specific versions of software."""
        if all(
            val in self.yml
            for val in ["fCernRootVersion", "fImagoRootVersion"]  # "fImagoRootDate"
        ):
            trg = f"/ENTRY[entry{self.entry_id}]/atom_probe/hit_finding/programID[program1]/"
            template[f"{trg}program"] = "CernRoot"
            template[f"{trg}program/@version"] = self.yml["fCernRootVersion"].strip()
            trg = f"/ENTRY[entry{self.entry_id}]/atom_probe/hit_finding/programID[program2]/"
            template[f"{trg}program"] = "ImagoRoot"
            template[f"{trg}program/@version"] = self.yml["fImagoRootVersion"].strip()
            # template[f"{trg}program/@date"] = self.yml["fImagoRootDate"].strip()
        if all(
            val in self.yml
            for val in [
                "fAcqBuildVersion",
                "fAcqMajorVersion",
                "fAcqMinorVersion",
            ]  # fStreamVersion
        ):
            trg = (
                f"/ENTRY[entry{self.entry_id}]/atom_probe/raw_data/programID[program1]/"
            )
            template[f"{trg}program"] = "IVAS or AP Suite Acquisition"
            template[f"{trg}program/@version"] = (
                f"{self.yml['fAcqMajorVersion']}.{self.yml['fAcqMinorVersion']}.{self.yml['fAcqBuildVersion']}"
            )
            # template[f"{trg}program/@stream"] = f"{self.yml['fStreamVersion']}"
        return template

    def parse_comments(self, template: dict) -> dict:
        """Concatenate several types of comments into one."""
        free_text = ""
        for keyword in ["fName", "fProjectName", "fComments", "fUserID"]:
            if keyword in self.yml:
                if self.yml[keyword] != "":
                    free_text += self.yml[keyword]
                    free_text += "\n\n"
        template[f"/ENTRY[entry{self.entry_id}]/experiment_description"] = free_text
        return template

    def parse_acquisition_mode(self, template: dict) -> dict:
        return template

    def parse_ranging_definitions(self, template: dict) -> dict:
        """Interpret human-readable ELN input to generate consistent composition table."""
        src = "fCMassRanges"
        if src in self.yml:
            if isinstance(self.yml[src], list):
                unique_elements = set()
                add_unknown_iontype(template, entry_id=1)
                ion_id = 0

                for rng_def in self.yml[src]:
                    ion_id += 1
                    if not all(
                        val in rng_def
                        for val in [
                            "fIdentifier",
                            "fMassToChargeHigh",
                            "fMassToChargeLow",
                            "fMassToChargeVolume",
                            "fRngComposition",
                            "fRngName",
                        ]
                    ):
                        continue
                    line = rng_def["fRngComposition"].strip()
                    tmp = re.split(r"[\s=]+", line)
                    atoms = []
                    for entry in tmp:
                        element_multiplicity = re.split(r":+", entry)
                        if len(element_multiplicity) != 2:
                            raise ValueError(
                                f"Line {line}, element multiplicity is not "
                                f"correctly formatted {len(element_multiplicity)}!"
                            )
                        if (
                            element_multiplicity[0] in chemical_symbols[1::]
                            and np.uint32(element_multiplicity[1])
                            < MAX_NUMBER_OF_ION_SPECIES
                        ):
                            # TODO::check if range is significant
                            symbol = element_multiplicity[0]
                            atoms = np.append(
                                atoms, [symbol] * int(element_multiplicity[1])
                            )
                            unique_elements.add(symbol)

                    ion = NxIon(nuclide_hash=create_nuclide_hash(atoms), charge_state=0)
                    ion.add_range(
                        rng_def["fMassToChargeLow"], rng_def["fMassToChargeHigh"]
                    )
                    ion.comment = NxField(rng_def["fRngName"], "")
                    ion.apply_combinatorics()
                    ion.update_human_readable_name()
                    # print(ion.report())

                    trg = f"/ENTRY[entry{self.entry_id}]/atom_probe/ranging/peak_identification/ionID[ion{ion_id}]/"
                    template[f"{trg}nuclide_hash"] = np.asarray(
                        ion.nuclide_hash.values, np.uint16
                    )
                    template[f"{trg}charge_state"] = np.int8(ion.charge_state.values)
                    template[f"{trg}mass_to_charge_range"] = np.asarray(
                        ion.ranges.values, np.float32
                    )
                    template[f"{trg}mass_to_charge_range/@units"] = (
                        "Da"  # ion.ranges.unit
                    )
                    template[f"{trg}nuclide_list"] = ion.nuclide_list.values
                    template[f"{trg}name"] = ion.name.values

                    if ion.charge_state_model["n_cand"] > 0:
                        path = f"{trg}charge_state_analysis/"
                        template[f"{path}nuclides"] = np.asarray(
                            ion.nuclide_hash.values, np.uint16
                        )
                        template[f"{path}mass_to_charge_range"] = np.asarray(
                            ion.ranges.values, np.float32
                        )
                        template[f"{path}mass_to_charge_range/@units"] = (
                            "Da"  # ion.ranges.unit
                        )
                        template[f"{path}min_abundance"] = np.float64(
                            ion.charge_state_model["min_abundance"]
                        )
                        template[f"{path}min_abundance_product"] = np.float64(
                            ion.charge_state_model["min_abundance_product"]
                        )
                        template[f"{path}min_half_life"] = np.float64(
                            ion.charge_state_model["min_half_life"]
                        )
                        template[f"{path}min_half_life/@units"] = "s"
                        template[f"{path}sacrifice_isotopic_uniqueness"] = np.uint8(
                            ion.charge_state_model["sacrifice_isotopic_uniqueness"]
                        )
                        if ion.charge_state_model["n_cand"] == 1:
                            template[f"{path}nuclide_hash"] = np.asarray(
                                ion.charge_state_model["nuclide_hash"], np.uint16
                            )
                            template[f"{path}charge_state"] = np.int8(
                                ion.charge_state_model["charge_state"]
                            )
                            template[f"{path}mass"] = np.float64(
                                ion.charge_state_model["mass"]
                            )
                            template[f"{path}mass/@units"] = "Da"
                            template[f"{path}natural_abundance_product"] = np.float64(
                                ion.charge_state_model["natural_abundance_product"]
                            )
                            template[f"{path}shortest_half_life"] = np.float64(
                                ion.charge_state_model["shortest_half_life"]
                            )
                            template[f"{path}shortest_half_life/@units"] = "s"
                        elif ion.charge_state_model["n_cand"] > 1:
                            template[f"{path}nuclide_hash"] = {
                                "compress": np.asarray(
                                    ion.charge_state_model["nuclide_hash"], np.uint16
                                ),
                                "strength": 1,
                            }
                            template[f"{path}charge_state"] = {
                                "compress": np.asarray(
                                    ion.charge_state_model["charge_state"], np.int8
                                ),
                                "strength": 1,
                            }
                            template[f"{path}mass"] = {
                                "compress": np.asarray(
                                    ion.charge_state_model["mass"], np.float64
                                ),
                                "strength": 1,
                            }
                            template[f"{path}mass/@units"] = "Da"
                            template[f"{path}natural_abundance_product"] = {
                                "compress": np.asarray(
                                    ion.charge_state_model["natural_abundance_product"],
                                    np.float64,
                                ),
                                "strength": 1,
                            }
                            template[f"{path}shortest_half_life"] = {
                                "compress": np.asarray(
                                    ion.charge_state_model["shortest_half_life"],
                                    np.float64,
                                ),
                                "strength": 1,
                            }
                            template[f"{path}shortest_half_life/@units"] = "s"

                trg = f"/ENTRY[entry{self.entry_id}]/atom_probe/ranging/"
                template[f"{trg}number_of_ion_types"] = np.uint32(ion_id)
                template[f"{trg}maximum_number_of_atoms_per_molecular_ion"] = np.uint32(
                    MAX_NUMBER_OF_ATOMS_PER_ION
                )

                atom_types_str = ", ".join(list(unique_elements))
                if atom_types_str != "":
                    trg = f"/ENTRY[entry{self.entry_id}]/specimen/"
                    template[f"{trg}type"] = "experiment"
                    template[f"{trg}atom_types"] = atom_types_str

        return template

    def parse(self, template: dict) -> dict:
        """Copy data from self into template the appdef instance."""
        self.parse_event_statistics(template)
        self.parse_versions(template)
        self.parse_comments(template)
        # self.parse_acquisition_mode(template)
        self.parse_ranging_definitions(template)
        identifier = [self.entry_id, 1]
        add_specific_metadata_pint(APM_CAMECA_TO_NEXUS, self.yml, identifier, template)
        return template
