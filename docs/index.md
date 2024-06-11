---
hide: toc
---

# pynxtools-apm documentation
pynxtools-apm is a free and open-source data software for creating standardized semantic serializations of atom probe tomography and related field-ion microscopy data and metadata for research data management using NeXus, implemented with the goal to make scientific research data FAIR (findable, accessible, interoperable and reusable).

pynxtools-apm, which is a plugin for pynxtools, provides a tool for reading data from various proprietary and open data formats from technology partners of the
atom probe community and standardizing it such that it is compliant with the NeXus application definition NXapm.

pynxtools-apm is developed both as a standalone reader and as a tool within NOMAD, which is the open-source research data management platform for Materials Science that is developed by the [FAIRmat consortium of the German National Research Data Infrastructure (German NFDI)](https://www.nfdi.de/consortia-fairmat/?lang=en).

pynxtools-apm solves the challenge that comes with using heterogeneous and semantically ambiguous serialization formats that are commonly used in atom probe research. In addition, the plugin provides an interface for writing readers for different file formats to be mapped to NeXus.

pynxtools-apm is useful for scientists from the atom probe community who deal with heterogeneous data, for technology partners, software developers, and data providers who search for ways to make their data more completely aligned with the aims of the FAIR principles.

<!-- A single sentence that says what the product is, succinctly and memorably -->
<!-- A paragraph of one to three short sentences, that describe what the product does. -->
<!-- A third paragraph of similar length, this time explaining what need the product meets -->
<!-- Finally, a paragraph that describes whom the product is useful for. -->

<div markdown="block" class="home-grid">
<div markdown="block">

### Tutorial
<!--This is the place where to add documentation of [diátaxis](https://diataxis.fr) content type tutorial.-->

- [Convert atom probe content to NeXus](tutorial/standalone.md)
- [How to use a NeXus/HDF5 file](tutorial/nexusio.md)
<!-- - [Convert data to NeXus using NOMAD Oasis](tutorial/oasis.md) -->

</div>
<div markdown="block">

### How-to guides
<!--This is the place where to add documentation of [diátaxis](https://diataxis.fr) content type how-to guides.-->


</div>
<div markdown="block">

### Learn
<!--This is the place where to add documentation of [diátaxis](https://diataxis.fr) content type explanation.-->

- [Scope and idea](explanation/learn.md)
- [Known issues](explanation/performance.md)

</div>
<div markdown="block">

### Reference
<!--This is the place where to add documentation of [diátaxis](https://diataxis.fr) content type reference.-->
Here you can learn which specific pieces of information and concepts the plugin supports for the
respective file formats of the atom probe tomography and field-ion microscopy communities.

- [How to map pieces of information to NeXus](reference/contextualization.md)
- [APT file format](reference/apt.md)
- [ePOS file format](reference/epos.md)
- [POS file format](reference/pos.md)
- [RNG file format](reference/rng.md)
- [RRNG file format](reference/rrng.md)
- [Matlab Atom Probe Toolbox ranging definitions](reference/faufig.md)
- [OXCART instrument and pyccapt](reference/pyccapt.md)
- [ATO file format](reference/ato.md)
- [ENV file format](reference/env.md)
- [CSV file format](reference/csv.md)
- [Inspico file formats](reference/inspico.md)
- [AMETEK/Cameca ROOT-based formats](reference/camecaroot.md)
- [Automated charge state analysis](reference/mqanalysis.md)
- [Automated extraction of elements](reference/atomtypes.md)

</div>
</div>

<h2>Project and community</h2>
[The work is funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) – 460197019 (FAIRmat)](https://gepris.dfg.de/gepris/projekt/460197019?language=en).