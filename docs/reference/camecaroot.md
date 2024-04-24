# AMETEK/Cameca CernROOT-based file formats

Please note that the proprietary file formats RRAW, STR, ROOT, RHIT, and HITS from AMETEK/Cameca are currently not processable
with software other than provided by Cameca. We have investigated the situation and were able to confirm though that a substantial number
of metadata have been documented by Cameca. In addition, we have done a successful proof-of-concept to explore a route of reading several pieces of information contained in all of these binary file formats using only Python.

The main motivation for this was to explore a route that would enable automated mapping and normalizing of some of the metadata into NeXus via a simpler - programmatic approach - than having users to enter the information via e.g. electronic lab notebooks or supplementary files.
The main motivation to access the binary file structure directly in contrast to using a library from [Cern's ROOT](https://root.cern/) ecosystem was that every
tool which would include a ROOT-capable pynxtools-apm plugin would also have to install at least some part of the versatile but functionally
rich ROOT library that may not be appropriate in all cases when working with already complex research data management system with their
own dependencies.

AMETEK/Cameca offered to inspect the situation and work on an implementation of features in AP Suite that will eventually allow users to
export some of these metadata via the AMETEK/Cameca APT file format that is open-source. When these features will be available,
we are happy to work on an update of pynxtools-apm and the underlying ifes_apt_tc_data_modeling library.
