"""Run from any directory: python examples/synthetic/run_demo.py"""
import argparse
from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from analysis.interactions import FEATURES, load_counts, summarize, compare_groups, plot_summary


def generate(path):
    """Fixed seed; fabricated independent compound profiles and related poses.

    Group-specific probabilities deliberately illustrate an analysis signal.
    They do not model PAH, GCDH or experimental drug response.
    """
    rng = np.random.default_rng(42)
    probabilities = {'control':[.55,.35,.2], 'stabilizer':[.75,.8,.3], 'destabilizer':[.4,.2,.65]}
    rows = []
    for group, probs in probabilities.items():
        for i in range(20):
            active = rng.random(3) < probs
            base = (rng.integers(1, 5, 3)*active).astype(int)
            for pose in range(1, 4):
                counts = np.maximum(0, base-rng.integers(0,2,3))
                rows.append(dict(compound_id=f'{group}_{i:02}', pose_id=str(pose), group=group,
                                 **dict(zip(FEATURES, counts.tolist()))))
    pd.DataFrame(rows).to_csv(path,index=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,help='Validated real counts or a custom synthetic CSV; no automatic generation when supplied')
    parser.add_argument('--output-dir',type=Path,default=ROOT/'examples/synthetic/output')
    args=parser.parse_args(); out=args.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    if args.input:
        source=args.input.resolve()
    else:
        source=out/'synthetic_pose_counts.csv'; generate(source)
    df=load_counts(source); means,presence=summarize(df)
    means.to_csv(out/'compound_mean_counts.csv',index=False)
    presence.to_csv(out/'compound_presence.csv',index=False)
    compare_groups(presence).to_csv(out/'compound_comparisons.csv',index=False)
    # The bundled plotting template is specifically labeled for the synthetic demo.
    if not args.input:
        plot_summary(means,out/'synthetic_interactions.svg')
    print(f'Analyzed {len(means)} compounds / {len(df)} pose rows. Outputs: {out}')

if __name__=='__main__': main()
