# Workflow and reproducibility guide

## Scope

The numbered notebooks document a research analysis workflow, rather than a packaged application. Their numbering is a reading guide; several stages consume separately generated files and are not an automatically connected pipeline.

## Inputs and outputs

| Stage | Expected inputs | Main derived outputs |
| --- | --- | --- |
| Variant analysis | Mutation predictions containing mutation, position and ddG_pred fields; variant-position annotations | Pivot tables and annotated heatmaps |
| Pocket mapping | Protein PDB and docked ligand PDBQT or pose files | Complex files, pocket-residue CSV tables and binary residue maps |
| Interaction analysis | Prepared protein–ligand complexes and interaction tables | Residue-by-interaction matrices and visualizations |
| Compound summaries | Per-compound/per-pose interaction matrices and group labels | Aggregated feature tables and distribution plots |
| Exploratory statistics | Compound-feature table with group labels | Threshold-dependent contingency tables and exploratory p-values |

Raw research inputs are not provided as a complete reproducible dataset. Only use inputs you are authorized to access and share.

## Environment

Observed dependencies include Python, Jupyter, pandas, NumPy, Matplotlib, Seaborn, SciPy, RDKit, Biopython, PyMOL with pymol2, PLIP and the Open Babel command-line tool. Dependencies and versions need validation together before a reproducible environment file can be published.

Run notebooks that import `src.generate_graph_new` with the `notebooks/` directory as the working directory, or explicitly configure the module search path. The helper file is located at `notebooks/src/generate_graph_new.py`.

## Before running

1. Replace hard-coded input/output and executable paths with local equivalents.
2. Confirm protein identity, chain selection, residue numbering and sequence length. Several notebooks assume PAH positions 0–452; this must be reconciled with structure-file numbering.
3. Confirm that ligand/pose filenames match the parsing rules used by the notebook.
4. Review temporary-directory operations: some cells remove a relative `tmp` directory. Use an isolated working directory and inspect those cells first.
5. Check state dependencies. For example, the first notebook references `df_pivot_AF3`, which is not defined by the preceding shown cells.
6. Check compound group labels against their source definition. A summary cell maps a weak label to strong; confirm whether this represents a justified grouping of controls.
7. Review and clear notebook outputs before sharing. Research tables and rendered figures can disclose information even when the underlying input files are absent.

## Statistical interpretation

Notebook 07 searches across thresholds and selects the minimum p-value. This is a data-dependent selection procedure; the selected value cannot be interpreted as an ordinary pre-specified single-test p-value.

Before confirmatory analysis, specify the unit of analysis, define group labels and thresholds, inspect contingency-table assumptions, and choose a suitable correction or validation procedure. Related poses must remain associated with their compound. The broad exception handler should be replaced with explicit handling so invalid tests are recorded rather than silently assigned a p-value.

## Development priorities

- Centralized path and analysis configuration.
- A permitted synthetic or public example dataset.
- A tested dependency environment.
- Explicit input schema and residue-numbering checks.
- Compound/pose alignment using identifiers rather than row order.
- A documented, validated statistical analysis plan.

These items describe future improvements, not completed features.
