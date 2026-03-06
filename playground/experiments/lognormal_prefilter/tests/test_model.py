"""
Tests for the model layer.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from model import Band, ModelStore, create_default_model_store


def test_band_creation():
    """Test that Band objects can be created."""
    band = Band(
        p_min=100000,
        p_max=1000000,
        shape=1.5,
        scale=0.0001,
        min_gap=2.0,
        max_gap=1000.0
    )
    
    assert band.p_min == 100000
    assert band.p_max == 1000000
    assert band.shape == 1.5
    assert band.scale == 0.0001
    print("✓ Band creation works")


def test_model_store_exact_match():
    """Test get_band_for_p with exact matches."""
    bands = [
        Band(p_min=100, p_max=1000, shape=1.0, scale=0.1),
        Band(p_min=1000, p_max=10000, shape=1.2, scale=0.01),
        Band(p_min=10000, p_max=100000, shape=1.4, scale=0.001),
    ]
    store = ModelStore(bands)
    
    # Test exact matches
    band = store.get_band_for_p(500)
    assert band is not None
    assert band.p_min == 100
    assert band.p_max == 1000
    
    band = store.get_band_for_p(5000)
    assert band is not None
    assert band.p_min == 1000
    assert band.p_max == 10000
    
    band = store.get_band_for_p(50000)
    assert band is not None
    assert band.p_min == 10000
    assert band.p_max == 100000
    
    print("✓ ModelStore exact matches work")


def test_model_store_no_match():
    """Test get_band_for_p with no matches."""
    bands = [
        Band(p_min=100, p_max=1000, shape=1.0, scale=0.1),
        Band(p_min=1000, p_max=10000, shape=1.2, scale=0.01),
    ]
    store = ModelStore(bands)
    
    # Test outside range
    band = store.get_band_for_p(50)
    assert band is None
    
    band = store.get_band_for_p(20000)
    assert band is None
    
    print("✓ ModelStore returns None for out-of-range values")


def test_model_store_closest_band():
    """Test get_closest_band for values outside known ranges."""
    bands = [
        Band(p_min=100, p_max=1000, shape=1.0, scale=0.1),
        Band(p_min=1000, p_max=10000, shape=1.2, scale=0.01),
        Band(p_min=10000, p_max=100000, shape=1.4, scale=0.001),
    ]
    store = ModelStore(bands)
    
    # Test below range - should get first band
    band = store.get_closest_band(50)
    assert band.p_min == 100
    assert band.p_max == 1000
    
    # Test above range - should get last band
    band = store.get_closest_band(200000)
    assert band.p_min == 10000
    assert band.p_max == 100000
    
    # Test within range - should get exact match
    band = store.get_closest_band(5000)
    assert band.p_min == 1000
    assert band.p_max == 10000
    
    print("✓ ModelStore get_closest_band works")


def test_default_model_store():
    """Test that the default model store has correct bands."""
    store = create_default_model_store()
    
    # Should have 4 bands
    assert len(store.bands) == 4
    
    # Test band ranges
    band1 = store.get_band_for_p(5 * 10**5)
    assert band1 is not None
    assert band1.p_min == 10**5
    assert band1.p_max == 10**6
    
    band2 = store.get_band_for_p(5 * 10**6)
    assert band2 is not None
    assert band2.p_min == 10**6
    assert band2.p_max == 10**7
    
    band3 = store.get_band_for_p(5 * 10**7)
    assert band3 is not None
    assert band3.p_min == 10**7
    assert band3.p_max == 10**8
    
    band4 = store.get_band_for_p(5 * 10**8)
    assert band4 is not None
    assert band4.p_min == 10**8
    assert band4.p_max == 10**9
    
    # Check that parameters are reasonable
    for band in store.bands:
        assert band.shape > 0
        assert band.scale > 0
        assert band.min_gap is not None
        assert band.max_gap is not None
        assert band.min_gap < band.max_gap
    
    print("✓ Default model store has correct structure")


def run_all_tests():
    """Run all model tests."""
    test_band_creation()
    test_model_store_exact_match()
    test_model_store_no_match()
    test_model_store_closest_band()
    test_default_model_store()
    print("\n✓ All model tests passed!")


if __name__ == "__main__":
    run_all_tests()
