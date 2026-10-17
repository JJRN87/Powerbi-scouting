import unittest
import itertools
from src.analyze_profiles import evaluate, leader_certificate


class ReviewTests(unittest.TestCase):
    def test_dense_ties_and_zero_weights(self):
        matrix = {1:[100,0],2:[0,100],3:[0,0]}
        scores, ranks = evaluate(matrix,[50,50])
        self.assertEqual(ranks,{1:1,2:1,3:2})
        self.assertEqual(scores[1],50)
        self.assertTrue(all(v is None for v in evaluate(matrix,[0,0])[1].values()))

    def test_certificate_distinguishes_dominance_from_weight_dependence(self):
        self.assertTrue(leader_certificate({1:[90,80],2:[60,70]},[50,50],1,.5)['strict_first_proven'])
        self.assertFalse(leader_certificate({1:[100,0],2:[0,100]},[60,40],1,.5)['strict_first_proven'])

    def test_negative_weights_rejected(self):
        with self.assertRaises(ValueError):
            evaluate({1:[90,80]},[-1,100])

    def test_negative_margin_is_still_a_lower_bound(self):
        matrix = {1:[100,0],2:[0,100]}
        bound = leader_certificate(matrix,[60,40],1,.5)['conservative_score_margin_lower_bound']
        for a,b in itertools.product([.5,1,1.5], repeat=2):
            scores,_ = evaluate(matrix,[60*a,40*b])
            self.assertLessEqual(bound, scores[1]-scores[2]+1e-8)
