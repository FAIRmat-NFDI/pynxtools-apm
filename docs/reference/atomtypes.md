# Automated extraction of elements in the dataset

All ranging definitions are post-processed by the parser to infer the elements. The set of unique element chemical symbols
is used to define the `/ENTRY[entry*]/specimen/atom_types` in the resulting NeXus/HDF5 file in accordance with the
requirements that are defined by the `NXapm` application definition.
