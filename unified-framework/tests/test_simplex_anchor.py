"""
Unit tests for simplex_anchor module.

Validates:
- Component factors are correct
- Enhancement calculations work properly
- No fallback detection works
- Determinism and reproducibility
"""

import pytest
from src.z5d.simplex_anchor import (
    SimplexAnchorConfig,
    apply_anchor_to_density,
    apply_anchor_to_candidate_count,
    create_z5d_state,
    validate_no_fallback,
    get_expected_improvement,
)


class TestSimplexAnchorConfig:
    """Test SimplexAnchorConfig class."""
    
    def test_component_factors(self):
        """Verify individual component factors."""
        assert abs(SimplexAnchorConfig.A4_FACTOR - 1.041667) < 1e-6
        assert abs(SimplexAnchorConfig.EULER_FACTOR - 1.02) < 1e-6
        assert abs(SimplexAnchorConfig.SELF_DUAL_FACTOR - 1.015) < 1e-6
    
    def test_product_factor(self):
        """Verify product factor E = 1.078437."""
        expected = 1.041667 * 1.02 * 1.015
        assert abs(SimplexAnchorConfig.PRODUCT_FACTOR - expected) < 1e-6
        # Verify against stated value
        assert abs(SimplexAnchorConfig.PRODUCT_FACTOR - 1.078437) < 0.001
    
    def test_get_factor_baseline(self):
        """Baseline should return 1.0."""
        assert SimplexAnchorConfig.get_factor("baseline") == 1.0
    
    def test_get_factor_simplex(self):
        """Simplex should return product factor."""
        factor = SimplexAnchorConfig.get_factor("simplex")
        assert abs(factor - SimplexAnchorConfig.PRODUCT_FACTOR) < 1e-9
    
    def test_get_factor_components(self):
        """Individual conditions should return their component."""
        assert abs(
            SimplexAnchorConfig.get_factor("A4") - SimplexAnchorConfig.A4_FACTOR
        ) < 1e-9
        assert abs(
            SimplexAnchorConfig.get_factor("euler") - SimplexAnchorConfig.EULER_FACTOR
        ) < 1e-9
        assert abs(
            SimplexAnchorConfig.get_factor("self_dual") - SimplexAnchorConfig.SELF_DUAL_FACTOR
        ) < 1e-9
    
    def test_get_factor_invalid(self):
        """Invalid condition should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown condition"):
            SimplexAnchorConfig.get_factor("invalid")
    
    def test_get_components_baseline(self):
        """Baseline should have all 1.0 components."""
        components = SimplexAnchorConfig.get_components("baseline")
        assert components["A4_factor"] == 1.0
        assert components["euler_factor"] == 1.0
        assert components["self_dual_factor"] == 1.0
    
    def test_get_components_simplex(self):
        """Simplex should have all component factors."""
        components = SimplexAnchorConfig.get_components("simplex")
        assert abs(components["A4_factor"] - SimplexAnchorConfig.A4_FACTOR) < 1e-9
        assert abs(components["euler_factor"] - SimplexAnchorConfig.EULER_FACTOR) < 1e-9
        assert abs(components["self_dual_factor"] - SimplexAnchorConfig.SELF_DUAL_FACTOR) < 1e-9
    
    def test_get_components_ablation(self):
        """Ablation conditions should have only one component active."""
        # A4 only
        comp = SimplexAnchorConfig.get_components("A4")
        assert abs(comp["A4_factor"] - SimplexAnchorConfig.A4_FACTOR) < 1e-9
        assert comp["euler_factor"] == 1.0
        assert comp["self_dual_factor"] == 1.0
        
        # Euler only
        comp = SimplexAnchorConfig.get_components("euler")
        assert comp["A4_factor"] == 1.0
        assert abs(comp["euler_factor"] - SimplexAnchorConfig.EULER_FACTOR) < 1e-9
        assert comp["self_dual_factor"] == 1.0
        
        # Self-dual only
        comp = SimplexAnchorConfig.get_components("self_dual")
        assert comp["A4_factor"] == 1.0
        assert comp["euler_factor"] == 1.0
        assert abs(comp["self_dual_factor"] - SimplexAnchorConfig.SELF_DUAL_FACTOR) < 1e-9


class TestDensityApplication:
    """Test density enhancement application."""
    
    def test_baseline_no_change(self):
        """Baseline should not change density."""
        base = 0.10
        result = apply_anchor_to_density(base, "baseline")
        assert result == base
    
    def test_simplex_enhancement(self):
        """Simplex should enhance density by E factor."""
        base = 0.10
        result = apply_anchor_to_density(base, "simplex")
        expected = base * SimplexAnchorConfig.PRODUCT_FACTOR
        assert abs(result - expected) < 1e-9
    
    def test_component_enhancement(self):
        """Component conditions should apply their factor."""
        base = 0.10
        
        result_a4 = apply_anchor_to_density(base, "A4")
        assert abs(result_a4 - base * SimplexAnchorConfig.A4_FACTOR) < 1e-9
        
        result_euler = apply_anchor_to_density(base, "euler")
        assert abs(result_euler - base * SimplexAnchorConfig.EULER_FACTOR) < 1e-9
        
        result_self = apply_anchor_to_density(base, "self_dual")
        assert abs(result_self - base * SimplexAnchorConfig.SELF_DUAL_FACTOR) < 1e-9


class TestCandidateCountApplication:
    """Test candidate count reduction."""
    
    def test_baseline_no_change(self):
        """Baseline should not change candidate count."""
        base = 354.89
        result = apply_anchor_to_candidate_count(base, "baseline")
        assert result == base
    
    def test_simplex_reduction(self):
        """Simplex should reduce candidates (inverse of factor)."""
        base = 354.89
        result = apply_anchor_to_candidate_count(base, "simplex")
        expected = base / SimplexAnchorConfig.PRODUCT_FACTOR
        assert abs(result - expected) < 1e-6
        # Should be ~329.09 for 1024-bit
        assert abs(result - 329.09) < 1.0
    
    def test_2048bit_reduction(self):
        """Test 2048-bit candidate reduction."""
        base = 709.78
        result = apply_anchor_to_candidate_count(base, "simplex")
        expected = base / SimplexAnchorConfig.PRODUCT_FACTOR
        assert abs(result - expected) < 1e-6
        # Should be ~658.18
        assert abs(result - 658.18) < 1.0


class TestZ5DStateCreation:
    """Test Z5D state dictionary creation."""
    
    def test_baseline_state(self):
        """Baseline state should have factor 1.0."""
        state = create_z5d_state("baseline")
        assert state["condition"] == "baseline"
        assert state["enhancement_factor"] == 1.0
        assert state["components"]["A4_factor"] == 1.0
    
    def test_simplex_state(self):
        """Simplex state should have product factor."""
        state = create_z5d_state("simplex")
        assert state["condition"] == "simplex"
        assert abs(state["enhancement_factor"] - SimplexAnchorConfig.PRODUCT_FACTOR) < 1e-9
    
    def test_additional_params(self):
        """Additional parameters should be included."""
        state = create_z5d_state("simplex", {"seed": 1337, "bit_length": 1024})
        assert state["seed"] == 1337
        assert state["bit_length"] == 1024
    
    def test_state_completeness(self):
        """State should contain all required keys."""
        state = create_z5d_state("simplex")
        assert "condition" in state
        assert "enhancement_factor" in state
        assert "components" in state
        assert "A4_factor" in state["components"]
        assert "euler_factor" in state["components"]
        assert "self_dual_factor" in state["components"]


class TestFallbackValidation:
    """Test no-fallback enforcement."""
    
    def test_clean_state_passes(self):
        """State without fallback keys should pass."""
        state = create_z5d_state("simplex")
        validate_no_fallback(state)  # Should not raise
    
    def test_fallback_key_raises(self):
        """State with fallback key should raise."""
        state = {"fallback_enabled": True}
        with pytest.raises(ValueError, match="Forbidden fallback key"):
            validate_no_fallback(state)
    
    def test_hybrid_key_raises(self):
        """State with hybrid key should raise."""
        state = {"hybrid_mode": "auto"}
        with pytest.raises(ValueError, match="Forbidden fallback key"):
            validate_no_fallback(state)
    
    def test_revert_key_raises(self):
        """State with revert key should raise."""
        state = {"revert_to_baseline": False}
        with pytest.raises(ValueError, match="Forbidden fallback key"):
            validate_no_fallback(state)


class TestExpectedImprovement:
    """Test expected improvement calculations."""
    
    def test_density_improvement_baseline(self):
        """Baseline should have 0% improvement."""
        improvement = get_expected_improvement("baseline", "density")
        assert improvement == 0.0
    
    def test_density_improvement_simplex(self):
        """Simplex should have ~7.84% density improvement."""
        improvement = get_expected_improvement("simplex", "density")
        expected = (SimplexAnchorConfig.PRODUCT_FACTOR - 1.0) * 100.0
        assert abs(improvement - expected) < 1e-6
        assert abs(improvement - 7.84) < 0.1
    
    def test_candidates_reduction_simplex(self):
        """Simplex should have ~7.27% candidate reduction."""
        improvement = get_expected_improvement("simplex", "candidates")
        # Should be negative (reduction)
        assert improvement < 0
        assert abs(improvement - (-7.27)) < 0.1
    
    def test_ttf_reduction_simplex(self):
        """TTF should have same reduction as candidates."""
        improvement_ttf = get_expected_improvement("simplex", "ttf")
        improvement_cand = get_expected_improvement("simplex", "candidates")
        assert abs(improvement_ttf - improvement_cand) < 1e-9
    
    def test_invalid_metric(self):
        """Invalid metric should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown metric"):
            get_expected_improvement("baseline", "invalid")


class TestDeterminism:
    """Test determinism and reproducibility."""
    
    def test_factor_determinism(self):
        """Factors should be deterministic across calls."""
        factors1 = [SimplexAnchorConfig.get_factor(c) for c in ["baseline", "simplex", "A4"]]
        factors2 = [SimplexAnchorConfig.get_factor(c) for c in ["baseline", "simplex", "A4"]]
        assert factors1 == factors2
    
    def test_state_determinism(self):
        """States should be deterministic for same inputs."""
        state1 = create_z5d_state("simplex", {"seed": 42})
        state2 = create_z5d_state("simplex", {"seed": 42})
        assert state1 == state2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
