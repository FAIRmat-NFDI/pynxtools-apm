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

"""Script to batch-convert to NeXus/HDF5 using pynxtools-apm."""

# e.g. python3 pynxtools-apm/examples/oasisb/04_convert_archived_legacy_data_using_pynxtools.py .../harvest_examples/data aus_sydney_bilal .../scidat_nomad_apt
import io
import json
import logging
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import bibtexparser
import flatdict as fd
import pandas as pd
from ifes_apt_tc_data_modeling import get_ifes_apt_tc_data_modeling_version
from pynxtools.dataconverter.convert import convert
from pynxtools.dataconverter.helpers import (
    get_nxdl_root_and_path,
    get_pynxtools_version,
)

from pynxtools_apm import get_pynxtools_apm_version


class ISO8601Formatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(
            record.created,
            tz=ZoneInfo("Europe/Berlin"),
        )
        return dt.isoformat()


try:
    # pynxtools-camecaroot is not in the public domain!
    from pynxtools_camecaroot import get_pynxtools_camecaroot_version

    if get_pynxtools_camecaroot_version() != "unknown_version":
        USE_WORKING_CAMECAROOT_PLUGIN = True
    else:
        USE_WORKING_CAMECAROOT_PLUGIN = False
except (ImportError, ModuleNotFoundError):
    USE_WORKING_CAMECAROOT_PLUGIN = False

from pynxtools_apm.examples.oasisb_eln import generate_oasis_specific_yaml
from pynxtools_apm.examples.oasisb_utils import (
    APT_MIME_TYPES,
    CAMECA_ROOT_MIME_TYPES,
    CSV_HEADER_FOR_HASH_FILE,
)


def switch_root_logfile(
    file_path: str, formatter, log_level=logging.DEBUG
) -> logging.FileHandler:
    """Replace the root logger's handler with a new FileHandler."""
    root = logging.getLogger()
    root.setLevel(log_level)
    # remove and close old handlers
    for h in root.handlers[:]:
        root.removeHandler(h)
        try:
            h.close()
        except Exception:
            pass
    new_handler = logging.FileHandler(file_path, mode="a", encoding="utf-8")
    new_handler.setFormatter(formatter)
    root.addHandler(new_handler)
    return new_handler


def process_project(
    project_name: str,
    config_file: str,
    bib_file: str,
    hash_file: str,
    source_directory: str,
    target_directory: str,
    openalex_file: str = "",
    logger_file_path_suffix: str = "",
    generate_eln_file: bool = True,
    generate_nexus_file: bool = True,
    # time_zone_info: ZoneInfo = ZoneInfo("Europe/Berlin"),
) -> None:
    """Run first (if available) optional pynxtools-camecaroot followed by or only pynxtools-apm to generate a NeXus/HDF5 file for each dataset in the project named project_name.

    project_name : name of the legacy atom probe project for which this function processes all entries,
        e.g. "deu_duesseldorf_kuehbach" is a project-specific such name
    config_file : spreadsheet file (currently ods) that identifies which atom probe files (pos, rrng, ...)
        from the project should be combined into one entry in one NeXus/HDF5 file
    bib_file : bibtex bibliography file that resolves project-name-specific CitationKeys like
        D_DeuDuesseldorfKuehbach or A_DeuDuesseldorfKuehbach to populate NXcitation instances
    hash_file : csv file which stores the hash and original file name of each file from a project
    source_directory : location of atom probe files that the parser should convert
    target_directory : location where generated NeXus/HDF5 and log files should be stored
    openalex_file : (optional) project-name-specific JSON file, retrieved from OpenAlex
        to provide additional metadata context to a project, e.g. D_DeuDuesseldorfKuehbach.json
    logger_file_path_suffix : suffix to add to the name of the log file
    """

    config: dict[str, str] = {
        "python_version": f"{sys.version}",
        "working_directory": f"{os.getcwd()}",
        "project_name": project_name,
        "config_file": config_file,
        "bib_file": bib_file,
        "source_directory": source_directory,
        "target_directory": target_directory,
        "openalex_file": openalex_file,
        "pynxtools_version": f"{get_pynxtools_version()}",
        "ifes_apt_tc_data_modeling_version": f"{get_ifes_apt_tc_data_modeling_version()}",
        "pynxtools_apm_version": f"{get_pynxtools_apm_version()}",
    }
    if USE_WORKING_CAMECAROOT_PLUGIN:
        config["pynxtools_camecaroot_version"] = f"{get_pynxtools_camecaroot_version()}"
    else:
        config["pynxtools_camecaroot_version"] = "unknown_version or not available"

    master_buffer = io.StringIO()
    master_handler = logging.StreamHandler(master_buffer)
    master_handler.setFormatter(
        ISO8601Formatter(fmt="%(asctime)s;%(levelname)s;%(message)s")
    )
    master_logger = logging.getLogger(project_name)
    master_logger.setLevel(logging.DEBUG)
    master_logger.addHandler(master_handler)
    for key, value in config.items():
        master_logger.info(f"{key} {value}")

    nxdl = "NXapm"
    nxdl_root, nxdl_file = get_nxdl_root_and_path(nxdl)
    if not os.path.exists(nxdl_file):
        master_logger.error(f"Unable to load {nxdl_file}")
        return

    try:
        spread_sheet_of_project = pd.read_excel(
            config_file,
            sheet_name=f"{config['project_name']}",
            engine="odf",
            dtype=str,
        ).fillna("")
    except (FileNotFoundError, OSError):
        master_logger.error(f"Unable to load {config_file}")
        return

    try:
        with open(bib_file) as fp:
            bib = bibtexparser.load(fp).entries_dict
    except (FileNotFoundError, OSError):
        master_logger.error(f"Unable to load {bib_file}")
        return

    openalex = fd.FlatDict({}, delimiter="/")
    if openalex_file != "":
        try:
            with open(openalex_file, encoding="utf-8") as fp:
                openalex = fd.FlatDict(json.load(fp), delimiter="/")
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            master_logger.error(f"Unable to load {openalex_file}")

    try:
        with open(hash_file) as fp:
            start = next(
                idx for idx, line in enumerate(fp) if CSV_HEADER_FOR_HASH_FILE in line
            )
            df_hash = pd.read_csv(hash_file, sep=";", skiprows=start)
            df_hash.columns = ["path", "size", "mtime", "sha256"]

            # get the dictionary of hashes where to identifyto replace original file names with short and clean unique ones
            file_to_hash: dict[str, str] = {}
            for line in df_hash.itertuples(index=True):
                for mime_type_list in [APT_MIME_TYPES, CAMECA_ROOT_MIME_TYPES]:
                    if line.path.lower().endswith(tuple(mime_type_list)):  # type: ignore
                        file_to_hash[line.path] = line.sha256  # type: ignore
    except (FileNotFoundError, OSError):
        master_logger.error(f"Unable to load {hash_file}")
        return

    # one NeXus file per row, compositing from at least one atom probe file and eln.yaml
    for row_idx in range(spread_sheet_of_project.shape[0]):
        has_input: bool = False
        for col_idx in range(1, 6):  # resolves to
            # 0, str_rraw, ignore
            # 1, rhit_hits
            # 2, root
            # 3, pos_epos_apt_ato_csv
            # 4, rng_rrng_fig_env
            # 5, hdf_xml_nxs_raw_ops
            # >= 6, comment columns, ignore
            value = spread_sheet_of_project.iat[row_idx, col_idx]  # type: ignore
            if value == "":
                continue
            has_input = True
            break
        if not has_input:
            master_logger.warning(f"No content to parse for row {row_idx}")
            continue

        # collect all external metadata that is not stored in any atom probe specific file
        eln_file_path = generate_oasis_specific_yaml(
            f"{project_name}.{row_idx}.oasis.specific.yaml",  # eln_data.yaml
            row_idx,  # type: ignore
            target_directory,
            bib,  # type: ignore
            openalex,
        )
        if os.path.isfile(eln_file_path):
            master_logger.debug(eln_file_path)
        else:
            continue

        # define the name of the NeXus file
        output_file_path = f"{project_name}.{row_idx}.nxs"

        root_parser_used: bool = False
        if USE_WORKING_CAMECAROOT_PLUGIN:
            # if True, we run pynxtools-camecaroot followed by pynxtools-apm
            # if False, we just run pynxtools-apm
            pynx_root_input_files: list[str] = []
            for col_idx in range(1, 6):  # ignore str_rraw
                value = spread_sheet_of_project.iat[row_idx, col_idx]  # type: ignore
                if value != "":
                    pynx_root_input_files.append(
                        f"{source_directory}{os.sep}"
                        f"{project_name}.{row_idx}.{col_idx}."
                        f"{file_to_hash[value]}."  # type: ignore
                        f"{value.rsplit('.', 1)[1].lower()}"  # type: ignore
                    )

            if len(pynx_root_input_files) > 0:
                # master_logger.debug(f"{tuple(pynx_root_input_files)}")
                # master_logger.debug(f"pynxtools-cameca, {output_file_path}")

                _ = convert(
                    input_file=tuple(pynx_root_input_files),
                    reader="camecaroot",
                    nxdl=nxdl,
                    append=False,
                    skip_verify=True,
                    ignore_undocumented=True,
                    output=output_file_path,
                )
                root_parser_used = True

        pynx_open_input_files: list[str] = []
        for col_idx in range(3, 6):
            # col_idx int will be 0, str_rraw, 1, rhit_hits, 2, root,
            # 3, pos_epos_apt_ato_csv, 4, rng_rrng_fig_env, 5, hdf_xml_nxs_raw_ops
            value = spread_sheet_of_project.iat[row_idx, col_idx]  # type: ignore
            if value != "":
                if value in file_to_hash:
                    pynx_open_input_files.append(
                        f"{source_directory}{os.sep}"
                        f"{project_name}.{row_idx}.{col_idx}."
                        f"{file_to_hash[value]}."  # type: ignore
                        f"{value.rsplit('.', 1)[-1].lower()}"  # type: ignore
                    )
                else:
                    master_logger.error(f"Unable to find hash for {row_idx}.{col_idx}")
                    break

        pynx_open_input_files.append(eln_file_path)

        # master_logger.debug(f"{tuple(pynx_open_input_files)}")
        # master_logger.debug(f"pynxtools-apm, {output_file_path}")

        # in every case ELN content has been added by pynxtools-apm
        if root_parser_used:
            _ = convert(
                input_file=tuple(pynx_open_input_files),
                reader="apm",
                nxdl=nxdl,
                append=True,
                skip_verify=True,  # obsolete as append switches validation off anyway
                ignore_undocumented=True,
                output=output_file_path,
            )
        else:
            _ = convert(
                input_file=tuple(pynx_open_input_files),
                reader="apm",
                nxdl=nxdl,
                append=False,
                skip_verify=True,
                ignore_undocumented=True,
                output=output_file_path,
            )

    with open(
        f"{target_directory}{os.sep}{project_name}.{logger_file_path_suffix}.csv", "w"
    ) as fp:
        fp.write(master_buffer.getvalue())

    print(f"Batch queue for project {project_name} processed successfully")
