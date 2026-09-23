from app.services.rail_engine import Placement, Segment, first_fit, free_gaps


def test_first_fit_leftmost():
    occ = [Segment(20, 40)]
    p = first_fit(100, occ, 15)
    assert p is not None
    assert p.start_cm == 0
    assert p.end_cm == 15


def test_first_fit_skips_too_small_gap():
    occ = [Segment(0, 10), Segment(18, 50)]
    p = first_fit(100, occ, 10)
    assert p is not None
    assert p.start_cm == 50


def test_no_space():
    occ = [Segment(0, 80)]
    assert first_fit(100, occ, 25) is None


def test_free_gaps_edges():
    gaps = free_gaps(50, [Segment(10, 20), Segment(30, 35)])
    assert gaps == [Segment(0, 10), Segment(20, 30), Segment(35, 50)]


def test_max_items_blocks_even_with_space_left():
    # 已挂 2 件达上限，剩余厘米远够挂第三件，仍必须拒绝
    occ = [Segment(0, 10), Segment(10, 20)]
    assert first_fit(100, occ, 15, active_items=2, max_items=2) is None


def test_max_items_allows_below_cap():
    occ = [Segment(0, 10)]
    p = first_fit(100, occ, 15, active_items=1, max_items=2)
    assert p == Placement(10, 25)


def test_none_cap_means_unlimited():
    # 未配置上限的杆不限制件数
    occ = [Segment(start, start + 10) for start in range(0, 50, 10)]
    p = first_fit(100, occ, 9, active_items=5, max_items=None)
    assert p is not None
    assert p.start_cm == 50
