import unittest
from src.metrics import event_counts, percentile, progressive, rates, score, stint_minutes


class MetricTests(unittest.TestCase):
    def test_creation_context_and_xg_partition(self):
        shot={'shot':{'statsbomb_xg':.21}}
        cases=[('Regular Play',None,'open_play'),('From Counter',None,'open_play'),
               ('From Corner',None,'set_piece'),('From Free Kick',None,'set_piece'),
               ('Regular Play','Corner','set_piece'),('From Throw In','Throw-in','set_piece'),
               ('From Throw In',None,'open_play'),('From Goal Kick',None,'open_play')]
        for pattern,kind,context in cases:
            with self.subTest(pattern=pattern,kind=kind):
                e={'type':{'name':'Pass'},'play_pattern':{'name':pattern},
                   'pass':{'assisted_shot_id':'s','type':{'name':kind}}}
                c=event_counts(e,{'s':shot})
                self.assertEqual(c['key_passes_'+context],1)
                self.assertAlmostEqual(c['xg_assisted_'+context],.21)
                self.assertEqual(c['key_passes_open_play']+c['key_passes_set_piece'],c['key_passes'])
                self.assertAlmostEqual(c['xg_assisted_open_play']+c['xg_assisted_set_piece'],c['xg_assisted'])

    def test_creation_missing_link_is_not_zero_xg(self):
        with self.assertRaises(ValueError):
            event_counts({'type':{'name':'Pass'},'pass':{'shot_assist':True}}, {})

    def test_halftime_and_added_time(self):
        # A first-half injury-time substitution must not create >90 regulation minutes.
        first = {'from':'00:00','from_period':1,'to':'47:20','to_period':1}
        second = {'from':'47:20','from_period':1,'to':None,'to_period':None}
        self.assertEqual(stint_minutes(first),45)
        self.assertEqual(stint_minutes(second),45)
        stoppage_sub = {'from':'91:00','from_period':2,'to':None,'to_period':None}
        self.assertEqual(stint_minutes(stoppage_sub),0)

    def test_temporary_absence(self):
        pieces = [{'from':'00:00','from_period':1,'to':'51:21','to_period':2},
                  {'from':'53:56','from_period':2,'to':'59:57','to_period':2}]
        self.assertAlmostEqual(sum(stint_minutes(p) for p in pieces),57+22/60)

    def test_progression_is_toward_goal_and_requires_magnitude(self):
        self.assertTrue(progressive([55,40],[80,40]))
        self.assertFalse(progressive([100,40],[105,40]))
        self.assertFalse(progressive([80,40],[55,40]))
        self.assertFalse(progressive(None,[80,40]))

    def test_pass_outcomes_and_set_pieces(self):
        e = {'type':{'name':'Pass'},'location':[55,40],'pass':{'end_location':[80,40]}}
        self.assertEqual(event_counts(e,{})['passes_completed'],1)
        self.assertEqual(event_counts(e,{})['progressive_passes'],1)
        e['pass']['type']={'name':'Free Kick'}
        self.assertEqual(event_counts(e,{})['progressive_passes'],0)
        e['pass']['outcome']={'name':'Unknown'}
        self.assertEqual(event_counts(e,{})['passes_attempted'],0)
        self.assertEqual(event_counts(e,{})['passes_excluded'],1)

    def test_goals_and_assisted_xg(self):
        shot={'type':{'name':'Shot'},'shot':{'type':{'name':'Penalty'},'outcome':{'name':'Goal'},'statsbomb_xg':.78}}
        self.assertEqual(event_counts(shot,{})['goals'],1)
        self.assertEqual(event_counts(shot,{})['non_penalty_goals'],0)
        p={'type':{'name':'Pass'},'pass':{'assisted_shot_id':'s','goal_assist':True}}
        self.assertAlmostEqual(event_counts(p,{'s':shot})['xg_assisted'],.78)
        self.assertEqual(event_counts(p,{'s':shot})['key_passes'],1)

    def test_percentiles_and_direction(self):
        self.assertEqual(percentile(4,[4,4,4]),50)
        self.assertEqual(percentile(0,[0,0,1,2]),25)
        self.assertEqual(percentile(0,[0,0,1,2],True),75)
        self.assertIsNone(percentile(None,[1,2]))

    def test_weights_change_order_and_missing_is_not_zero(self):
        a,b={'a':90,'b':10},{'a':10,'b':90}
        self.assertGreater(score(a,{'a':80,'b':20}),score(b,{'a':80,'b':20}))
        self.assertLess(score(a,{'a':20,'b':80}),score(b,{'a':20,'b':80}))
        self.assertIsNone(score(a,{'a':0,'b':0}))
        self.assertIsNone(score({'a':None},{'a':1}))
        self.assertEqual(score({'a':None,'b':50},{'a':0,'b':1}),50)
        with self.assertRaises(ValueError):
            score(a,{'a':-1})

    def test_rates_weight_denominators(self):
        # Season precision must be 91/110, not average of 90% and 10%.
        self.assertAlmostEqual(rates({'passes_attempted':110,'passes_completed':91},180)['pass_completion_pct'],91/110*100)
        self.assertIsNone(rates({},90)['dribble_success_pct'])
        self.assertIsNone(rates({},0)['shots_p90'])


if __name__=='__main__':
    unittest.main()
