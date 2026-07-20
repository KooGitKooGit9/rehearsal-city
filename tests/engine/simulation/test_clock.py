from engine.simulation.clock import TICKS_PER_DAY, tick_to_clock_str


def test_tick_to_clock_str_midnight():
    assert tick_to_clock_str(0) == "00:00"


def test_tick_to_clock_str_example():
    assert tick_to_clock_str(48) == "08:00"


def test_tick_to_clock_str_wraps_at_day_boundary():
    assert tick_to_clock_str(TICKS_PER_DAY) == "00:00"
