from astro_pointer.helpers import get_current_date_time_string, get_offset, utc_offset_to_tzstring

class TestHelpers:

    def test_get_offset(self):
        assert get_offset(0, 0) == 0
        assert get_offset(22.3193, 114.1694) == 28800       # UTC+8
        assert get_offset(40.7128, -74.0060) == -14400      # UTC-4
        assert get_offset(-18.031282, 178.422218) == 43200  # UTC+12


    def test_utc_offset_to_tzstring(self):
        assert utc_offset_to_tzstring(0) == "UTC+00:00"
        assert utc_offset_to_tzstring(3600) == "UTC+01:00"
        assert utc_offset_to_tzstring(-3600) == "UTC-01:00"
        assert utc_offset_to_tzstring(43200) == "UTC+12:00"


    def test_get_current_date_time_string(self):
        pass