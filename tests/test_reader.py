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

import os
import shutil
from typing import Literal

import pytest
import yaml
from pynxtools.dataconverter.convert import convert, get_reader
from pynxtools.dataconverter.helpers import get_nxdl_root_and_path

from pynxtools_apm.examples.get_file_from_archive_formats import get_file_from_zip

# from pynxtools.testing.nexus_conversion import ReaderTest
from pynxtools_apm.parsers.hfive_base import (
    NXAPM_VOLATILE_NAMED_HDF_PATHS,
    NXAPM_VOLATILE_SUFFIX_HDF_PATHS,
    HdfFiveBaseParser,
)
from pynxtools_apm.utils.use_requests import download_requests

READER_NAME = "apm"
READER_CLASS = get_reader(READER_NAME)
NXDLS = ["NXapm"]

working_directory = os.path.dirname(__file__)

with open(
    os.path.join(*[working_directory, "data", "datasets.yaml"]),
    encoding="utf-8",
) as fp:
    datasets = yaml.safe_load(fp)

# test_cases = [
#     ("default", "NOMAD simple APM example"),
# ]

test_params = []

if isinstance(datasets, dict):
    for mime_type, examples in datasets.items():
        if not isinstance(examples, dict):
            continue
        for example, metadata in examples.items():
            # logger.debug(f"{mime_type}, {example}")
            # only include examples with a license
            if not all(concept in metadata for concept in ("name", "spdx")):
                continue

            if os.path.isfile(os.path.join(*[working_directory, metadata["name"]])):
                test_params += [
                    pytest.param(
                        "NXapm",
                        f"{metadata['name']}",  # {mime_type}/{example}/
                        id=f"{metadata['name']}",
                    )
                ]
                # never download data twice
                continue

            # does not exist needs download or copying over
            if "url" in metadata:
                if metadata["url"].count(":") == 2:  # possibly compressed
                    archive_link, file_path = metadata["url"].rsplit(":", 1)
                    # logger.debug(
                    #     f"remote file, compressed >>>> {archive_link}, {file_path}, {file_path.rsplit('/', 1)[-1]} >>>> {metadata['name']}"
                    # )
                    archive_file_name = download_requests(archive_link)
                    if archive_file_name.endswith(".zip"):
                        decompressed = get_file_from_zip(
                            archive_file_name,
                            file_path,
                            working_directory,
                            metadata["name"],
                        )
                        os.remove(archive_file_name)
                        if os.path.isfile(decompressed):
                            test_params += [
                                pytest.param(
                                    "NXapm",
                                    f"{decompressed}",  # {mime_type}/{example}/
                                    id=f"{decompressed}",
                                )
                            ]
                else:
                    # logger.debug(
                    #     f"remote file, not compressed >>>> {metadata['url']} >>>> {metadata['name']}"
                    # )
                    data_file_name = download_requests(metadata["url"])
                    os.rename(
                        data_file_name,
                        os.path.join(*[working_directory, metadata["name"]]),
                    )
                    if os.path.isfile(
                        os.path.join(*[working_directory, metadata["name"]])
                    ):
                        test_params += [
                            pytest.param(
                                "NXapm",
                                f"{metadata['name']}",  # {mime_type}/{example}/
                                id=f"{metadata['name']}",
                            )
                        ]
            else:
                if os.path.isfile(
                    os.path.join(
                        *[
                            working_directory,
                            "data",
                            mime_type,
                            example,
                            metadata["name"],
                        ]
                    )
                ):
                    shutil.copy(
                        os.path.join(
                            *[
                                working_directory,
                                "data",
                                mime_type,
                                example,
                                metadata["name"],
                            ]
                        ),
                        os.path.join(*[working_directory, metadata["name"]]),
                    )
                    # logger.debug(
                    #     f"local file, not compressed >>>> data/{mime_type}/{example}/{metadata['name']}"
                    # )
                    if os.path.isfile(
                        os.path.join(*[working_directory, metadata["name"]])
                    ):
                        test_params += [
                            pytest.param(
                                "NXapm",
                                f"{metadata['name']}",  # {mime_type}/{example}/
                                id=f"{metadata['name']}",
                            )
                        ]


# for test_case in test_cases:
#     # ToDo: make tests for all supported application definitions possible
#    for nxdl in NXDLS:
#         test_params += [pytest.param(nxdl, test_case[0], id=f"{test_case[1]}")]


def convert_using_example_data(input_path, output_path, caplog, **kwargs) -> None:
    """Run the converter during the test."""
    # see pynxtools/testing/nexus_conversion/ReaderTest

    nxdl = "NXapm"
    reader_name = "apm"
    caplog_level: Literal["ERROR", "WARNING"] = "WARNING"

    reader = get_reader(reader_name)
    assert hasattr(reader, "supported_nxdls"), (
        f"Reader{reader} must have supported_nxdls attribute"
    )
    assert nxdl in reader.supported_nxdls, f"Reader does not support {nxdl} NXDL."
    assert callable(reader.read), f"Reader{reader} must have read method"

    nxdl_root, nxdl_file = get_nxdl_root_and_path(nxdl)
    assert os.path.exists(nxdl_file), f"NXDL file {nxdl_file} not found"

    # Clear the log of `convert`
    caplog.clear()

    with caplog.at_level(caplog_level):
        _ = convert(
            input_file=tuple([input_path]),
            reader=reader_name,
            nxdl=nxdl,
            skip_verify=True,
            ignore_undocumented=True,
            output=f"{output_path}",
            **kwargs,
        )


@pytest.mark.parametrize(
    "nxdl, sub_reader_data_dir",
    test_params,
)
# explores an alternative testing strategy which checks for binary
# reproducibility at the individual HDF5 node using per node checksums
def test_nexus_conversion(nxdl, sub_reader_data_dir, tmp_path, caplog):
    """
    Test APM reader

    Parameters
    ----------
    nxdl : str
        Name of the NXDL application definition that is to be tested by
        this reader plugin (e.g. NXsts, NXmpes, etc)..
    sub_reader_data_dir : str
        Test data directory that contains all the files required for running the data
        conversion through one of the sub-readers. All of these data dirs
        are placed within tests/data/...
    tmp_path : pathlib.PosixPath
        Pytest fixture variable, used to clean up the files generated during
        the test.
    caplog : _pytest.logging.LogCaptureFixture
        Pytest fixture variable, used to capture the log messages during the
        test.

    Returns
    -------
    None.

    """
    caplog.clear()
    # reader = READER_NAME
    # assert callable(reader.read)

    input_path = os.path.join(*[os.path.dirname(__file__), sub_reader_data_dir])
    output_path = os.path.join(*[tmp_path, f"{sub_reader_data_dir.rsplit('/', 1)[-1]}"])

    convert_using_example_data(
        input_path, os.path.join(*[tmp_path, f"{output_path}.nxs"]), caplog
    )

    hfive_parser = HdfFiveBaseParser(
        file_path=os.path.join(*[tmp_path, f"{output_path}.nxs"]),
        hashing=True,
        verbose=False,
    )
    hfive_parser.get_content()
    hfive_parser.store_hashes(
        blacklist_by_key=NXAPM_VOLATILE_NAMED_HDF_PATHS,
        blacklist_by_suffix=NXAPM_VOLATILE_SUFFIX_HDF_PATHS,
        file_path=os.path.join(*[tmp_path, f"{output_path}.nxs.sha256.test.yaml"]),
    )

    # keep a copy of the local file
    # for convenience dropped already where one would overwrite
    # here make it the reference
    # use this block to overwrite a reference from the tmp_path to the tests/reference
    # TODO IN PRODUCTION THIS BLOCK NEEDS TO BE COMMENTED OUT BEGINNING HERE
    """
    shutil.copy(
        f"{output_path}.nxs.sha256.test.yaml",
        os.path.join(
            *[
                f"{input_path.rsplit('/', 1)[0]}",
                "reference",
                f"{input_path.rsplit('/', 1)[-1]}.nxs.sha256.ref.yaml",
            ]
        ),
    )
    """
    # TODO ... ENDING HERE

    # assert against reference YAML artifact
    test_artifact_file_path = f"{output_path}.nxs.sha256.test.yaml"
    with open(test_artifact_file_path) as fp_test:
        try:
            test_artifact = yaml.safe_load(fp_test)
        except yaml.YAMLError as exc:
            print(f"Unable to load test_artifact {test_artifact_file_path} !")

    ref_artifact_file_path = os.path.join(
        *[
            f"{input_path.rsplit('/', 1)[0]}",
            "reference",
            f"{input_path.rsplit('/', 1)[-1]}.nxs.sha256.ref.yaml",
        ]
    )
    with open(ref_artifact_file_path) as fp_ref:
        try:
            reference_artifact = yaml.safe_load(fp_ref)
        except yaml.YAMLError as exc:
            print(f"Unable to load ref_artifact {ref_artifact_file_path} !")

    assert test_artifact == reference_artifact
    # test.check_reproducibility_of_nexus()

    # TODO remove if not working
