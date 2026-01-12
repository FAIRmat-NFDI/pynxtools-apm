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

    trg = f"{prefix}/atom_probeID[atom_probe]/reconstruction/reconstructed_positions"
    xyz = pos_file.get_reconstructed_positions()
    template[f"{trg}"] = {
        "compress": np.asarray(xyz.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(xyz.magnitude, np.float32), (0, 1)
        ),
    }
    template[f"{trg}/@units"] = f"{xyz.units}"
    del xyz

    trg = f"{prefix}/atom_probeID[atom_probe]/mass_to_charge_conversion/mass_to_charge"
    m_z = pos_file.get_mass_to_charge_state_ratio()
    template[f"{trg}"] = {
        "compress": np.asarray(m_z.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(m_z.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}/@units"] = f"{m_z.units}"
    del m_z
    return template


def extract_data_from_epos_file(file_path: str, prefix: str, template: dict) -> dict:
    """Add those required information which an ePOS file has."""
    logger.debug(f"Extracting data from EPOS file: {file_path}")
    epos_file = ReadEposFileFormat(file_path)

    trg = f"{prefix}/atom_probeID[atom_probe]/reconstruction/reconstructed_positions"
    xyz = epos_file.get_reconstructed_positions()
    template[f"{trg}"] = {
        "compress": np.asarray(xyz.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(xyz.magnitude, np.float32), (0, 1)
        ),
    }
    template[f"{trg}/@units"] = f"{xyz.units}"
    del xyz

    trg = f"{prefix}/atom_probeID[atom_probe]/mass_to_charge_conversion/mass_to_charge"
    m_z = epos_file.get_mass_to_charge_state_ratio()
    template[f"{trg}"] = {
        "compress": np.asarray(m_z.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(m_z.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}/@units"] = f"{m_z.units}"
    del m_z

    trg = f"{prefix}/measurement/eventID[event1]/instrument/pulser/standing_voltage"
    standing_voltage = epos_file.get_standing_voltage()
    template[f"{trg}"] = {
        "compress": np.asarray(standing_voltage.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(standing_voltage.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}/@units"] = f"{standing_voltage.units}"
    del standing_voltage

    trg = f"{prefix}/measurement/eventID[event1]/instrument/pulser/pulse_voltage"
    pulse_voltage = epos_file.get_pulse_voltage()
    template[f"{trg}"] = {
        "compress": np.asarray(pulse_voltage.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(pulse_voltage.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}/@units"] = f"{pulse_voltage.units}"
    del pulse_voltage

    trg = f"{prefix}/atom_probeID[atom_probe]/voltage_and_bowl/raw_tof"
    raw_time_of_flight = epos_file.get_raw_time_of_flight()
    template[f"{trg}"] = {
        "compress": np.asarray(raw_time_of_flight.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(raw_time_of_flight.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}/@units"] = f"{raw_time_of_flight.units}"
    del raw_time_of_flight

    trg = f"{prefix}/atom_probeID[atom_probe]/hit_finding/hit_positions"
    hit_positions = epos_file.get_hit_positions()
    template[f"{trg}"] = {
        "compress": np.asarray(hit_positions.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(hit_positions.magnitude, np.float32), (0, 1)
        ),
    }
    template[f"{trg}/@units"] = f"{hit_positions.units}"
    del hit_positions

    # add multiplicity data from epos
    return template


def extract_data_from_apt_file(file_path: str, prefix: str, template: dict) -> dict:
    """Add those required information which a APT file has."""
    logger.debug(f"Extracting data from APT file: {file_path}")
    apt_file = ReadAptFileFormat(file_path)

    # def add_to_template(hdf_path: str, quantity_name: str, dtype: type, chunk_priority: tuple)

    trg = f"{prefix}/atom_probeID[atom_probe]/reconstruction/reconstructed_positions"
    xyz = apt_file.get_named_quantity("Position")
    if xyz is not None:
        template[f"{trg}"] = {
            "compress": np.asarray(xyz.magnitude, np.float32),
            "strength": DEFAULT_COMPRESSION_LEVEL,
            "chunks": prioritized_axes_heuristic(
                np.asarray(xyz.magnitude, np.float32), (0, 1)
            ),
        }
        template[f"{trg}/@units"] = f"{xyz.units}"
    del xyz

    trg = f"{prefix}/atom_probeID[atom_probe]/mass_to_charge_conversion/mass_to_charge"
    m_z = apt_file.get_named_quantity("Mass")
    if m_z is not None:
        template[f"{trg}"] = {
            "compress": np.asarray(m_z.magnitude, np.float32),
            "strength": DEFAULT_COMPRESSION_LEVEL,
            "chunks": prioritized_axes_heuristic(
                np.asarray(m_z.magnitude, np.float32), (0,)
            ),
        }
        template[f"{trg}/@units"] = f"{m_z.units}"
    del m_z
    # all less explored optional branches in an APT6 file can also already
    # be accessed via the aptfile.get_named_quantity function
    # but it needs to be checked if this returns reasonable values
    # and specifically what these values logically mean, interaction with
    # Cameca as well as the community is vital here
    trg = f"{prefix}/measurement/eventID[event1]/instrument/pulser/standing_voltage"
    standing_voltage = apt_file.get_named_quantity("Voltage")
    if standing_voltage is not None:
        template[f"{trg}"] = {
            "compress": np.asarray(standing_voltage.magnitude, np.float32),
            "strength": DEFAULT_COMPRESSION_LEVEL,
            "chunks": prioritized_axes_heuristic(
                np.asarray(standing_voltage.magnitude, np.float32), (0,)
            ),
        }
        template[f"{trg}/@units"] = f"{standing_voltage.units}"
    del standing_voltage

    trg = f"{prefix}/measurement/eventID[event1]/instrument/pulser/pulse_voltage"
    for name_in_a_version in ["Vap", "Pulse Voltage"]:
        voltage = apt_file.get_named_quantity(name_in_a_version)
        if voltage is not None:
            template[f"{trg}"] = {
                "compress": np.asarray(voltage.magnitude, np.float32),
                "strength": DEFAULT_COMPRESSION_LEVEL,
                "chunks": prioritized_axes_heuristic(
                    np.asarray(voltage.magnitude, np.float32), (0,)
                ),
            }
            template[f"{trg}/@units"] = f"{voltage.units}"
            break
    try:
        del voltage
    except NameError:
        pass

    trg = f"{prefix}/measurement/eventID[event1]/instrument/reflectron/voltage"
    reflectron_voltage = apt_file.get_named_quantity("Vref")
    if reflectron_voltage is not None:
        template[f"{trg}"] = {
            "compress": np.asarray(reflectron_voltage.magnitude, np.float32),
            "strength": DEFAULT_COMPRESSION_LEVEL,
            "chunks": prioritized_axes_heuristic(
                np.asarray(reflectron_voltage.magnitude, np.float32), (0,)
            ),
        }
        template[f"{trg}/@units"] = f"{reflectron_voltage.units}"
    del reflectron_voltage

    trg = f"{prefix}/atom_probeID[atom_probe]/hit_finding/hit_positions"
    detx = apt_file.get_named_quantity("XDet_mm")
    dety = apt_file.get_named_quantity("YDet_mm")
    if detx is not None and dety is not None:
        if (
            np.shape(detx.magnitude) == np.shape(dety.magnitude)
            and f"{detx.units}" == f"{dety.units}"
        ):
            values = np.zeros((np.shape(detx.magnitude), 2), np.float32)
            values[:, 0] = detx.magnitude
            values[:, 1] = dety.magnitude
            template[f"{trg}"] = {
                "compress": np.asarray(values, np.float32),
                "strength": DEFAULT_COMPRESSION_LEVEL,
                "chunks": prioritized_axes_heuristic(
                    np.asarray(values, np.float32), (0, 1)
                ),
            }
            template[f"{trg}/@units"] = f"{detx.units}"
    del detx, dety
    return template


def extract_data_from_ato_file(file_path: str, prefix: str, template: dict) -> dict:
    """Add those required information which a ATO file has."""
    logger.debug(f"Extracting data from ATO file: {file_path}")
    ato_file = ReadAtoFileFormat(file_path)

    trg = f"{prefix}/atom_probeID[atom_probe]/reconstruction/reconstructed_positions"
    xyz = ato_file.get_reconstructed_positions()
    template[f"{trg}"] = {
        "compress": np.asarray(xyz.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(xyz.magnitude, np.float32), (0, 1)
        ),
    }
    template[f"{trg}/@units"] = f"{xyz.units}"
    del xyz

    trg = f"{prefix}/atom_probeID[atom_probe]/mass_to_charge_conversion/mass_to_charge"
    m_z = ato_file.get_mass_to_charge_state_ratio()
    template[f"{trg}"] = {
        "compress": np.asarray(m_z.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(m_z.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}/@units"] = f"{m_z.units}"
    del m_z
    return template


def extract_data_from_csv_file(file_path: str, prefix: str, template: dict) -> dict:
    """Add those required information which a CSV file has."""
    logger.debug(f"Extracting data from CSV file: {file_path}")
    csv_file = ReadCsvFileFormat(file_path)

    trg = f"{prefix}/atom_probeID[atom_probe]/reconstruction/reconstructed_positions"
    xyz = csv_file.get_reconstructed_positions()
    template[f"{trg}"] = {
        "compress": np.asarray(xyz.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(xyz.magnitude, np.float32), (0, 1)
        ),
    }
    template[f"{trg}/@units"] = f"{xyz.units}"
    del xyz

    trg = f"{prefix}/atom_probeID[atom_probe]/mass_to_charge_conversion/mass_to_charge"
    m_z = csv_file.get_mass_to_charge_state_ratio()
    template[f"{trg}"] = {
        "compress": np.asarray(m_z.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(m_z.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}/@units"] = f"{m_z.units}"
    del m_z
    return template


def extract_data_from_pyc_file(file_path: str, prefix: str, template: dict) -> dict:
    """Add those required information which a pyccapt/calibration HDF5 file has."""
    logger.debug(f"Extracting data from pyccapt/calibration HDF5 file: {file_path}")
    pyc_file = ReadPyccaptCalibrationFileFormat(file_path)

    trg = f"{prefix}/atom_probeID[atom_probe]/reconstruction/reconstructed_positions"
    xyz = pyc_file.get_reconstructed_positions()
    template[f"{trg}"] = {
        "compress": np.asarray(xyz.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(xyz.magnitude, np.float32), (0, 1)
        ),
    }
    template[f"{trg}/@units"] = f"{xyz.units}"
    del xyz

    trg = f"{prefix}/atom_probeID[atom_probe]/mass_to_charge_conversion/mass_to_charge"
    m_z = pyc_file.get_mass_to_charge_state_ratio()
    template[f"{trg}"] = {
        "compress": np.asarray(m_z.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(m_z.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}/@units"] = f"{m_z.units}"
    del m_z

    trg = f"{prefix}/atom_probeID[atom_probe]/voltage_and_bowl/raw_tof"
    raw_time_of_flight = pyc_file.get_raw_time_of_flight()
    template[f"{trg}"] = {
        "compress": np.asarray(raw_time_of_flight.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(raw_time_of_flight.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}/@units"] = f"{raw_time_of_flight.units}"
    del raw_time_of_flight

    trg = f"{prefix}/atom_probeID[atom_probe]/voltage_and_bowl/calibrated_tof"
    calibrated_time_of_flight = pyc_file.get_calibrated_time_of_flight()
    template[f"{trg}"] = {
        "compress": np.asarray(calibrated_time_of_flight.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(calibrated_time_of_flight.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}/@units"] = f"{calibrated_time_of_flight.units}"
    del calibrated_time_of_flight

    trg = f"{prefix}/measurement/eventID[event1]/instrument/pulser/standing_voltage"
    standing_voltage = pyc_file.get_standing_voltage()
    template[f"{trg}"] = {
        "compress": np.asarray(standing_voltage.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(standing_voltage.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}/@units"] = f"{standing_voltage.units}"
    del standing_voltage

    trg = f"{prefix}/measurement/eventID[event1]/instrument/pulser/pulse_voltage"
    pulse_voltage = pyc_file.get_pulse_voltage()
    template[f"{trg}"] = {
        "compress": np.asarray(pulse_voltage.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(pulse_voltage.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}/@units"] = f"{pulse_voltage.units}"
    del pulse_voltage

    trg = f"{prefix}/atom_probeID[atom_probe]/hit_finding/hit_positions"
    hit_positions = pyc_file.get_detector_hit_positions()
    template[f"{trg}"] = {
        "compress": np.asarray(hit_positions.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(hit_positions.magnitude, np.float32), (0, 1)
        ),
    }
    template[f"{trg}/@units"] = f"{hit_positions.units}"
    del hit_positions

    return template


def extract_data_from_cameca_hfive_file(
    file_path: str, prefix: str, template: dict
) -> dict:
    """Add those required information which a Cameca HDF5 file has."""
    logger.debug(f"Extracting data from Cameca HDF5 file: {file_path}")
    hfive_file = ReadCamecaHfiveFileFormat(file_path)

    trg = f"{prefix}/atom_probeID[atom_probe]/reconstruction/reconstructed_positions"
    xyz = hfive_file.get_reconstructed_positions()
    template[f"{trg}"] = {
        "compress": np.asarray(xyz.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(xyz.magnitude, np.float32), (0, 1)
        ),
    }
    template[f"{trg}/@units"] = f"{xyz.units}"
    del xyz

    trg = f"{prefix}/atom_probeID[atom_probe]/mass_to_charge_conversion/mass_to_charge"
    m_z = hfive_file.get_mass_to_charge_state_ratio()
    template[f"{trg}"] = {
        "compress": np.asarray(m_z.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(m_z.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}/@units"] = f"{m_z.units}"
    del m_z
    return template


def extract_data_from_ops_file(file_path: str, prefix: str, template: dict) -> dict:
    """Add those required information which a PoSAP ops file has."""
    logger.debug(f"Extracting data from PoSAP OPS file: {file_path}")
    ops_file = ReadOpsFileFormat(file_path)

    if "time_stamp" in ops_file.instrument:
        trg = f"{prefix}/start_time"
        template[f"{trg}"] = ops_file.instrument["time_stamp"]

    trg = f"{prefix}/measurement/voltage_curve/"
    if not all(
        name in ops_file.voltages
        for name in ["standing_voltage", "pulse_voltage", "next_hit_group_offset"]
    ):
        return template
    reference_shape = np.shape(ops_file.voltages["standing_voltage"].magnitude)
    if not all(
        np.shape(ops_file.voltages[name]) == reference_shape
        for name in ["pulse_voltage", "next_hit_group_offset"]
    ):
        return template
    del reference_shape
    if (
        not f"{ops_file.voltages['standing_voltage'].units}"
        == f"{ops_file.voltages['pulse_voltage'].units}"
    ):
        return template
    voltage = np.zeros(
        (np.shape(ops_file.voltages["standing_voltage"].magnitude)[0],),
        np.float32,
    )
    for name in ["standing_voltage", "pulse_voltage"]:
        voltage += ops_file.voltages[name].magnitude

    template[f"{trg}title"] = f"Voltage curve"
    template[f"{trg}@signal"] = "voltage"
    template[f"{trg}@axes"] = "axis_evaporation_id"
    template[f"{trg}@AXISNAME_indices[@axis_evaporation_id_indices]"] = np.uint32(0)
    template[f"{trg}DATA[voltage]"] = {
        "compress": np.asarray(voltage, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(voltage, np.float32),
            (0,),
        ),
    }
    template[f"{trg}DATA[voltage]/@units"] = (
        f"{ops_file.voltages['standing_voltage'].units}"
    )
    template[f"{trg}DATA[voltage]/@long_name"] = (
        f"Standing voltage + pulse voltage ({ops_file.voltages['standing_voltage'].units})"
    )
    template[f"{trg}AXISNAME[axis_evaporation_id]"] = {
        "compress": np.asarray(
            ops_file.voltages["next_hit_group_offset"].magnitude,
            np.uint32,
        ),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(
                ops_file.voltages["next_hit_group_offset"].magnitude,
                np.uint32,
            ),
            (0,),
        ),
    }
    template[f"{trg}AXISNAME[axis_evaporation_id]/@long_name"] = (
        f"Next hit group offset"  # TODO
    )

    return template


def extract_data_from_stuttgart_apyt_raw_file(
    file_path: str, prefix: str, template: dict
) -> dict:
    """Add those required information which a Stuttgart RAW file has."""
    logger.debug(f"Extracting data from Stuttgart RAW file: {file_path}")
    apyt_file = ReadStuttgartApytRawFileFormat(file_path)

    trg = f"{prefix}/measurement/eventID[event1]/instrument/pulser/standing_voltage"
    standing_voltage = apyt_file.get_base_voltage()
    template[f"{trg}"] = {
        "compress": np.asarray(standing_voltage.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(standing_voltage.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}/@units"] = f"{standing_voltage.units}"
    del standing_voltage

    trg = f"{prefix}/measurement/eventID[event1]/instrument/pulser/pulse_voltage"
    pulse_voltage = apyt_file.get_pulse_voltage()
    template[f"{trg}"] = {
        "compress": np.asarray(pulse_voltage.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(pulse_voltage.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}/@units"] = f"{pulse_voltage.units}"
    del pulse_voltage

    trg = f"{prefix}/atom_probeID[atom_probe]/voltage_and_bowl/raw_tof"
    raw_time_of_flight = apyt_file.get_raw_time_of_flight()
    template[f"{trg}"] = {
        "compress": np.asarray(raw_time_of_flight.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(raw_time_of_flight.magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}/@units"] = f"{raw_time_of_flight.units}"
    del raw_time_of_flight

    return template


def extract_data_from_stuttgart_apyt_mass_spectrum_file(
    file_path: str, prefix: str, template: dict
) -> dict:
    """Add those required information which an APyT _trimmed.txt file has."""
    logger.debug(f"Extracting data from APyT _trimmed.txt file: {file_path}")
    apyt_file = ReadStuttgartApytSpectrumAlignFileFormat(file_path)

    trg = f"{prefix}/atom_probeID[atom_probe]/ranging/mass_to_charge_distribution/"
    m_z = apyt_file.get_complete_spectrum()

    # template[f"{trg}programID[program1]/program"] = "APyT"
    # template[f"{trg}programID[program1]/program/@version"] = "UNKNOWN VERSION"

    number_of_bins = np.shape(m_z[0].magnitude)[0]
    template[f"{trg}min_mass_to_charge"] = np.float32(m_z[0].magnitude)
    template[f"{trg}min_mass_to_charge/@units"] = f"{m_z[0].units}"
    template[f"{trg}max_mass_to_charge"] = np.float32(m_z[0].magnitude)
    template[f"{trg}max_mass_to_charge/@units"] = f"{m_z[0].units}"
    template[f"{trg}n_mass_to_charge"] = np.uint32(number_of_bins)
    trg = (
        f"{prefix}/atom_probeID[atom_probe]/ranging/"
        f"mass_to_charge_distribution/mass_spectrum/"
    )
    template[f"{trg}title"] = (
        f"Mass spectrum ({np.around(m_z[0].magnitude[1] - m_z[0].magnitude[0], decimals=3) if number_of_bins > 1 else ''} {m_z[0].units} binning)"
    )
    template[f"{trg}@signal"] = "intensity"
    template[f"{trg}@axes"] = "axis_mass_to_charge"
    template[f"{trg}@AXISNAME_indices[@axis_mass_to_charge_indices]"] = np.uint32(0)
    template[f"{trg}DATA[intensity]"] = {
        "compress": np.asarray(m_z[1].magnitude, np.uint32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(m_z[1].magnitude, np.uint32), (0,)
        ),
    }
    template[f"{trg}DATA[intensity]/@long_name"] = "Intensity (1)"  # Counts (1)"
    template[f"{trg}AXISNAME[axis_mass_to_charge]"] = {
        "compress": np.asarray(m_z[0].magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(m_z[0].magnitude, np.float32), (0,)
        ),
    }
    template[f"{trg}AXISNAME[axis_mass_to_charge]/@units"] = f"{m_z[0].units}"
    template[f"{trg}AXISNAME[axis_mass_to_charge]/@long_name"] = (
        f"Mass-to-charge-state-ratio (Da)"  # Da !!
    )
    logger.debug(
        f"Plot mass spectrum ({np.around(m_z[0].magnitude[1] - m_z[0].magnitude[0], decimals=3) if number_of_bins > 1 else ''} {m_z[0].units} binning)"
    )
    return template


def extract_data_from_stuttgart_apyt_recon_file(
    file_path: str, prefix: str, template: dict
) -> dict:
    """Add those required information which a APyT _xyz.txt file has."""
    logger.debug(f"Extracting data from APyT _xyz.txt file: {file_path}")
    apyt_file = ReadStuttgartApytReconstructionFileFormat(file_path)

    trg = f"{prefix}/atom_probeID[atom_probe]/reconstruction/reconstructed_positions"
    xyz = apyt_file.get_reconstructed_positions()
    template[f"{trg}"] = {
        "compress": np.asarray(xyz.magnitude, np.float32),
        "strength": DEFAULT_COMPRESSION_LEVEL,
        "chunks": prioritized_axes_heuristic(
            np.asarray(xyz.magnitude, np.float32), (0, 1)
        ),
    }
    template[f"{trg}/@units"] = f"{xyz.units}"
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
        prfx = f"/ENTRY[entry{self.meta['entry_id']}]"
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
