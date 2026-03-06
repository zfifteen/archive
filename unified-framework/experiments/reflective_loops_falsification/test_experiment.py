"""
Test suite for reflective loops falsification experiment.

Ensures the experiment produces valid, reproducible results.
"""

import json
import sys
import os
from pathlib import Path

# Add experiment directory to path
sys.path.insert(0, str(Path(__file__).parent))

import experiment
import analyze_results


def test_experiment_runs():
    """Test that experiment runs without errors."""
    results = experiment.run_experiment(seed=42, n_trials=5)
    assert results is not None
    assert 'metadata' in results
    assert 'results' in results
    assert 'statistics' in results
    print("✓ Experiment runs successfully")


def test_experiment_reproducibility():
    """Test that same seed produces same results."""
    results1 = experiment.run_experiment(seed=12345, n_trials=5)
    results2 = experiment.run_experiment(seed=12345, n_trials=5)
    
    # Check that statistics match
    stats1 = results1['statistics']
    stats2 = results2['statistics']
    
    # Overall coherence should be identical
    coh1 = stats1['overall']['control']['mean_coherence']
    coh2 = stats2['overall']['control']['mean_coherence']
    assert abs(coh1 - coh2) < 1e-10, f"Reproducibility failed: {coh1} != {coh2}"
    
    print("✓ Experiment is reproducible with same seed")


def test_reflective_shows_improvement():
    """Test that reflective loops show improvement over control."""
    results = experiment.run_experiment(seed=42, n_trials=50)
    stats = results['statistics']
    
    # Overall improvements should be positive
    assert stats['effect_sizes']['coherence_improvement'] > 0, \
        "Reflective loops should improve coherence"
    assert stats['effect_sizes']['alignment_improvement'] > 0, \
        "Reflective loops should improve alignment"
    assert stats['effect_sizes']['resolution_improvement'] > 0, \
        "Reflective loops should improve resolution"
    
    print("✓ Reflective loops show expected improvements")


def test_graduated_protection_effect():
    """Test that protection effect increases with contradiction severity."""
    results = experiment.run_experiment(seed=42, n_trials=50)
    stats = results['statistics']
    by_level = stats['by_contradiction_level']
    
    # Get coherence improvements by level
    improvements = {}
    for level in ['none', 'mild', 'moderate', 'severe']:
        if level in by_level:
            improvements[level] = by_level[level]['improvement']['coherence_delta']
    
    # Verify graduated effect: severe > moderate > mild
    if 'severe' in improvements and 'moderate' in improvements:
        assert improvements['severe'] > improvements['moderate'], \
            "Severe contradictions should show larger improvement"
    
    if 'moderate' in improvements and 'mild' in improvements:
        assert improvements['moderate'] > improvements['mild'], \
            "Moderate contradictions should show larger improvement than mild"
    
    print("✓ Graduated protection effect verified")


def test_scenario_creation():
    """Test that scenarios are created correctly."""
    scenarios = experiment.create_test_scenarios()
    
    assert len(scenarios) > 0, "Should create scenarios"
    
    # Check we have scenarios at each level
    levels = set(s.contradiction_level for s in scenarios)
    assert 'none' in levels or 'mild' in levels, "Should have baseline scenarios"
    assert 'moderate' in levels or 'severe' in levels, "Should have contradiction scenarios"
    
    # Check each scenario has required fields
    for scenario in scenarios:
        assert scenario.name, "Scenario must have name"
        assert scenario.instructions, "Scenario must have instructions"
        assert scenario.query, "Scenario must have query"
        assert scenario.expected_behavior, "Scenario must have expected behavior"
        assert scenario.contradiction_level in ['none', 'mild', 'moderate', 'severe']
    
    print(f"✓ Created {len(scenarios)} valid scenarios")


def test_statistical_calculations():
    """Test that statistical calculations are valid."""
    results = experiment.run_experiment(seed=42, n_trials=10)
    stats = results['statistics']
    
    # Check overall statistics exist
    assert 'overall' in stats
    assert 'control' in stats['overall']
    assert 'reflective' in stats['overall']
    
    # Check values are in valid ranges
    for condition in ['control', 'reflective']:
        cond_stats = stats['overall'][condition]
        assert 0 <= cond_stats['mean_coherence'] <= 1
        assert 0 <= cond_stats['mean_alignment'] <= 1
        assert 0 <= cond_stats['resolution_rate'] <= 1
        assert cond_stats['n'] > 0
    
    print("✓ Statistical calculations are valid")


def test_analysis_loads_results():
    """Test that analysis script can load results."""
    # Generate test results
    results = experiment.run_experiment(seed=42, n_trials=5)
    
    # Save to temp file
    test_file = '/tmp/test_results.json'
    with open(test_file, 'w') as f:
        json.dump(results, f)
    
    # Load with analysis
    loaded = analyze_results.load_results(test_file)
    assert loaded is not None
    assert loaded['metadata']['seed'] == 42
    
    # Clean up
    os.remove(test_file)
    
    print("✓ Analysis script loads results correctly")


def run_all_tests():
    """Run all tests and report results."""
    tests = [
        ("Experiment Runs", test_experiment_runs),
        ("Reproducibility", test_experiment_reproducibility),
        ("Reflective Improvement", test_reflective_shows_improvement),
        ("Graduated Protection", test_graduated_protection_effect),
        ("Scenario Creation", test_scenario_creation),
        ("Statistical Calculations", test_statistical_calculations),
        ("Analysis Loads Results", test_analysis_loads_results),
    ]
    
    print("\n" + "=" * 70)
    print("Running Reflective Loops Experiment Tests")
    print("=" * 70 + "\n")
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ {name} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {name} ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
