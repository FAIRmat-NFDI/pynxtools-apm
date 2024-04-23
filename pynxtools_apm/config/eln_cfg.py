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

APM_ENTRY_TO_NEXUS = {
    "prefix_trg": "/ENTRY[entry*]",
    "prefix_src": "entry/",
    "map_to_str": [
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
        ("grain_diameter", "grain_diameter/value"),
        ("grain_diameter_error", "grain_diameter_error/value"),
        ("heat_treatment_temperature", "heat_treatment_temperature/value"),
        ("heat_treatment_temperature_error", "heat_treatment_temperature_error/value"),
        ("heat_treatment_quenching_rate", "heat_treatment_quenching_rate/value"),
        (
            "heat_treatment_quenching_rate_error",
            "heat_treatment_quenching_rate_error/value",
        ),
    ],
    "map_to_str": [
        "alias",
        "description",
        "method",
        ("grain_diameter/@units", "grain_diameter/unit"),
        ("grain_diameter_error/@units", "grain_diameter/unit"),
        ("heat_treatment_temperature/@units", "heat_treatment_temperature/unit"),
        (
            "heat_treatment_temperature_error/@units",
            "heat_treatment_temperature_error/unit",
        ),
        ("heat_treatment_quenching_rate/@units", "heat_treatment_quenching_rate/unit"),
        (
            "heat_treatment_quenching_rate_error/@units",
            "heat_treatment_quenching_rate_error/unit",
        ),
    ],
}


APM_SPECIMEN_TO_NEXUS = {
    "prefix_trg": "/ENTRY[entry*]/specimen",
    "prefix_src": "specimen/",
    "map": [
        ("initial_radius", "initial_radius/value"),
        ("shank_angle", "shank_angle/value"),
    ],
    "map_to_bool": ["is_polycrystalline", "is_amorphous"],
    "map_to_str": [
        "alias",
        "preparation_date",
        "description",
        "method",
        ("initial_radius/@units", "initial_radius/unit"),
        ("shank_angle/@units", "shank_angle/unit"),
    ],
}


APM_INSTRUMENT_STATIC_TO_NEXUS = {
    "prefix_trg": "/ENTRY[entry*]/measurement/instrument",
    "prefix_src": "atom_probe/",
    "map": [("analysis_chamber/flight_path", "nominal_flight_path/value")],
    "map_to_str": [
        "status",
        "instrument_name",
        "location",
        ("FABRICATION[fabrication]/vendor", "fabrication_vendor"),
        ("FABRICATION[fabrication]/model", "fabrication_model"),
        ("FABRICATION[fabrication]/identifier", "fabrication_identifier"),
        ("reflectron/status", "reflectron_status"),
        ("local_electrode/name", "local_electrode_name"),
        ("pulser/pulse_mode", "pulser/pulse_mode"),
        ("analysis_chamber/flight_path/@units", "nominal_flight_path/unit"),
    ],
}


APM_INSTRUMENT_DYNAMIC_TO_NEXUS = {
    "prefix_trg": "/ENTRY[entry*]/measurement/event_data_apm_set/EVENT_DATA_APM[event_data_apm]/instrument",
    "prefix_src": "atom_probe/",
    "use": [("control/target_detection_rate/@units", "ions/pulse")],
    "map": [
        ("control/target_detection_rate", "target_detection_rate"),
        ("pulser/pulse_frequency", "pulser/pulse_frequency/value"),
        ("pulser/pulse_fraction", "pulser/pulse_fraction"),
        ("analysis_chamber/chamber_pressure", "chamber_pressure/value"),
        ("stage_lab/base_temperature", "base_temperature/value"),
    ],
    "map_to_str": [
        ("control/evaporation_control", "evaporation_control"),
        ("pulser/pulse_frequency/@units", "pulser/pulse_frequency/unit"),
        ("analysis_chamber/chamber_pressure/@units", "chamber_pressure/unit"),
        ("stage_lab/base_temperature/@units", "base_temperature/unit"),
    ],
}


APM_RANGE_TO_NEXUS = {
    "prefix_trg": "/ENTRY[entry*]/atom_probe/ranging",
    "prefix_src": "ranging/",
    "map_to_str": [
        ("programID[program1]/program", "program"),
        ("programID[program1]/program/@version", "program_version"),
    ],
}


APM_RECON_TO_NEXUS = {
    "prefix_trg": "/ENTRY[entry*]/atom_probe/reconstruction",
    "prefix_src": "reconstruction/",
    "map": [("field_of_view", "field_of_view/value")],
    "map_to_str": [
        "protocol_name",
        "crystallographic_calibration",
        "parameter",
        ("programID[program1]/program", "program"),
        ("programID[program1]/program/@version", "program_version"),
        ("field_of_view/@units", "field_of_view/unit"),
    ],
}


APM_WORKFLOW_TO_NEXUS = {
    "prefix_trg": "/ENTRY[entry*]/atom_probe",
    "prefix_src": "workflow/",
    "sha256": [
        ("raw_data/SERIALIZED[serialized]/checksum", "raw_dat_file"),
        ("hit_finding/SERIALIZED[serialized]/checksum", "hit_dat_file"),
        ("reconstruction/config/checksum", "recon_cfg_file"),
    ],
}

# NeXus concept specific mapping tables which require special treatment as the current
# NOMAD Oasis custom schema implementation delivers them as a list of dictionaries instead
# of a directly flattenable list of key, value pairs

APM_USER_TO_NEXUS = {
    "prefix_trg": "/ENTRY[entry*]/USER[user*]",
    "map_to_str": [
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
    "use": [
        ("IDENTIFIER[identifier]/is_persistent", False),
        ("IDENTIFIER[identifier]/service", "orcid"),
    ],
    "map_to_str": [
        ("IDENTIFIER[identifier]/identifier", "orcid"),
    ],
}
