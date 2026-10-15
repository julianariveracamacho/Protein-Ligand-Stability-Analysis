import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from analysis.interactions import load_counts, summarize, compare_groups, FEATURES
from examples.synthetic.run_demo import generate

class InteractionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'data.csv';generate(self.path);self.df=load_counts(self.path)

    def test_compound_unit_and_order_invariance(self):
        means,p=summarize(self.df);self.assertEqual(len(means),60)
        _,shuffled=summarize(self.df.sample(frac=1,random_state=4))
        pd.testing.assert_frame_equal(compare_groups(p),compare_groups(shuffled))
        result=compare_groups(p)
        self.assertEqual(len(result),6)
        self.assertTrue((result.p_adjusted_by>=result.p_value).all())

    def test_repeated_pose_does_not_inflate_sample_size(self):
        extra=self.df.copy();extra['pose_id']='extra_'+extra.pose_id
        _,p=summarize(pd.concat([self.df,extra],ignore_index=True))
        _,original=summarize(self.df)
        pd.testing.assert_frame_equal(compare_groups(p),compare_groups(original))

    def test_bad_inputs_fail(self):
        for df in [pd.concat([self.df,self.df.iloc[:1]]),self.df.assign(hbond=-1),self.df.assign(ionic=np.nan)]:
            df.to_csv(self.path,index=False)
            with self.assertRaises(ValueError):load_counts(self.path)
        with self.assertRaises(ValueError):summarize(self.df.iloc[1:])

    def test_missing_group_and_constant_feature(self):
        _,p=summarize(self.df)
        with self.assertRaises(ValueError):compare_groups(p[p.group!='control'])
        p[FEATURES]=0;r=compare_groups(p)
        self.assertTrue((r.p_value==1).all());self.assertTrue((r.status=='constant_feature').all())

if __name__=='__main__':unittest.main()
