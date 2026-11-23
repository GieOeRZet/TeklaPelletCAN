from tools.cg_l3_table23_scan import SOURCE_BASE, RECORD_SIZE, RECORD23, WRAPPERS, CALLERS

def test_wrapper_count_and_callers():
    assert len(WRAPPERS) == 4
    assert set(CALLERS) == set(WRAPPERS.values())

def test_table23_address():
    assert RECORD_SIZE == 0x14
    assert RECORD23 == 0x20008EFC
    assert RECORD23 + RECORD_SIZE - 1 == 0x20008F0F
