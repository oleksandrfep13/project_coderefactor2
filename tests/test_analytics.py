import pytest
from datetime import datetime, timedelta
from src.application.analytics import (
    AverageMoodStrategy, VolatilityStrategy,
    RecentTrendStrategy, StabilityStrategy, ExtremeValueStrategy
)
from src.domain.models import HealthEntry, EntryType

def create_entry(value):
    return HealthEntry("id", datetime.now(), EntryType.MOOD, float(value), "note")

def create_dated_entry(value, days_offset, seconds_offset=0):
    dt = datetime.now() + timedelta(days=days_offset, seconds=seconds_offset)
    return HealthEntry("id", dt, EntryType.MOOD, float(value), "note")

def test_avg_empty(): assert AverageMoodStrategy().calculate([]) == 0.0
def test_avg_single(): assert AverageMoodStrategy().calculate([create_entry(4.0)]) == 4.0
def test_avg_normal(): assert AverageMoodStrategy().calculate([create_entry(2.0), create_entry(4.0)]) == 3.0
def test_avg_bounds(): assert AverageMoodStrategy().calculate([create_entry(1.0), create_entry(5.0)]) == 3.0
def test_avg_precision(): assert AverageMoodStrategy().calculate([create_entry(1.11), create_entry(1.12)]) == 1.12
def test_avg_all_ones(): assert AverageMoodStrategy().calculate([create_entry(1.0)] * 10) == 1.0
def test_avg_all_fives(): assert AverageMoodStrategy().calculate([create_entry(5.0)] * 100) == 5.0
def test_avg_large_dataset():
    data = [create_entry(i) for i in [1, 2, 3, 4, 5] * 1000]
    assert AverageMoodStrategy().calculate(data) == 3.0
def test_avg_zeroes(): assert AverageMoodStrategy().calculate([create_entry(0.0), create_entry(0.0)]) == 0.0
def test_avg_fractional_results():
    assert round(AverageMoodStrategy().calculate([create_entry(3.0), create_entry(4.0), create_entry(4.0)]), 2) == 3.67

def test_vol_empty(): assert VolatilityStrategy().calculate([]) == 0.0
def test_vol_single(): assert VolatilityStrategy().calculate([create_entry(5.0)]) == 0.0
def test_vol_stable(): assert VolatilityStrategy().calculate([create_entry(5.0), create_entry(5.0)]) == 0.0
def test_vol_simple_change(): assert VolatilityStrategy().calculate([create_entry(1.0), create_entry(3.0)]) == 2.0
def test_vol_complex_change(): assert VolatilityStrategy().calculate([create_entry(1.0), create_entry(5.0), create_entry(2.0)]) == 3.5
def test_vol_strictly_increasing():
    assert VolatilityStrategy().calculate([create_entry(1), create_entry(2), create_entry(3), create_entry(4), create_entry(5)]) == 1.0
def test_vol_strictly_decreasing():
    assert VolatilityStrategy().calculate([create_entry(5), create_entry(4), create_entry(3), create_entry(2), create_entry(1)]) == 1.0
def test_vol_alternating_extremes():
    assert VolatilityStrategy().calculate([create_entry(1), create_entry(5), create_entry(1), create_entry(5)]) == 4.0
def test_vol_long_plateau():
    assert VolatilityStrategy().calculate([create_entry(3)] * 5 + [create_entry(7)]) == 0.8
def test_vol_micro_fluctuations():
    assert round(VolatilityStrategy().calculate([create_entry(3.1), create_entry(3.2), create_entry(3.1)]), 2) == 0.1

def test_stab_empty(): assert StabilityStrategy().calculate([]) == 0.0
def test_stab_stable(): assert StabilityStrategy().calculate([create_entry(3.0), create_entry(3.0)]) == 0.0
def test_stab_single(): assert StabilityStrategy().calculate([create_entry(4.0)]) == 0.0
def test_stab_varied(): assert StabilityStrategy().calculate([create_entry(1.0), create_entry(5.0)]) == 2.0
def test_stab_precision(): assert round(StabilityStrategy().calculate([create_entry(1.0), create_entry(2.0), create_entry(3.0)]), 1) == 0.8
def test_stab_bimodal_extremes():
    assert StabilityStrategy().calculate([create_entry(1.0)] * 10 + [create_entry(5.0)] * 10) == 2.0
def test_stab_perfect_uniform():
    assert round(StabilityStrategy().calculate([create_entry(1), create_entry(2), create_entry(3), create_entry(4), create_entry(5)]), 2) == 1.41
def test_stab_large_identical_set():
    assert StabilityStrategy().calculate([create_entry(2.5)] * 1000) == 0.0

def test_extreme_empty(): assert ExtremeValueStrategy().calculate([]) == 0.0
def test_extreme_single(): assert ExtremeValueStrategy().calculate([create_entry(3.0)]) == 0.0
def test_extreme_range(): assert ExtremeValueStrategy().calculate([create_entry(1.0), create_entry(5.0)]) == 4.0
def test_extreme_negative_math(): assert ExtremeValueStrategy().calculate([create_entry(2.0), create_entry(2.0)]) == 0.0
def test_extreme_unsorted(): assert ExtremeValueStrategy().calculate([create_entry(5.0), create_entry(1.0), create_entry(3.0)]) == 4.0
def test_extreme_all_same(): assert ExtremeValueStrategy().calculate([create_entry(4.0)] * 50) == 0.0
def test_extreme_decimals(): assert round(ExtremeValueStrategy().calculate([create_entry(1.5), create_entry(4.8)]), 1) == 3.3
def test_extreme_large_dataset():
    data = [create_entry(3.0)] * 99 + [create_entry(1.0), create_entry(5.0)] + [create_entry(3.0)] * 99
    assert ExtremeValueStrategy().calculate(data) == 4.0

def test_trend_empty(): assert RecentTrendStrategy().calculate([]) == 0.0
def test_trend_too_old(): assert RecentTrendStrategy().calculate([create_dated_entry(5.0, -10)]) == 0.0
def test_trend_recent(): assert RecentTrendStrategy().calculate([create_dated_entry(4.0, 0)]) == 4.0
def test_trend_mixed():
    entries = [create_dated_entry(4.0, 0), create_dated_entry(1.0, -20)]
    assert RecentTrendStrategy().calculate(entries) == 4.0
def test_trend_multiple_recent():
    entries = [create_dated_entry(2.0, -1), create_dated_entry(4.0, -2)]
    assert RecentTrendStrategy().calculate(entries) == 3.0

def test_trend_exactly_on_boundary():
    assert RecentTrendStrategy().calculate([create_dated_entry(3.0, -7)]) == 3.0

def test_trend_just_outside_boundary():
    assert RecentTrendStrategy().calculate([create_dated_entry(5.0, -7, -1)]) == 0.0

def test_trend_just_inside_boundary():
    assert RecentTrendStrategy().calculate([create_dated_entry(4.0, -7, +1)]) == 4.0

def test_trend_future_date_ignored_or_counted():
    assert RecentTrendStrategy().calculate([create_dated_entry(5.0, +2)]) == 5.0

def test_trend_all_old_one_new():
    entries = [create_dated_entry(1.0, -30)] * 50 + [create_dated_entry(4.0, -1)]
    assert RecentTrendStrategy().calculate(entries) == 4.0