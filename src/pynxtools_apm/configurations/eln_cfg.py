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
"""Dict mapping custom schema instances from eln_data.yaml file on concepts in NXapm."""

from pynxtools_apm.utils.pint_custom_unit_registry import ureg

APM_ENTRY_TO_NEXUS = {
    "prefix_trg": "/ENTRY[entry*]",
    "prefix_src": "entry/",
    "map": [
        "run_number",
        "operation_mode",
        "start_time",
        "end_time",
        "experiment_description",
        ("experiment_alias", "run_number"),
    ],
}


APM_SAMPLE_TO_NEXUS = {
    "prefix_trg": "/ENTRY[entry*]/sample",
    "prefix_src": "sample/",
    "map": [
        "alias",
        "description",
        ("type", "method"),
        ("identifier/identifier", "identifier/identifier"),
        ("identifier/service", "identifier/service"),
    ],
    "map_to_bool": [("identifier/is_persistent", "identifier/is_persistent")],
    "map_to_f8": [
        (
            "grain_diameter",
            ureg.micrometer,
            "grain_diameter/value",
            "grain_diameter/unit",
        ),
        (
            "grain_diameter_error",
            ureg.micrometer,
            "grain_diameter_error/value",
            "grain_diameter_error/unit",
        ),
        (
            "heat_treatment_temperature",
            ureg.degC,
            "heat_treatment_temperature/value",
            "heat_treatment_temperature/unit",
        ),
        (
            "heat_treatment_temperature_error",
            ureg.degC,
            "heat_treatment_temperature_error/value",
            "heat_treatment_temperature_error/unit",
        ),
        (
            "heat_treatment_quenching_rate",
            ureg.kelvin / ureg.second,
            "heat_treatment_quenching_rate/value",
            "heat_treatment_quenching_rate/unit",
        ),
        (
            "heat_treatment_quenching_rate_error",
            ureg.kelvin / ureg.second,
            "heat_treatment_quenching_rate_error/value",
            "heat_treatment_quenching_rate_error/unit",
        ),
    ],
}


APM_SPECIMEN_TO_NEXUS = {
    "prefix_trg": "/ENTRY[entry*]/specimen",
    "prefix_src": "specimen/",
    "map": [
        "alias",
        "preparation_date",
        "description",
        ("type", "method"),
        ("identifier/identifier", "identifier/identifier"),
        ("identifier/service", "identifier/service"),
    ],
    "map_to_f8": [
        (
            "initial_radius",
            ureg.nanometer,
            "initial_radius/value",
            "initial_radius/unit",
        ),
        ("shank_angle", ureg.degree, "shank_angle/value", "shank_angle/unit"),
    ],
    "map_to_bool": [
        "is_polycrystalline",
        "is_amorphous",
        ("identifier/is_persistent", "identifier/is_persistent"),
    ],
}


APM_INSTRUMENT_STATIC_TO_NEXUS = {
    "prefix_trg": "/ENTRY[entry*]/measurement/instrument",
    "prefix_src": "instrument/",
    "map": [
        "status",
        "instrument_name",
        "location",
        ("fabrication/vendor", "fabrication_vendor"),
        ("fabrication/model", "fabrication_model"),
        ("fabrication/identifier/identifier", "fabrication_identifier"),
        ("reflectron/status", "reflectron_status"),
        ("local_electrode/name", "local_electrode_name"),
        ("pulser/pulse_mode", "pulser/pulse_mode"),
    ],
    "map_to_f8": [
        (
            "analysis_chamber/flight_path",
            ureg.meter,
            "nominal_flight_path/value",
            "nominal_flight_path/unit",
        )
    ],
}


APM_INSTRUMENT_DYNAMIC_TO_NEXUS = {
    "prefix_trg": "/ENTRY[entry*]/measurement/event_data_apm_set/event_data_apm/instrument",
    "prefix_src": "instrument/",
    "use": [("control/target_detection_rate/@units", "ions/pulse")],
    "map": [
        "pulser_pulse_mode",
        ("control/evaporation_control", "evaporation_control"),
    ],
    "map_to_f8": [
        ("control/target_detection_rate", "target_detection_rate"),
        (
            "pulser/pulse_frequency",
            ureg.kilohertz,
            "pulser/pulse_frequency/value",
            "pulser/pulse_frequency/unit",
        ),
        ("pulser/pulse_fraction", "pulser/pulse_fraction"),
        (
            "analysis_chamber/chamber_pressure",
            ureg.bar,
            "chamber_pressure/value",
            "chamber_pressure/unit",
        ),
        (
            "stage_lab/base_temperature",
            ureg.kelvin,
            "base_temperature/value",
            "base_temperature/unit",
        ),
    ],
}


APM_RANGE_TO_NEXUS = {
    "prefix_trg": "/ENTRY[entry*]/atom_probe/ranging",
    "prefix_src": "ranging/",
    "map": [
        ("programID[program1]/program", "program"),
        ("programID[program1]/program/@version", "program_version"),
    ],
}


APM_RECON_TO_NEXUS = {
    "prefix_trg": "/ENTRY[entry*]/atom_probe/reconstruction",
    "prefix_src": "reconstruction/",
    "map": [
        "protocol_name",
        "crystallographic_calibration",
        "parameter",
        ("programID[program1]/program", "program"),
        ("programID[program1]/program/@version", "program_version"),
    ],
    "map_to_f8": [
        ("field_of_view", ureg.centimeter, "field_of_view/value", "field_of_view/unit")
    ],
}


APM_WORKFLOW_TO_NEXUS = {
    "prefix_trg": "/ENTRY[entry*]/atom_probe",
    "prefix_src": "workflow/",
    "sha256": [
        ("raw_data/serialized/checksum", "raw_dat_file"),
        ("hit_finding/serialized/checksum", "hit_dat_file"),
        ("reconstruction/config/checksum", "recon_cfg_file"),
    ],
}

# NeXus concept specific mapping tables which require special treatment as the current
# NOMAD Oasis custom schema implementation delivers them as a list of dictionaries instead
# of a directly flattenable list of key, value pairs

APM_USER_TO_NEXUS = {
    "prefix_trg": "/ENTRY[entry*]/USER[user*]",
    "prefix_src": "",
    "map": [
        "name",
        "affiliation",
        "address",
        "email",
        "telephone_number",
        "role",
        "social_media_name",
        "social_media_platform",
    ],
}


APM_IDENTIFIER_TO_NEXUS = {
    "prefix_trg": "/ENTRY[entry*]/USER[user*]",
    "prefix_src": "",
    "use": [("identifier/service", "orcid")],
    "map": [("identifier/identifier", "orcid")],
    "map_to_bool": [("identifier/is_persistent", "identifier/is_persistent")],
}
