# Known issues

## Charge state analysis
When the ranging definitions have molecular ions which are composed from many atoms and elements with many isotopes
it is possible that the interpretation of the ranging definitions can take long. The situation is case dependent.
The reason is that while parsing the reader uses a combinatorial algorithm to identify the charge state(s) from the
ranging definitions. The computation time of this algorithm depends on the total number of possible isotopic combinations
that need evaluation.

## Verifying instance against cardinality/existence constraints
Performance relevant for only some cases and input is that the verification of the instantiated schema can be slow.
This verification step is executed before the data are written to the NeXus/HDF5 file. The reason for this issue is that
the dataconverter traverses the dependency graph of the already instantiated concepts of the NXapm application definition
to assure that the template is valid, i.e. that all required quantities have been instantiated. Depending on which branches
get instantiated by the input, this evaluation can be slower as more pathes have to be visited.

Note that this issue is independent of size of the input i.e. how many ions are included in a dataset does not really matter.

## Molecular ions
The reader currently supports to define up to 255 ranging definitions. In all cases where we have seen range files from
groups across the world where more ranging definitions have been made these were typically duplicated lines in the
ranging definitions file.

The reader currently supports to define molecular ions with up to 32 atoms which covers for almost all cases of molecular ion
fragments that are typically studied with atom probe. Note that in mass spectrometry fragments with a considerable larger
number of atoms are observed but telling them apart in atom probe would in practice be even more complicated.

A more detailed overview for resolving molecular ions in atom probe is available [in the literature](https://doi.org/10.1016/j.patter.2020.100192).
