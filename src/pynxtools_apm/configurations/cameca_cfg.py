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
"""Dict mapping custom schema instances from custom yaml file on concepts in NXapm."""

from typing import Any, Dict

from pynxtools_apm.utils.pint_custom_unit_registry import ureg

APM_CAMECA_TO_NEXUS: Dict[str, Any] = {
    "prefix_trg": "/ENTRY[entry*]",
    "prefix_src": "",
    "map": [
        ("reconstruction/quality", "fQuality"),
        ("reconstruction/primary_element", "fPrimaryElement"),
        ("measurement/instrument/local_electrode/name", "fApertureName"),
        ("measurement/instrument/instrument_name", "fAtomProbeName"),
        ("measurement/instrument/fabrication/model", "fLeapModel"),
        (
            "measurement/instrument/pulser/SOURCE[sourceID]/fabrication/model",
            "fLaserModel",
        ),
        ("measurement/instrument/comments", "fInstrumentComment"),
        ("atom_probe/raw_data/serialized/path", "fRawPathName"),
        ("measurement/status", "fResults"),
        ("specimen/description", "fSpecimenCondition"),
        ("specimen/alias", "fSpecimenName"),
        ("start_time", "fStartISO8601"),
    ],
    "map_to_f8": [
        ("reconstruction/efficiency", "fEfficiency"),
        (
            "reconstruction/evaporation_field",
            ureg.volt / ureg.nanometer**2,
            "fEvaporationField",
        ),
        ("reconstruction/flight_path", ureg.millimeter, "fFlightPath"),
        ("reconstruction/image_compression", "??", "fImageCompression"),
        ("reconstruction/kfactor", "??", "fKfactor"),
        ("reconstruction/volume", ureg.nanometer**3, "fReconVolume"),
        ("reconstruction/shank_angle", ureg.degrees, "fShankAngle"),
        ("reconstruction/obb/xmax", ureg.nanometer, "fXmax"),
        ("reconstruction/obb/xmin", ureg.nanometer, "fXmin"),
        ("reconstruction/obb/ymax", ureg.nanometer, "fYmax"),
        ("reconstruction/obb/ymin", ureg.nanometer, "fYmin"),
        ("reconstruction/obb/zmax", ureg.nanometer, "fZmax"),
        ("reconstruction/obb/zmin", ureg.nanometer, "fZmin"),
        (
            "measurement/instrument/analysis_chamber/pressure",
            ureg.torr,
            "fAnalysisPressure",
        ),
        (
            "measurement/instrument/local_electrode/voltage",
            ureg.volt,
            "fAnodeAccelVoltage",
        ),
        ("elapsed_time", ureg.second, "fElapsedTime"),
        (
            "measurement/instrument/pulser/pulse_frequency",
            ureg.kilohertz,
            "fInitialPulserFreq",
        ),
        ("measurement/instrument/ion_detector/mcp_efficiency", "fMcpEfficiency"),
        ("measurement/instrument/ion_detector/mesh_efficiency", "fMeshEfficiency"),
        (
            "measurement/instrument/analysis_chamber/flight_path",
            ureg.millimeter,
            "fMaximumFlightPathMm",
        ),
        ("measurement/stage/specimen_temperature", ureg.kelvin, "fSpecimenTemperature"),
        (
            "atom_probe/voltage_and_bowl/tof_zero_estimate",
            ureg.nanosecond,
            "fT0Estimate",
        ),
    ],
    "map_to_u4": [
        ("measurement/instrument/fabrication/serial_number", "fSerialNumber"),
        ("run_number", "fRunNumber"),
    ],
}

# second
# ("experiment_description", ["fProjectName", "fName", "fComments"])
# ("operation_mode", "fAcquisitionMode")
# ("atom_probe/hit_finding/total_hit_quality", "fTotalEventGolden")
# ("", "fTotalEventIncomplete")
# ("", "fTotalEventMultiple")
# ("", "fTotalEventPartials")
# ("", "fTotalEventRecords")
# ("", "fAcqBuildVersion")
# ("", "fAcqMajorVersion")
# ("", "fAcqMinorVersion")
# ("", "fCernRootVersion")
# ("", "fImagoRootDate")
# ("", "fImagoRootVersion")
# ("", "fStreamVersion")]

# third
# ("", ureg.nanometer, "fTipRadius")
# ("", ureg.nanometer, "fTipRadius0")
# ("", ureg.volt, "fVoltage0")
# ("", "fUserID")
# ("", "fBcaSerialRev")
# ("", "fFirmwareVersion")
# ("", "fFlangeSerialNumber")
# ("", "fHvpsType")
# ("", "fLaserModelString")
# ("", "fLaserSerialNumber")
# ("", "fLcbSerialRev")
# ("", "fMcpSerialNumber")
# ("", "fPulserType")
# ("", "fTaSerialRev")
# ("", "fTdcType")
# ("", "fTargetEvapRate")
# ("", "fTargetPulseFraction")
# ("", "fPidAlgorithmID")
# ("", "fPidMaxInitialSlew")
# ("", "fPidMaxTurnOnSlew")
# ("", "fPidPropCoef")
# ("", "fPidPulsesPerUpdate")
# ("", "fPidTradHysterisis")
# ("", "fPidTradStep")
