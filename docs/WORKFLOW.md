# Workflow and reproducibility guide

## Start with the runnable example

The [synthetic demo](../examples/synthetic/README.md) needs only the pinned scientific-Python dependencies in `requirements-demo.txt`. It is the fully executed public example. The [generated preview](../figures/synthetic_interactions.svg) contains fabricated values only.

## Research notebook configuration

Copy `config.example.json` to `config.local.json` in the repository root. Relative paths in this file resolve against the configuration file, not the notebook working directory. Alternatively, set `PROTEIN_ANALYSIS_CONFIG` to your configuration file path.

```json
{
  "variant_predictions": "data/variant_predictions.csv",
  "complex_manifest": "data/complex_manifest.csv",
  "output_dir": "results",
  "ligand_id": "UNK",
  "pocket_distance_angstrom": 6.0
}
```

Use authorized local inputs only. No research inputs are supplied. Open Jupyter within this repository. The local configuration, raw data, results and generated demo outputs are ignored by git.

### Input schemas

- **Notebook 01:** CSV with `mutation`, `position`, `ddG_pred`. Provide numeric effect predictions, unique mutation/position pairs and documented source-model/sign conventions. Protein/domain or clinical annotations are not bundled.
- **Notebooks 02 and 04:** manifest CSV with `compound_id`, `pose_id`, `group`, `complex_path`. Each row refers to one prepared protein–ligand complex PDB. Relative complex paths resolve against the manifest directory. Use one group per compound and unique compound/pose keys. The ligand residue name must match `ligand_id`.
- **Notebooks 03 and 05:** consume pocket or interaction CSVs written by 02/04. Residue keys retain chain and input residue number; sequence length is not hard-coded.
- **Notebook 06:** produces one row per compound/pose with `compound_id`, `pose_id`, `group`, `hydrophobic`, `hbond`, `ionic`. Zero-event poses are preserved using the manifest metadata. Other PLIP classes remain in the detailed interaction map, but are outside the three-feature comparison family.
- **Notebook 07:** defaults to the generated synthetic CSV. To use notebook 06 outputs, explicitly change `input_path` and check group definitions before execution.

The old notebooks assumed filename-encoded groups and positional row alignment. The revised analysis uses explicit keys and joins. It does not silently recode historical weak/strong categories.

## Structural environment and limits

The structural helper module is attributed to PD Dr. Behnam Yousefi in the original notebooks. Its imports include PyMOL/pymol2, PLIP, RDKit and Biopython. These optional dependencies are not part of the demo environment. Structure preparation must occur upstream; the new notebooks consume prepared complexes and do not invoke shell commands or remove temporary directories.

The helper retains research assumptions, including atom ordering for some interaction assignments, a limited residue-key representation and handling of PLIP interaction types. The structural extraction stages have not been executed against institutional data in this update. A small variable-reference defect in the metal-contact branch was corrected, but this does not establish validation of that branch. Inspect raw extraction outputs and validate residue/ligand mapping before interpreting them. Structural dependencies need their own tested environment.

## Statistical analysis

`analysis/interactions.py` validates count tables, requires common pose coverage and summarizes once per compound. It uses a fixed `count > 0` any-pose presence rule, two-sided Fisher exact tests and a single Benjamini–Yekutieli family across all planned comparisons. It records prevalence differences, group sizes, positive counts and all adjusted p-values. Missing groups, invalid counts and duplicate pose keys fail explicitly. Constant features are flagged as uninformative.

The earlier notebook scanned thresholds and selected minimum p-values. That procedure has been replaced; historical results must be reanalyzed and cannot be validated without their source data. Corrected methodology does not establish new research findings.

## Verification performed

- Synthetic demo executed with 60 compounds and 180 pose rows.
- Unit tests cover identifier/count validation, sample unit, row-order invariance, repeated-pose invariance, absent groups and constant features.
- All numbered notebook code cells checked for Python syntax.
- Tabular/plotting notebook stages exercised with synthetic fixtures; structural extraction notebooks require the optional environment and prepared complexes.
- Notebook outputs cleared before commit. No research figures or clinical inputs were newly published.

## References

- [SciPy Fisher exact test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.fisher_exact.html)
- [SciPy false discovery control](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.false_discovery_control.html)

Learning notebooks are retained in `archive/learning/` for provenance and are outside the main analysis guide.
