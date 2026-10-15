"""Configuration shared by research notebooks; no institutional paths."""
import json
import os
from pathlib import Path


def project_root():
    here = Path.cwd().resolve()
    for candidate in (here, *here.parents):
        if (candidate/'analysis/interactions.py').is_file(): return candidate
    raise FileNotFoundError('Open the notebook from within this repository')


def load_config():
    root=project_root()
    source=Path(os.environ.get('PROTEIN_ANALYSIS_CONFIG',root/'config.local.json')).resolve()
    if not source.is_file():
        raise FileNotFoundError('Copy config.example.json to config.local.json and configure authorized local inputs. See docs/WORKFLOW.md.')
    config=json.loads(source.read_text())
    def resolve(value):
        path=Path(value).expanduser()
        return path if path.is_absolute() else (source.parent/path).resolve()
    for name in ['variant_predictions','complex_manifest','output_dir']:
        config[name]=resolve(config[name])
    config['output_dir'].mkdir(parents=True,exist_ok=True)
    return config


def load_manifest(config):
    import pandas as pd
    manifest=pd.read_csv(config['complex_manifest'],dtype={'compound_id':str,'pose_id':str})
    required=['compound_id','pose_id','group','complex_path']
    if not set(required)<=set(manifest): raise ValueError(f'Manifest needs {required}')
    if manifest[required].isna().any().any(): raise ValueError('Missing manifest value')
    if manifest.duplicated(['compound_id','pose_id']).any(): raise ValueError('Duplicate compound/pose')
    if manifest.groupby('compound_id').group.nunique().gt(1).any(): raise ValueError('Inconsistent compound group')
    def resolve(value):
        path=Path(value).expanduser()
        path=path if path.is_absolute() else config['complex_manifest'].parent/path
        if not path.is_file(): raise FileNotFoundError(path)
        return str(path.resolve())
    manifest['complex_path']=manifest.complex_path.map(resolve)
    return manifest
