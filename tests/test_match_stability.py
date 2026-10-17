import unittest
try:
    import numpy as np
except ModuleNotFoundError:
    np=None
if np is not None:
    from src.analyze_match_stability import percentiles, dense_ranks, profile_score, context_factor


@unittest.skipIf(np is None, 'Optional NumPy dependency is required for stability tests')
class MatchStabilityTests(unittest.TestCase):
    def test_ties_and_negative_direction(self):
        np.testing.assert_allclose(percentiles([0,0,2,4]),[25,25,62.5,87.5])
        np.testing.assert_allclose(percentiles([0,0,2,4],True),[75,75,37.5,12.5])
        np.testing.assert_array_equal(dense_ranks([80,80,70]),[[1,1,2]])

    def test_rates_use_summed_minutes_and_ratio_denominators(self):
        fields=['minutes','shots','passes_completed','passes_attempted']
        totals=np.array([[[180,2,90,100],[90,2,8,10]]],dtype=float)
        profile={'weights':{'shots_p90':50,'pass_completion_pct':50}}
        np.testing.assert_allclose(profile_score(totals,profile,fields),[[50,50]])
        np.testing.assert_allclose(profile_score(totals*3,profile,fields),[[50,50]])

    def test_context_is_neutral_at_half_and_has_correct_direction(self):
        self.assertEqual(context_factor(.5,'tackles_won'),1)
        self.assertGreater(context_factor(.7,'tackles_won'),1)
        self.assertLess(context_factor(.7,'progressive_carries'),1)
        self.assertEqual(context_factor(.7,'aerial_wins'),1)
        self.assertEqual(context_factor(.7,'passes_attempted'),1)
        self.assertEqual(context_factor(.7,'shots',defense_only=True),1)

    def test_missing_sample_not_silently_imputed(self):
        with self.assertRaises(ValueError):
            profile_score(np.array([[[0.,0.]]]),{'weights':{'shots_p90':100}},['minutes','shots'])


if __name__=='__main__': unittest.main()
