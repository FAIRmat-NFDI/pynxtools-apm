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
"""Wrapping multiple parsers for vendor files with reconstructed dataset files."""

from typing import Any

import numpy as np
from ifes_apt_tc_data_modeling.apt.apt6_reader import ReadAptFileFormat
from ifes_apt_tc_data_modeling.ato.ato_reader import ReadAtoFileFormat
from ifes_apt_tc_data_modeling.cameca.cameca_reader import ReadCamecaHfiveFileFormat
from ifes_apt_tc_data_modeling.csv.csv_reader import ReadCsvFileFormat
from ifes_apt_tc_data_modeling.epos.epos_reader import ReadEposFileFormat
from ifes_apt_tc_data_modeling.ops.ops_reader import ReadOpsFileFormat
from ifes_apt_tc_data_modeling.pos.pos_reader import ReadPosFileFormat
from ifes_apt_tc_data_modeling.pyccapt.pyccapt_reader import (
    ReadPyccaptCalibrationFileFormat,
)
from ifes_apt_tc_data_modeling.stuttgart.apyt_reader import (
    ReadStuttgartApytMetadataFileFormat,
    ReadStuttgartApytReconstructionFileFormat,
    ReadStuttgartApytSpectrumAlignFileFormat,
)
from ifes_apt_tc_data_modeling.stuttgart.raw_reader import (
    ReadStuttgartApytRawFileFormat,
)

from pynxtools_apm.utils.custom_guess_chunk import prioritized_axes_heuristic
from pynxtools_apm.utils.custom_logging import logger
from pynxtools_apm.utils.default_config import DEFAULT_COMPRESSION_LEVEL
from pynxtools_apm.utils.io_case_logic import VALID_FILE_NAME_SUFFIX_RECON


def extract_data_from_pos_file(file_path: str, prefix: str, template: dict) -> dict:
    """Add those required information which a POS file has."""
    logger.debug(f"Extracting data from POS file: {file_path}")
    pos_file = ReadPosFileFormat(file_path)

    trg = f"{prefix}reconstruction/"
    xyz = pos_file.get_reconstructed_positions()
    template[f"{trg}reconstructed_positions"] = {
        "compress": np.asarray(xyz.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(xyz.magnitude, np.float32), (0, 1)
        ),
    }
    template[f"{trg}reconstructed_positions/@units"] = f"{xyz.units}"
    del xyz

    trg = f"{prefix}mass_to_charge_conversion/"
    m_z = pos_file.get_mass_to_charge_state_ratio()
    template[f"{trg}mass_to_charge"] = {
        "compress": np.asarray(m_z.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(m_z.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}mass_to_charge/@units"] = f"{m_z.units}"
    del m_z
    return template


def extract_data_from_epos_file(file_path: str, prefix: str, template: dict) -> dict:
    """Add those required information which an ePOS file has."""
    logger.debug(f"Extracting data from EPOS file: {file_path}")
    epos_file = ReadEposFileFormat(file_path)

    trg = f"{prefix}reconstruction/"
    xyz = epos_file.get_reconstructed_positions()
    template[f"{trg}reconstructed_positions"] = {
        "compress": np.asarray(xyz.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(xyz.magnitude, np.float32), (0, 1)
        ),
    }
    template[f"{trg}reconstructed_positions/@units"] = f"{xyz.units}"
    del xyz

    trg = f"{prefix}mass_to_charge_conversion/"
    m_z = epos_file.get_mass_to_charge_state_ratio()
    template[f"{trg}mass_to_charge"] = {
        "compress": np.asarray(m_z.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(m_z.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}mass_to_charge/@units"] = f"{m_z.units}"
    del m_z

    # add exporting of further data from epos

    return template


def extract_data_from_apt_file(file_path: str, prefix: str, template: dict) -> dict:
    """Add those required information which a APT file has."""
    logger.debug(f"Extracting data from APT file: {file_path}")
    apt_file = ReadAptFileFormat(file_path)

    trg = f"{prefix}reconstruction/"
    xyz = apt_file.get_named_quantity("Position")
    template[f"{trg}reconstructed_positions"] = {
        "compress": np.asarray(xyz.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(xyz.magnitude, np.float32), (0, 1)
        ),
    }
    template[f"{trg}reconstructed_positions/@units"] = f"{xyz.units}"
    del xyz

    trg = f"{prefix}mass_to_charge_conversion/"
    m_z = apt_file.get_named_quantity("Mass")
    template[f"{trg}mass_to_charge"] = {
        "compress": np.asarray(m_z.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(m_z.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}mass_to_charge/@units"] = f"{m_z.units}"
    del m_z
    # all less explored optional branches in an APT6 file can also already
    # be accessed via the aptfile.get_named_quantity function
    # but it needs to be checked if this returns reasonable values
    # and specifically what these values logically mean, interaction with
    # Cameca as well as the community is vital here
    return template


def extract_data_from_ato_file(file_path: str, prefix: str, template: dict) -> dict:
    """Add those required information which a ATO file has."""
    logger.debug(f"Extracting data from ATO file: {file_path}")
    ato_file = ReadAtoFileFormat(file_path)

    trg = f"{prefix}reconstruction/"
    xyz = ato_file.get_reconstructed_positions()
    template[f"{trg}reconstructed_positions"] = {
        "compress": np.asarray(xyz.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(xyz.magnitude, np.float32), (0, 1)
        ),
    }
    template[f"{trg}reconstructed_positions/@units"] = f"{xyz.units}"
    del xyz

    trg = f"{prefix}mass_to_charge_conversion/"
    m_z = ato_file.get_mass_to_charge_state_ratio()
    template[f"{trg}mass_to_charge"] = {
        "compress": np.asarray(m_z.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(m_z.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}mass_to_charge/@units"] = f"{m_z.units}"
    del m_z
    return template


def extract_data_from_csv_file(file_path: str, prefix: str, template: dict) -> dict:
    """Add those required information which a CSV file has."""
    logger.debug(f"Extracting data from CSV file: {file_path}")
    csv_file = ReadCsvFileFormat(file_path)

    trg = f"{prefix}reconstruction/"
    xyz = csv_file.get_reconstructed_positions()
    template[f"{trg}reconstructed_positions"] = {
        "compress": np.asarray(xyz.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(xyz.magnitude, np.float32), (0, 1)
        ),
    }
    template[f"{trg}reconstructed_positions/@units"] = f"{xyz.units}"
    del xyz

    trg = f"{prefix}mass_to_charge_conversion/"
    m_z = csv_file.get_mass_to_charge_state_ratio()
    template[f"{trg}mass_to_charge"] = {
        "compress": np.asarray(m_z.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(m_z.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}mass_to_charge/@units"] = f"{m_z.units}"
    del m_z
    return template


def extract_data_from_pyc_file(file_path: str, prefix: str, template: dict) -> dict:
    """Add those required information which a pyccapt/calibration HDF5 file has."""
    logger.debug(f"Extracting data from pyccapt/calibration HDF5 file: {file_path}")
    pycfile = ReadPyccaptCalibrationFileFormat(file_path)

    trg = f"{prefix}reconstruction/"
    xyz = pycfile.get_reconstructed_positions()
    template[f"{trg}reconstructed_positions"] = {
        "compress": np.asarray(xyz.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(xyz.magnitude, np.float32), (0, 1)
        ),
    }
    template[f"{trg}reconstructed_positions/@units"] = f"{xyz.units}"
    del xyz

    trg = f"{prefix}mass_to_charge_conversion/"
    m_z = pycfile.get_mass_to_charge_state_ratio()
    template[f"{trg}mass_to_charge"] = {
        "compress": np.asarray(m_z.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(m_z.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}mass_to_charge/@units"] = f"{m_z.units}"
    del m_z
    return template


def extract_data_from_cameca_hfive_file(
    file_path: str, prefix: str, template: dict
) -> dict:
    """Add those required information which a Cameca HDF5 file has."""
    logger.debug(f"Extracting data from Cameca HDF5 file: {file_path}")
    hfive_file = ReadCamecaHfiveFileFormat(file_path)

    trg = f"{prefix}reconstruction/"
    xyz = hfive_file.get_reconstructed_positions()
    template[f"{trg}reconstructed_positions"] = {
        "compress": np.asarray(xyz.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(xyz.magnitude, np.float32), (0, 1)
        ),
    }
    template[f"{trg}reconstructed_positions/@units"] = f"{xyz.units}"
    del xyz

    trg = f"{prefix}mass_to_charge_conversion/"
    m_z = hfive_file.get_mass_to_charge_state_ratio()
    template[f"{trg}mass_to_charge"] = {
        "compress": np.asarray(m_z.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(m_z.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}mass_to_charge/@units"] = f"{m_z.units}"
    del m_z
    return template


def extract_data_from_ops_file(file_path: str, prefix: str, template: dict) -> dict:
    """Add those required information which a PoSAP ops file has."""
    logger.debug(f"Extracting data from PoSAP OPS file: {file_path}")
    ops_file = ReadOpsFileFormat(file_path)
    # TODO
    return template


def extract_data_from_stuttgart_apyt_raw_file(
    file_path: str, prefix: str, template: dict
) -> dict:
    """Add those required information which a Stuttgart RAW file has."""
    logger.debug(f"Extracting data from Stuttgart RAW file: {file_path}")
    apyt_file = ReadStuttgartApytRawFileFormat(file_path)
    # TODO
    return template


def extract_data_from_stuttgart_apyt_mass_spectrum_file(
    file_path: str, prefix: str, template: dict
) -> dict:
    """Add those required information which an APyT _trimmed.txt file has."""
    logger.debug(f"Extracting data from APyT _trimmed.txt file: {file_path}")
    apyt_file = ReadStuttgartApytSpectrumAlignFileFormat(file_path)

    # TODO needs to go to mass spectrum
    """
    trg = f"{prefix}mass_to_charge_conversion/"
    m_z = apyt_file.get_complete_spectrum()
    template[f"{trg}mass_to_charge"] = {
        "compress": np.asarray(m_z.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(m_z.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}mass_to_charge/@units"] = f"{m_z.units}"
    del m_z
    """
    return template


def extract_data_from_stuttgart_apyt_recon_file(
    file_path: str, prefix: str, template: dict
) -> dict:
    """Add those required information which a APyT _xyz.txt file has."""
    logger.debug(f"Extracting data from APyT _xyz.txt file: {file_path}")
    apyt_file = ReadStuttgartApytReconstructionFileFormat(file_path)

    trg = f"{prefix}reconstruction/"
    xyz = apyt_file.get_reconstructed_positions()
    template[f"{trg}reconstructed_positions"] = {
        "compress": np.asarray(xyz.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(xyz.magnitude, np.float32), (0, 1)
        ),
    }
    template[f"{trg}reconstructed_positions/@units"] = f"{xyz.units}"
    del xyz
    return template


class IfesReconstructionParser:
    """Wrapper for multiple parsers for vendor specific files."""

    def __init__(self, file_path: str, entry_id: int):
        self.meta: dict[str, Any] = {
            "file_format": None,
            "file_path": file_path,
            "entry_id": entry_id,
        }
        for suffix in VALID_FILE_NAME_SUFFIX_RECON:
            if file_path.lower().endswith(suffix):
                self.meta["file_format"] = suffix
                break
        if self.meta["file_format"] is None:
            raise ValueError(f"{file_path} is not a supported reconstruction file!")

    def parse(self, template: dict) -> dict:
        """Copy data from self into template the appdef instance.

        Paths in template are prefixed by prefix and have to be compliant
        with the application definition.
        """
        prfx = f"/ENTRY[entry{self.meta['entry_id']}]/atom_probeID[atom_probe]/"
        if self.meta["file_path"] != "" and self.meta["file_format"] is not None:
            if self.meta["file_format"] == ".apt":
                extract_data_from_apt_file(self.meta["file_path"], prfx, template)
            if self.meta["file_format"] == ".epos":
                extract_data_from_epos_file(self.meta["file_path"], prfx, template)
            if self.meta["file_format"] == ".pos":
                extract_data_from_pos_file(self.meta["file_path"], prfx, template)
            if self.meta["file_format"] == ".ato":
                extract_data_from_ato_file(self.meta["file_path"], prfx, template)
            if self.meta["file_format"] == ".csv":
                extract_data_from_csv_file(self.meta["file_path"], prfx, template)
            if self.meta["file_format"] == ".h5":
                extract_data_from_pyc_file(self.meta["file_path"], prfx, template)
            if self.meta["file_format"] == ".hdf5":
                extract_data_from_cameca_hfive_file(
                    self.meta["file_path"], prfx, template
                )
            if self.meta["file_format"] == ".ops":
                extract_data_from_ops_file(self.meta["file_path"], prfx, template)
            if self.meta["file_format"] == ".raw":
                extract_data_from_stuttgart_apyt_raw_file(
                    self.meta["file_path"], prfx, template
                )
            if self.meta["file_format"] == "_trimmed.txt":
                extract_data_from_stuttgart_apyt_mass_spectrum_file(
                    self.meta["file_path"], prfx, template
                )
            if self.meta["file_format"] == "_xyz.txt":
                extract_data_from_stuttgart_apyt_recon_file(
                    self.meta["file_path"], prfx, template
                )
        return template
