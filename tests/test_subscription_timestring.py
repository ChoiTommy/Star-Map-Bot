from astro_pointer.features.subscription import are_timings_valid

class TestSubscriptionTimestring:

    def test_are_timings_valid(self):
        assert are_timings_valid(["12:00", "13:00"]) == (True, ["12", "13"], ["00", "00"])
        assert are_timings_valid(["00:00", "01:59", "23:59"]) == (True, ["00", "01", "23"], ["00", "59", "59"])
        assert are_timings_valid(["33:00"]) == (False, [], [])
        assert are_timings_valid(["00:60"]) == (False, [], [])
        assert are_timings_valid(["bb:aa"]) == (False, [], [])
