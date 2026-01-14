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
"""Parent class for all tech partner-specific HDF5 parsers for mapping on NXem."""

# taken from pynxtools-em, eventually should be made a part of pynxtools like hfive_utils

import h5py
import numpy as np
import yaml

from pynxtools_apm.utils.custom_logging import logger
from pynxtools_apm.utils.get_checksum import get_sha256_of_bytes_object
from pynxtools_apm.utils.hfive_concepts import Concept

# the base parser implements the processing of standardized orientation maps via
# the pyxem software package from the electron microscopy community
# specifically so-called NeXus default plots are generated to add RDMS-relevant
# information to the NeXus file which supports scientists with judging the potential
# value of the dataset in the context of them using research data management systems (RDMS)
# in effect this parser is the partner of the MTex parser for all those file formats
# which are HDF5 based and which (at the time of working on this example Q3/Q4 2023)
# where not supported my MTex
# with offering this parser we also would like to embrace and acknowledge the efforts
# of other electron microscopists (like the pyxem team, hyperspy etc.) and their work
# towards software tools which are complementary to the MTex texture toolbox
# one could have also implemented the HDF5 parsing inside MTex but we leave this as a
# task for the community and instead focus here on showing a more diverse example
# towards more interoperability between the different tools in the community

# object timestamps are low-level features of HDF5 that if activated
# would still render HDF5 files whose binary content differs even though each
# entry and payload in the content tree is the same binary content
# however, these internal library administrative timestamps have been
# are in newer versions of hdf5 deactivated by default see here:
# https://github.com/h5py/h5py/issues/1953
# https://forum.hdfgroup.org/t/object-timestamps-useful-or-not/8901/7
# h5diff does not allow such a lean and customizable blacklist of nodes
# to the best of my knowledge hence comparing two versions of HDF5 files
# with h5diff is useful but if done in unit testing typically generate
# two long text outputs via stdout that are maybe more difficult to


def only_finite_payload(obj, payload) -> str:
    """Analyze if dat contains malformed values (NaN, Inf, etc.)"""
    if obj[...].dtype.kind in "iufc":
        if isinstance(payload, np.ndarray) and payload.size > 1:
            if np.all(np.isfinite(payload)):
                return "all_finite"
            else:
                return "not_all_finite"
        else:
            if payload.size == 1:
                if np.all(np.isfinite(payload)):
                    return "all_finite"
                else:
                    return "not_all_finite"
            else:
                return "issue_with_scalars"
    return "non_iufc"


NXAPM_VOLATILE_NAMED_HDF_PATHS = (
    "/@HDF5_Version",
    "/@NeXus_release",
    "/@file_time",
    "/@file_update_time",
    "entry1/definition/@version",
    "entry1/profiling/program1/program/@version",
    "entry1/profiling/template_filling_elapsed_time",
    # "entry1/profiling/template_filling_elapsed_time/@units"
)
NXAPM_VOLATILE_SUFFIX_HDF_PATHS = (
    "@axes",  # as these are stored as by default as byte objects variable length string array
    "file_name",  # if these include the full path the absolute path may differ between
    # test and production data
)


class HdfFiveBaseParser:
    def __init__(
        self,
        file_path: str = "",
        hashing: bool = True,
        malformed: bool = False,
        verbose: bool = False,
    ):
        # tech_partner the company which designed this format
        # schema_name the specific name of the family of schemas supported by this reader
        # schema_version the specific version(s) supported by this reader
        # writer_name the specific name of the tech_partner's (typically proprietary) software
        #   with which an instance of a file formatted according to schema_name and schema_version
        #   was written e.g. Oxford Instruments AZTec software in some version may generate
        #   an instance of a file whose schema belongs to the H5OINA family of HDF5 container formats
        #   specifically using version 5
        if file_path:
            self.file_path = file_path
        self.prfx: str = ""
        self.tmp: dict = {}
        self.source: str = ""
        # collection of instance path
        self.groups: dict = {}
        self.datasets: dict = {}
        self.attributes: dict = {}
        self.instances: dict = {}
        # collection of template
        self.template_groups: list = []
        self.template_datasets: list = []
        self.template_attributes: list = []
        self.templates: dict = {}
        self.h5r = None
        self.is_hdf = True  # TODO::check if HDF5 file using magic cookie
        self.hashing = hashing
        self.malformed = malformed
        self.verbose = verbose

    def init_cache(self, cache_key: str) -> str:
        """Init a new cache for normalized EBSD data if not existent."""
        # purpose of the cache is to hold normalized information
        if cache_key not in self.tmp:
            self.tmp[
                cache_key
            ] = {}  # reset to {} upon incomplete collection of the cache
            return cache_key
        else:
            raise ValueError(
                f"Existent named cache {cache_key} must not be overwritten !"
            )

    def clear_cache(self, cache_key: str):
        if cache_key in self.tmp:
            self.tmp.pop(cache_key)

    def open(self):
        if self.h5r is None:
            self.h5r = h5py.File(self.file_path, "r")

    def close(self):
        if self.h5r is not None:
            self.h5r.close()
            self.h5r = None

    def __call__(self, node_name, h5obj):
        # only h5py datasets have dtype attribute, so we can search on this
        if isinstance(h5obj, h5py.Dataset):
            if node_name not in self.datasets:
                if self.verbose:
                    print(node_name)
                if hasattr(h5obj, "dtype"):
                    if hasattr(h5obj.dtype, "fields") and hasattr(h5obj.dtype, "names"):
                        if h5obj.dtype.names is not None:
                            self.datasets[node_name] = (
                                "IS_COMPOUND_DATASET",
                                type(h5obj),
                                np.shape(h5obj),
                                h5obj[0],
                                f"{h5obj.dtype}__{get_sha256_of_bytes_object(h5obj[()])}"
                                if self.hashing
                                else "",
                                f"{only_finite_payload(h5obj, h5obj[()])}"
                                if self.malformed
                                else "",
                            )
                            self.instances[node_name] = Concept(
                                node_name,
                                None,
                                None,
                                type(h5obj),
                                np.shape(h5obj),
                                None,
                                hdf_type="compound_dataset",
                            )
                            n_dims = len(np.shape(h5obj))
                            if n_dims == 1:
                                for name in h5obj.dtype.names:
                                    self.datasets[f"{node_name}/#{name}"] = (
                                        "IS_FIELD_IN_COMPOUND_DATASET",
                                        h5obj.fields(name)[()].dtype,
                                        np.shape(h5obj.fields(name)[()]),
                                        h5obj.fields(name)[0],
                                        f"{h5obj.fields(name)[()].dtype}__{get_sha256_of_bytes_object(h5obj.fields(name)[()])}"
                                        if self.hashing
                                        else "",
                                        f"{only_finite_payload(h5obj, h5obj.fields(name)[()])}"
                                        if self.malformed
                                        else "",
                                    )
                                    self.instances[f"{node_name}/{name}"] = Concept(
                                        node_name,
                                        None,
                                        None,
                                        h5obj.fields(name)[()].dtype,
                                        np.shape(h5obj.fields(name)[()]),
                                        None,
                                        hdf_type="compound_dataset_entry",
                                    )
                            else:
                                raise ValueError(
                                    f"Unknown formatting of an h5py.Dataset, inspect {node_name} !"
                                )
                        else:  # h5obj.dtype.names is a tuple of struct variable names
                            n_dims = len(np.shape(h5obj))
                            if n_dims == 0:
                                self.datasets[node_name] = (
                                    "IS_REGULAR_DATASET",
                                    type(h5obj),
                                    np.shape(h5obj),
                                    h5obj[()],
                                    f"{h5obj.ndim}__{h5obj.shape}__{h5obj.dtype.name}__{get_sha256_of_bytes_object(h5obj[()])}"
                                    if self.hashing
                                    else "",
                                    f"{only_finite_payload(h5obj, h5obj[()])}"
                                    if self.malformed
                                    else "",
                                )
                                self.instances[node_name] = Concept(
                                    node_name,
                                    None,
                                    None,
                                    type(h5obj),
                                    np.shape(h5obj),
                                    None,
                                    hdf_type="regular_dataset",
                                )
                            elif n_dims == 1:
                                if 0 not in np.shape(h5obj):
                                    self.datasets[node_name] = (
                                        "IS_REGULAR_DATASET",
                                        type(h5obj),
                                        np.shape(h5obj),
                                        h5obj[0],
                                        f"{h5obj.ndim}__{h5obj.shape}__{h5obj.dtype.name}__{get_sha256_of_bytes_object(h5obj[()])}"
                                        if self.hashing
                                        else "",
                                        f"{only_finite_payload(h5obj, h5obj[()])}"
                                        if self.malformed
                                        else "",
                                    )
                                    self.instances[node_name] = Concept(
                                        node_name,
                                        None,
                                        None,
                                        type(h5obj),
                                        np.shape(h5obj),
                                        None,
                                        hdf_type="regular_dataset",
                                    )
                                else:
                                    self.datasets[node_name] = (
                                        "IS_REGULAR_DATASET",
                                        type(h5obj),
                                        np.shape(h5obj),
                                        h5obj[()],
                                        f"{h5obj.ndim}__{h5obj.shape}__{h5obj.dtype.name}__{get_sha256_of_bytes_object(h5obj[()])}"
                                        if self.hashing
                                        else "",
                                        f"{only_finite_payload(h5obj, h5obj[()])}"
                                        if self.malformed
                                        else "",
                                    )
                                    self.instances[node_name] = Concept(
                                        node_name,
                                        None,
                                        None,
                                        type(h5obj),
                                        np.shape(h5obj),
                                        None,
                                        hdf_type="regular_dataset",
                                    )
                            elif n_dims == 2:
                                self.datasets[node_name] = (
                                    "IS_REGULAR_DATASET",
                                    type(h5obj),
                                    np.shape(h5obj),
                                    h5obj[0, 0],
                                    f"{h5obj.ndim}__{h5obj.shape}__{h5obj.dtype.name}__{get_sha256_of_bytes_object(h5obj[()])}"
                                    if self.hashing
                                    else "",
                                    f"{only_finite_payload(h5obj, h5obj[()])}"
                                    if self.malformed
                                    else "",
                                )
                                self.instances[node_name] = Concept(
                                    node_name,
                                    None,
                                    None,
                                    type(h5obj),
                                    np.shape(h5obj),
                                    None,
                                    hdf_type="regular_dataset",
                                )
                            elif n_dims == 3:
                                self.datasets[node_name] = (
                                    "IS_REGULAR_DATASET",
                                    type(h5obj),
                                    np.shape(h5obj),
                                    h5obj[0, 0, 0],
                                    f"{h5obj.ndim}__{h5obj.shape}__{h5obj.dtype.name}__{get_sha256_of_bytes_object(h5obj[()])}"
                                    if self.hashing
                                    else "",
                                    f"{only_finite_payload(h5obj, h5obj[()])}"
                                    if self.malformed
                                    else "",
                                )
                                self.instances[node_name] = Concept(
                                    node_name,
                                    None,
                                    None,
                                    type(h5obj),
                                    np.shape(h5obj),
                                    None,
                                    hdf_type="regular_dataset",
                                )
                            else:
                                self.datasets[node_name] = (
                                    "IS_REGULAR_DATASET",
                                    type(h5obj),
                                    np.shape(h5obj),
                                    None,
                                    f"{h5obj.ndim}__{h5obj.shape}__{h5obj.dtype.name}__{get_sha256_of_bytes_object(h5obj[()])}"
                                    if self.hashing
                                    else "",
                                    f"{only_finite_payload(h5obj, h5obj[()])}"
                                    if self.malformed
                                    else "",
                                )
                                self.instances[node_name] = Concept(
                                    node_name,
                                    None,
                                    None,
                                    type(h5obj),
                                    np.shape(h5obj),
                                    None,
                                    hdf_type="regular_dataset",
                                )
                    else:
                        raise ValueError(
                            f"hasattr(h5obj.dtype, 'fields') and hasattr("
                            f"h5obj.dtype, 'names') failed, inspect {node_name} !"
                        )
                else:
                    raise ValueError(
                        f"hasattr(h5obj, dtype) failed, inspect {node_name} !"
                    )
        else:
            if node_name not in self.groups:
                self.groups[node_name] = "IS_GROUP"
                self.instances[node_name] = Concept(
                    node_name,
                    None,
                    None,
                    type(h5obj),
                    np.shape(h5obj),
                    None,
                    hdf_type="group",
                )
        # if hasattr(h5obj, 'dtype') and not node_name in self.metadata:
        #     self.metadata[node_name] = ["dataset"]

    def get_attribute_data_structure(self, prefix, src_dct):
        # trg_dct is self.attributes
        for key, val in src_dct.items():
            if f"{prefix}/@{key}" not in self.attributes:
                if isinstance(val, str):
                    self.attributes[f"{prefix}/@{key}"] = (
                        "IS_ATTRIBUTE",
                        type(val),
                        np.shape(val),
                        str,
                        val,
                        f"str__{get_sha256_of_bytes_object(val.encode('utf-8'))}"
                        if self.hashing
                        else "",
                    )
                    self.instances[f"{prefix}/{key}"] = Concept(
                        f"{prefix}/@{key}",
                        None,
                        None,
                        type(val),
                        np.shape(val),
                        None,
                        hdf_type="attribute",
                    )
                elif hasattr(val, "dtype"):
                    self.attributes[f"{prefix}/@{key}"] = (
                        "IS_ATTRIBUTE",
                        type(val),
                        np.shape(val),
                        val.dtype,
                        val,
                        f"{val.ndim}__{val.shape}__{val.dtype.name}__{get_sha256_of_bytes_object(bytes(val))}"
                        if self.hashing
                        else "",
                    )
                    self.instances[f"{prefix}/{key}"] = Concept(
                        f"{prefix}/@{key}",
                        None,
                        None,
                        type(val),
                        np.shape(val),
                        None,
                        hdf_type="attribute",
                    )
                else:
                    raise ValueError(
                        f"Unknown formatting of an attribute, inspect {prefix}/@{key} !"
                    )

    def get_content(self):
        """Walk recursively through the file to get content."""
        # if self.h5r is not None:  # if self.file_path is not None:
        with h5py.File(self.file_path, "r") as self.h5r:
            # parse the root header of the file, which typically has time data
            self.get_attribute_data_structure("", dict(self.h5r["/"].attrs))
            # automatic timestamping of objects in the HDF5 tree has already
            # been deactivated since several years

            # first step visit all groups and datasets recursively
            # get their full path within the HDF5 file
            self.h5r.visititems(self)
            # second step visit all these and get their attributes
            for h5path, h5ifo in self.groups.items():
                self.get_attribute_data_structure(h5path, dict(self.h5r[h5path].attrs))
            for h5path, h5ifo in self.datasets.items():
                if (
                    h5path.count("#") == 0
                ):  # skip resolved fields in compound data types
                    self.get_attribute_data_structure(
                        h5path, dict(self.h5r[h5path].attrs)
                    )

    def store_hashes(self, blacklist_by_key: list, blacklist_by_suffix: list, **kwargs):
        """Generate yaml file with sorted list of HDF5 grp, dst, and attrs

        including their datatype and SHA256 checksum computed from the each nodes data.
        This yaml file can be useful for unit tests of different NeXus files
        when differences in timestamps are expected but should not trigger
        the test to fail. The blacklist allows to exclude those HDF5 paths
        that should not be included in the yaml file."""
        hashes: dict[str, str] = {}
        for key, ifo in self.groups.items():
            if key not in blacklist_by_key and not key.endswith(blacklist_by_suffix):
                hashes[key] = "grp"
        for key, ifo in self.datasets.items():
            if key not in blacklist_by_key and not key.endswith(blacklist_by_suffix):
                hashes[key] = f"dst__{ifo[-2]}"
        for key, ifo in self.attributes.items():
            if key not in blacklist_by_key and not key.endswith(blacklist_by_suffix):
                hashes[key] = f"att__{ifo[-1]}"
        with open(
            kwargs.get(
                "file_path",
                f"""{self.file_path}.sha256{kwargs.get("suffix", "")}.yaml""",
            ),
            "w",
        ) as fp:
            yaml.dump(hashes, fp, default_flow_style=False, sort_keys=True)

    def store_malformed(self, **kwargs):
        """Generate yaml file with sorted list of HDF5 dst

        reporting if their payload is all finite or not."""
        key_value: dict[str, str] = {}
        for key, ifo in self.datasets.items():
            key_value[key] = f"{ifo[-1]}"
        with open(
            kwargs.get(
                "file_path",
                f"""{self.file_path}.malformed{kwargs.get("suffix", "")}.yaml""",
            ),
            "w",
        ) as fp:
            yaml.dump(key_value, fp, default_flow_style=False, sort_keys=True)

    def report_groups(self):
        logger.info(f"{self.file_path} contains the following groups:")
        for key, ifo in self.groups.items():
            logger.info(f"{key}, {ifo}")

    def report_datasets(self):
        logger.info(f"{self.file_path} contains the following datasets:")
        for key, ifo in self.datasets.items():
            logger.info(f"{key}, {ifo}")

    def report_attributes(self):
        logger.info(f"{self.file_path} contains the following attributes:")
        for key, ifo in self.attributes.items():
            logger.info(f"{key}, {ifo}")

    def report_content(self):
        self.report_groups()
        self.report_datasets()
        self.report_attributes()

    def store_report(
        self,
        store_instances=False,
        store_instances_templatized=True,
        store_templates=False,
    ):
        if store_instances is True:
            logger.info(
                f"Storing analysis results in "
                f"{self.file_path[self.file_path.rfind('/') + 1 :]}."
                f"EbsdHdfFileInstanceNames.txt..."
            )
            with open(f"{self.file_path}.EbsdHdfFileInstanceNames.txt", "w") as txt:
                for instance_name, concept in self.instances.items():
                    txt.write(
                        f"{instance_name}, hdf: {concept.hdf}, "
                        f"type: {concept.dtype}, shape: {concept.shape}\n"
                    )

        if store_instances_templatized is True:
            logger.info(
                f"Storing analysis results in "
                f"{self.file_path[self.file_path.rfind('/') + 1 :]}"
                f".EbsdHdfFileInstanceNamesTemplatized.txt..."
            )
            with open(
                f"{self.file_path}.EbsdHdfFileInstanceNamesTemplatized.txt", "w"
            ) as txt:
                for instance_name, concept in self.instances.items():
                    txt.write(f"{instance_name}, hdf: {concept.hdf}\n")

        if store_templates is True:
            logger.info(
                f"Storing analysis results in "
                f"{self.file_path[self.file_path.rfind('/') + 1 :]}"
                f".EbsdHdfFileTemplateNames.txt..."
            )
            with open(f"{self.file_path}.EbsdHdfFileTemplateNames.txt", "w") as txt:
                for template_name, concept in self.templates.items():
                    txt.write(
                        f"{template_name}, hdf: {concept.hdf}, "
                        f"type: {concept.dtype}, shape: {concept.shape}\n"
                    )

    def get_attribute_value(self, h5path):
        if self.h5r is not None:
            if h5path in self.attributes:
                trg, attribute_name = h5path.split("@")
                # with (self.file_path, "r") as h5r:
                obj = self.h5r[trg].attrs[attribute_name]
                if isinstance(obj, np.bytes_):
                    return obj[0].decode("utf8")
                else:
                    return obj
        return None

    def get_dataset_value(self, h5path):
        if self.h5r is not None:
            if h5path in self.datasets:
                if self.datasets[h5path][0] == "IS_REGULAR_DATASET":
                    # with (self.file_path, "r") as h5r:
                    obj = self.h5r[h5path]
                    if isinstance(obj[0], np.bytes_):
                        return obj[0].decode("utf8")
                    else:
                        return obj  # [()].decode("utf8")
            # implement get the entire compound dataset
            if h5path.count("#") == 1:
                # with (self.file_path, "r") as h5r:
                obj = self.h5r[h5path[0 : h5path.rfind("#")]]
                return obj.fields(h5path[h5path.rfind("#") + 1 :])[:]
            return None

    def get_value(self, h5path):
        """Return tuple of normalized regular ndarray for h5path or None."""
        # h5path with exactly one @ after rfind("/") indicating an attribute
        # h5path with exactly one # after rfind("/") indicating a field name in compound type
        # most likely h5path names a dataset
        if h5path.count("@") == 0:
            return self.get_dataset_value(h5path)
        if h5path.count("@") == 1:
            return self.get_attribute_value(h5path)
        # no need to check groups as they have no value
        return None
