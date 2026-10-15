"""Compound-level interaction analysis. No assay or structure data are bundled."""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact, false_discovery_control

FEATURES = ['hydrophobic', 'hbond', 'ionic']
KEYS = ['compound_id', 'pose_id', 'group']


def load_counts(path):
    """Validate one row per compound/pose; never infer labels from filenames."""
    df = pd.read_csv(path, dtype={'compound_id': str, 'pose_id': str})
    required = KEYS + FEATURES
    missing = set(required) - set(df)
    if missing:
        raise ValueError(f'Missing columns: {sorted(missing)}')
    if df[required].isna().any().any() or (df[KEYS].astype(str).apply(lambda s: s.str.strip()) == '').any().any():
        raise ValueError('Identifiers, groups and counts must be present')
    if df.duplicated(['compound_id', 'pose_id']).any():
        raise ValueError('Duplicate compound/pose rows')
    if df.groupby('compound_id')['group'].nunique().gt(1).any():
        raise ValueError('A compound must have exactly one group label')
    values = df[FEATURES].apply(pd.to_numeric, errors='raise')
    if not np.isfinite(values.to_numpy()).all() or (values < 0).any().any() or (values % 1 != 0).any().any():
        raise ValueError('Counts must be finite nonnegative integers')
    df[FEATURES] = values.astype(int)
    return df


def summarize(df):
    """Mean counts for display; any-pose presence for compound-level tests.

    Every compound must have the same number of poses so any-pose presence has
    the same observation opportunity. Related poses are not independent samples.
    """
    nposes = df.groupby('compound_id').size()
    if nposes.nunique() != 1:
        raise ValueError('Use a common pose count per compound before analysis')
    grouped = df.groupby(['compound_id', 'group'], sort=True)[FEATURES]
    means = grouped.mean().reset_index()
    presence = grouped.max().gt(0).astype(int).reset_index()
    return means, presence


def compare_groups(presence, control='control', groups=('stabilizer', 'destabilizer')):
    """Two-sided Fisher tests, fixed count>0 rule, one BY family across all tests.

    Effect size is the compound contact-prevalence difference (group-control).
    Empty groups fail explicitly. Constant features are reported as uninformative.
    """
    if not groups or len(set(groups)) != len(groups) or control in groups:
        raise ValueError('Specify distinct comparison groups and a separate control')
    unexpected = set(presence['group']) - {control, *groups}
    if unexpected:
        raise ValueError(f'Unmapped group labels: {sorted(unexpected)}')
    if presence['compound_id'].duplicated().any():
        raise ValueError('Statistical table must have one row per compound')
    if not presence[FEATURES].isin([0, 1]).all().all():
        raise ValueError('Presence features must be binary')
    rows = []
    for group in groups:
        a = presence.loc[presence.group == group, FEATURES]
        b = presence.loc[presence.group == control, FEATURES]
        if a.empty or b.empty:
            raise ValueError(f'Missing comparison group: {group} or {control}')
        for feature in FEATURES:
            x, y = int(a[feature].sum()), int(b[feature].sum())
            table = [[x, len(a)-x], [y, len(b)-y]]
            informative = len(set(a[feature]) | set(b[feature])) > 1
            p = float(fisher_exact(table, alternative='two-sided').pvalue) if informative else 1.0
            rows.append(dict(group=group, control=control, feature=feature,
                             n_group=len(a), n_control=len(b), present_group=x,
                             present_control=y, prevalence_difference=x/len(a)-y/len(b),
                             p_value=p, status='tested' if informative else 'constant_feature'))
    result = pd.DataFrame(rows)
    result['p_adjusted_by'] = false_discovery_control(result.p_value.to_numpy(), method='by')
    return result


def plot_summary(means, output):
    """Group distributions of per-compound mean counts; illustrative, not affinity."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    order = ['control', 'stabilizer', 'destabilizer']
    colors = ['#9db9cd', '#246b9b', '#173b59']
    fig, axes = plt.subplots(1, 3, figsize=(11, 4), constrained_layout=True)
    rng = np.random.default_rng(5)
    for ax, feature in zip(axes, FEATURES):
        vals = [means.loc[means.group == g, feature].to_numpy() for g in order]
        bp = ax.boxplot(vals, patch_artist=True, showfliers=False)
        for box, color in zip(bp['boxes'], colors): box.set_facecolor(color); box.set_alpha(.4)
        for i, (v, color) in enumerate(zip(vals, colors), 1):
            ax.scatter(i+rng.uniform(-.1,.1,len(v)), v, color=color, s=13, alpha=.7)
        ax.set_xticks([1,2,3], ['Control','Stabilizer','Destabilizer'], rotation=18)
        ax.set_title(feature.capitalize()); ax.spines[['top','right']].set_visible(False)
    axes[0].set_ylabel('Mean contact count across 3 poses / compound')
    fig.suptitle('SYNTHETIC DEMO · protein–ligand interaction analysis', fontsize=14, fontweight='bold')
    fig.supxlabel('Fabricated group labels and counts · each point is one compound · no biological conclusion', fontsize=9)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180); plt.close(fig)
