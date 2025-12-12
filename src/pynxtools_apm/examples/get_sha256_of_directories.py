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

"""Compute checksums of each file in a directory recurse common compressed files."""

# python3 rdm_management_complete.py 'test' '.'
import hashlib
import os
import sys
import tarfile
import zipfile
from datetime import datetime

import py7zr
import rarfile

# import blake3
from pynxtools_apm.utils.versioning import __version__

SEPARATOR = "____"
HASHING = True

from collections.abc import Mapping


def to_int(value: str | int | bytes | Mapping[str, str]) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, bytes):
        return int(value.decode())
    if isinstance(value, str):
        return int(value)
    raise TypeError(f"Cannot convert {value!r} to int")


def analyze_file(fpath: str, results: str, issues: str, hashing: bool = HASHING) -> int:
    """Get metadata about file and compute its SHA256 hash."""
    byte_size = 0
    if os.path.isfile(fpath):
        try:
            stat = os.stat(fpath)
            byte_size += int(stat.st_size)
            # print(f"{fpath}\t\t{stat.st_mtime_ns}\t\t{stat.st_mtime_ns}\t\t{stat.st_size}")  # int64
            # fhsh = blake3.blake3(max_threads=blake3.blake3.AUTO).update_mmap(fpath).hexdigest()
            results += f"{fpath};{stat.st_size};{stat.st_mtime}"
            if hashing:
                fh = hashlib.sha256()
                with open(fpath, "rb") as ffp:
                    while True:
                        chunk = ffp.read(fh.block_size)
                        if not chunk:
                            break
                        fh.update(chunk)
                results += f";{fh.hexdigest()}"
            results += "\n"
        except Exception as exception:
            issues += f"{fpath}{SEPARATOR}{exception}\n"
    return byte_size


def analyze_tar_file(
    fpath: str, results: str, issues: str, hashing: bool = HASHING
) -> int:
    """Get metadata about tarfile and recursively compute SHA256 hash for each of its files."""
    byte_size = 0
    if fpath.lower().endswith((".tar", ".tar.gz", ".tar.bz2", ".tar.xz")):
        try:
            with tarfile.open(fpath, "r:*") as tar:
                for member in tar:
                    if member.isreg():
                        # thsh = blake3.blake3(tar.extractfile(member.name).read(), max_threads=blake3.blake3.AUTO).hexdigest()
                        # https://github.com/python/cpython/pull/102128
                        # https://github.com/python/cpython/issues/102120
                        tfp = tar.extractfile(member.name)
                        info = member.get_info()
                        results += f"{fpath}:{member.name};{to_int(info['size'])};{to_int(info['mtime'])}"
                        byte_size += to_int(info["size"])
                        if hashing:
                            th = hashlib.sha256()
                            while True:
                                chunk = tfp.read(th.block_size)
                                if not chunk:
                                    tfp.close()
                                    break
                                th.update(chunk)
                            results += f";{th.hexdigest()}"
                        results += "\n"
        except Exception as exception:
            issues += f"{fpath}{SEPARATOR}{exception}\n"
    return byte_size


def analyze_zip_file(
    fpath: str, results: str, issues: str, hashing: bool = HASHING
) -> int:
    """Get metadata about zipfile and recursively compute SHA256 hash for each of its files."""
    byte_size = 0
    if fpath.lower().endswith((".zip", ".eln")):  # .eln, e.g., RO-Crate
        try:
            with zipfile.ZipFile(fpath, "r") as zip_file_hdl:
                for member in zip_file_hdl.infolist():
                    results += f"{fpath}:{member.filename};{member.file_size};{datetime(*member.date_time).timestamp()}"
                    byte_size += int(member.file_size)
                    if hashing:
                        zh = hashlib.sha256()
                        with zip_file_hdl.open(member, "r") as zfp:
                            # zhsh = blake3.blake3(zfp.read(), max_threads=blake3.blake3.AUTO).hexdigest()
                            while True:
                                chunk = zfp.read(zh.block_size)
                                if not chunk:
                                    break
                                zh.update(chunk)
                            results += f";{zh.hexdigest()}"
                    results += "\n"
        except Exception as exception:
            issues += f"{fpath}{SEPARATOR}{exception}\n"
    return byte_size


def analyze_rar_file(
    fpath: str, results: str, issues: str, hashing: bool = HASHING
) -> int:
    """Get metadata about rarfile and recursively compute SHA256 hash for each of its files."""
    byte_size = 0
    if fpath.lower().endswith((".rar")):
        try:
            with rarfile.RarFile(fpath, "r") as rar_file_hdl:
                for member in rar_file_hdl.infolist():
                    results += f"{fpath}:{member.filename};{member.file_size};{datetime(*member.date_time).timestamp()}"
                    byte_size += int(member.file_size)
                    if hashing:
                        rh = hashlib.sha256()
                        with rar_file_hdl.open(member, "r") as rfp:
                            # rhsh = blake3.blake3(fp.read(), max_threads=blake3.blake3.AUTO).hexdigest()
                            while True:
                                chunk = rfp.read(rh.block_size)
                                if not chunk:
                                    break
                                rh.update(chunk)
                            results += f";{rh.hexdigest()}"
                    results += "\n"
        except Exception as exception:
            issues += f"{fpath}{SEPARATOR}{exception}\n"
    return byte_size


def analyze_sevenzip_file(
    fpath: str, results: str, issues: str, hashing: bool = HASHING
) -> int:
    """Get metadata about 7z file and recursively compute SHA256 hash for each of its files."""
    byte_size = 0
    if fpath.lower().endswith((".7z")):
        try:
            with py7zr.SevenZipFile(fpath, "r") as seven_file_hdl:
                mdata: dict[str, dict[str, str | int]] = {}
                for obj in seven_file_hdl.list():
                    if obj.uncompressed > 0:  # do not bookkeep directories in that 7z
                        key = obj.filename
                        if key not in mdata:
                            mdata[key] = {}
                            mdata[key]["mtime"] = f"{obj.creationtime}".replace(
                                " ", "T"
                            )
                            # = datetime.datetime(*obj.creationtime).timestamp()
                            mdata[key]["size"] = obj.uncompressed
                if hashing:
                    for key, bio in seven_file_hdl.readall().items():
                        if key in mdata:
                            sh = hashlib.sha256(bio.getbuffer())
                            # bio.getbuffer().nbytes is equivalent to obj.uncompressed
                            mdata[key]["sha256"] = sh.hexdigest()
                        else:
                            issues += f"{fpath}{SEPARATOR}KeyError {key} not found\n"
                    for key in mdata:
                        results += f"{fpath}:{key};{mdata[key]['size']};{mdata[key]['mtime']};{mdata[key]['sha256']}\n"
                        byte_size += int(mdata[key]["size"])
                else:
                    for key in mdata:
                        results += f"{fpath}:{key};{mdata[key]['size']};{mdata[key]['mtime']}\n"
                        byte_size += int(mdata[key]["size"])
        except Exception as exception:
            issues += f"{fpath}{SEPARATOR}{exception}\n"
    return byte_size


config: dict[str, str] = {
    "python_version": f"{sys.version}",
    "working_directory": f"{os.getcwd()}",
    "pynxtools_apm version": f"{__version__}",
    "rarfile version": f"{rarfile.__version__}",
    "sevenzip version": f"{py7zr.__version__}",
    # "blake3-py version": f"{blake3.__version__}",
    # "blake3-py max_threads": f"{blake3.blake3.AUTO}",
    "directory": sys.argv[1],
}

# tic = datetime.datetime.now().timestamp()
# "file_path:archive_path;byte_size;unix_mtime;sha256sum\n"
# with open(f"{drive_name}.stdout.csv", "w", encoding="utf-8", errors="surrogateescape") as stdout_to_csv_hdl:
#     stdout_to_csv_hdl.write(stdout)

cnt = 0
byte_size_processed = 0
# skip_first_part_completed = False
# skip_fpath = ""  # path inclusive past which to process, before which all paths on the recursive dir traversal are skipped
for root, dirs, files in os.walk(config["directory"]):
    for file in files:
        fpath = f"{root}/{file}".replace(os.sep * 2, os.sep)
        # fname = os.path.basename(fpath)
        suffix = fpath.replace(config["directory"], "")
        cnt += 1
        if byte_size_processed >= (
            1 * 1024 * 1024 * 1024
        ):  # incrementally report results # cnt % 5 == 0:
            print(cnt)  # I/O
            byte_size_processed = 0
# toc = datetime.datetime.now().timestamp()
# with open(f"{drive_name}.stdout.csv", "a", encoding="utf-8", errors="surrogateescape") as stdout_to_csv_hdl:
#     stdout_to_csv_hdl.write(stdout)
print(f"Hashing performed with {cnt} paths")
