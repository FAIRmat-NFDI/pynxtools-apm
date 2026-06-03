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

import io
import logging
import os
import shutil
import sys

import pandas as pd
import yaml
from pycountry import countries

from pynxtools_apm import get_pynxtools_apm_version
from pynxtools_apm.examples.get_file_from_archive_formats import (
    get_file_from_rar,
    get_file_from_sevenzip,
    get_file_from_tar,
    get_file_from_zip,
)


def get_project_id(project_name: str) -> str:
    """Convert integer project_name ids like 1, 2, 3, ..., to three-digit format with prefix D for dataset or A for article."""
    if 1 <= len(project_name) <= 3:
        return f"{'0' * (3 - len(project_name))}{project_name}"
    return ""


def snake_case_to_camel_case(snake_case: str) -> str:
    camel_case = ""
    for token in snake_case.split("_"):
        camel_case += token.capitalize()
    return camel_case


def export_to_yaml(fpath: str, lookup_dict: dict):
    """Write content of lookup_dict to yaml file."""
    with open(fpath, "w") as fp:
        yaml.dump(lookup_dict, fp, default_flow_style=False, width=float("inf"))


def export_to_text(fpath: str, the_set: set[str]):
    """Write sorted list of all entries of the_set."""
    with open(fpath, "w") as fp:
        for item in sorted(the_set):
            fp.write(f"{item}\n")


def is_valid_alpha3(code: str) -> bool:
    try:
        return countries.get(alpha_3=code.upper()) is not None
    except KeyError:
        return False


APT_MIME_TYPES = [
    # common file formats for acquisition, reconstruction, and ranging
    ".apt",  # Cameca/AP Suite APT file format currently most used
    ".pos",  # Cameca/IVAS position and mass-to-charge minimal result of reconstruction and mass-to-charge calibration
    ".epos",  # Cameca/IVAS extended POS file, additional data classically designed to assist open-source software development of data analysis algorithms
    ".ato",  # Rouen, GPM
    ".csv",  # sometimes used serialization of reconstructions
    # ranging definitions
    ".env",  # Rouen, GPM
    ".rrng",  # classical Miller-style ranging definitions
    ".rng",  # classical Miller-style ranging definitions
    ".fig.txt",  # serialized ranging definitions from Erlangen Matlab Atom Probe Toolbox fig file
    # mixed mode, open-source, exotic stuff, and legacy
    ".h5",  # Erlangen OXCART raw, ranging, and reconstruction, pyccapt
    ".hdf",
    ".hdf5",  # Cameca HDF5 from Materials Data Facility
    ".analysis",  # XML-based Imago legacy IVAS state file
    ".analysisset",  # eventually modern? XML-based Cameca/IVAS state file
    ".nxs",  # NeXus/HDF5
    ".raw",  # Stuttgart TAP-style instruments
    "_trimmed.txt",  # Stuttgart APyT complete mass spectrum analysis results file
    "_xyz.txt",  # Stuttgart APyT reconstruction analysis results file
    "db.yaml",  # Stuttgart APyT database file
    ".ops",  # legacy 3DAP acquisition, Oxford Position-Sensitive Atom Probe (PoSAP)
    "_mass_spectrum.txt",  # Tarda meteorite can_ontario_wilson custom text format, there is also a APT_specifications.txt file following Blum's recommendations
]
CAMECA_ROOT_MIME_TYPES = [
    ".str",  # raw files, acquisition, unprocessed hits
    ".rraw",  # raw files, acquisition, unprocessed hits
    ".rhit",  # classical, IVAS results and parameter of hit finding and analysis steps up to reconstruction and ranging
    ".hits",  # newer, AP Suite results and parameter of hit finding and analysis steps up to reconstruction and ranging
    ".root",  # parameterization of reconstruction and ranging
]

CSV_HEADER_FOR_HASH_FILE = "file_path:archive_path;byte_size;unix_mtime;sha256sum"


def load_file_to_hash(hash_values_in_csv_file_path: str) -> dict[str, str]:
    """Create a dictionary for looking up a hash value to an entry in a cell in a project configuration file."""
    with open(hash_values_in_csv_file_path) as fp:
        start = next(
            idx for idx, line in enumerate(fp) if CSV_HEADER_FOR_HASH_FILE in line
        )

    df_hash = pd.read_csv(hash_values_in_csv_file_path, sep=";", skiprows=start)
    df_hash.columns = ["path", "size", "mtime", "sha256"]

    # build dictionary of hashes to replace original file names with short and clean unique ones
    file_to_hash: dict[str, str] = {}
    for line in df_hash.itertuples(index=True):
        for mime_type_list in [APT_MIME_TYPES, CAMECA_ROOT_MIME_TYPES]:
            if line.path.lower().endswith(tuple(mime_type_list)):  # type: ignore
                file_to_hash[line.path] = line.sha256  # type: ignore
    return file_to_hash


# DEFAULT_LOGGER_NAME = "convert_legacy_data"
# logger = logging.getLogger(DEFAULT_LOGGER_NAME)
# line_formatting = "%(levelname)s %(asctime)s %(message)s"
# time_formatting = "%Y-%m-%dT%H:%M:%S.%z"  # .%f%z"
# formatter = logging.Formatter(line_formatting, time_formatting)
# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)


def prepare_parsing(
    project_name: str,
    config_file_path: str,
    hash_file_path: str,
    src_directory: str,
    trg_directory: str,
    report: bool,
    write: bool,
    logger_file_path_suffix: str,
) -> dict[str, dict[str, int]]:
    """
    Load EBSD files from a configuration file, identify MTex-processable files,
    and decompress these to a target directory.

    Parameters
    ----------
    project_name : str
        Project name, e.g. deu_duesseldorf_kuehbach
    config_file_path : str
        Configuration file (ODS spreadsheet) that lists all files of project with alias project_id.
    hash_file_path : str
        CSV file that lists all files of project and their checksum
    src_directory : str
        Directory prefix where to find archive or files that should be processed.
    trg_directory : str
        Directory where processable files will be decompressed.
    report : bool
        If True, will write a csv file to trg_directory named {project_id}.decompressed.log
    write : bool
        If True, will decompress files to disk.

    Returns
    -------
    dict[str, Any]
        Dictionary containing metadata about the loaded files, including:
        - which files are processable
        - any errors encountered
    """

    if report:
        log_buffer = io.StringIO()
        log_path = f"{trg_directory}{os.sep}{project_name}.decompressed.{logger_file_path_suffix}.csv"
        logger = logging.getLogger(project_name)
        logger.setLevel(logging.DEBUG)
        log_handler = logging.StreamHandler(log_buffer)
        # log_handler = logging.FileHandler(log_path, mode="w")
        line_formatting = "%(levelname)s;%(asctime)s;%(message)s"
        time_formatting = "%Y-%m-%dT%H:%M:%S.%z"
        formatter = logging.Formatter(line_formatting, time_formatting)
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)

        logger.info(f"python_version: {sys.version.replace(' ', '_')}")
        logger.info(f"working_directory: {os.getcwd()}")
        logger.info(f"pynxtools_em version: {get_pynxtools_apm_version()}")
        # logger.info(f"target_directory: {trg_directory}")
        # logger.info(f"hash_file: {hash_file_path}")
        # logger.info(f"config_file: {config_file_path}")

    status: dict[str, dict[str, int]] = {}

    with open(hash_file_path) as fp:
        start = next(
            idx for idx, line in enumerate(fp) if CSV_HEADER_FOR_HASH_FILE in line
        )

    df_hash = pd.read_csv(hash_file_path, sep=";", skiprows=start)
    df_hash.columns = ["path", "size", "mtime", "sha256"]

    # build dictionary of hashes to replace original file names with short and clean unique ones
    path_to_hash: dict[str, str] = {}
    path_to_size: dict[str, int] = {}
    for line in df_hash.itertuples(index=True):
        # no ignores at this stage
        # inspecting only the file name ending is not a guarantee that the file is of
        # the expected format, checking for these details is the duty of the pynx plugin
        path_to_hash[line.path] = line.sha256  # type: ignore
        # no duplicates possible inside an individual (sub)directory,
        # irrespective if that content is compressed or not cuz for each project
        # line.path encodes file paths
        path_to_size[line.path] = line.size
    del df_hash

    # no ignoring of duplicates for NOMAD as config_file_path contains already the
    # selection the scientist wish to process

    # generate a list of files to finally consider, compose target filenames with hashes
    decompressed: list[tuple[str, str]] = []  # src file as key, trg file name as value

    spread_sheet_of_project = pd.read_excel(
        config_file_path,
        sheet_name=project_name,
        engine="odf",
        dtype=str,
    ).fillna("")

    for row_idx in range(0, spread_sheet_of_project.shape[0]):
        for col_idx in range(0, 6):
            # TODO !!  df.shape[1]), for deu_stuttgart_eich_tap processed further columns
            # if their CSV_HEADER_FOR_HASH_FILE not startswith("ignore")
            path = spread_sheet_of_project.iat[row_idx, col_idx]
            # if path == "":
            #     continue

            # spread_sheet_for_project/config file is written by the scientists
            # documenting which raw data, reconstruction, and ranging if present to combine,
            # note that with NeXus/HDF5 NXapm we bundle together artifacts that were so far
            # left decoupled during the atom probe data processing workflow
            # path in the spreadsheet can be absolute or relative and can also
            # include two parts e.g. archive.zip:recon.pos indicating that the
            # legacy data are stored inside an archive.zip file inside which there
            # is the recon.pos file, sub-directories past the : archive-dirtree marker
            # are possible
            if path in path_to_hash and path in path_to_size:
                src = f"{src_directory}{os.sep}{project_name}{os.sep}"
                trg = f"{trg_directory}{os.sep}"
                main = f"{src}{path}"
                # if main not in decompressed:
                hash = path_to_hash[path]
                size = path_to_size[path]
                typ = path.rsplit(".", 1)[1].lower()
                decompressed.append(
                    (main, f"{trg}{project_name}.{row_idx}.{col_idx}.{hash}.{typ}")
                )
                if typ not in status:
                    status[typ] = {"n": 1, "bytes": size}
                else:
                    status[typ]["n"] += 1
                    status[typ]["bytes"] += size

    if write:
        archive_handlers = {
            get_file_from_zip: (".zip", ".eln"),
            get_file_from_tar: (".tar", ".tar.gz", ".tar.bz2", ".tar.xz"),
            get_file_from_rar: (".rar"),
            get_file_from_sevenzip: (".7z"),
        }

        for src, trg in decompressed:
            if src.count(":") == 1:
                archive_file_path, file_path = src.split(":")
                trg_directory, trg_file_name = trg.rsplit(os.sep, 1)

                for handler, extensions in archive_handlers.items():
                    if archive_file_path.lower().endswith(extensions):  # type: ignore
                        success = handler(
                            archive_file_path, file_path, trg_directory, trg_file_name
                        )
                        if report:
                            if success:
                                logger.info(f"{src};;{trg}")
                            else:
                                logger.error(f"{src};;{trg}")
                        break  # stop checking other handlers once matched
            else:
                try:
                    return_value: str = shutil.copy2(src, trg)
                    if report:
                        if return_value == trg:
                            logger.info(f"{src};;{trg}")
                        else:
                            logger.error(f"{src};;{trg}")
                except OSError:
                    logger.error(f"{src};;{trg}")
    else:
        if report:
            for src, trg in decompressed:
                logger.info(f"{src};;{trg}")

    if report:
        # pro: allows writing log files only when these have content
        # con: requires main memory for caching
        if len(decompressed) > 0:
            with open(log_path, "w") as fp:
                fp.write(log_buffer.getvalue())

    return status
