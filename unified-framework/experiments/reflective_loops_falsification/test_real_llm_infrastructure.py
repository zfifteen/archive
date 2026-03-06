"""
Tests for Real LLM Validation Infrastructure

Tests the core components without making actual API calls.
"""

import json
import os
import sys
from pathlib import Path

# Test imports
def test_imports():
    """Test that all modules can be imported."""
    try:
        import real_llm_runner
        import evaluate_response
        import experiment_orchestrator
        print("✓ All modules import successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_prompt_files_exist():
    """Test that prompt files are present."""
    prompts_dir = Path("prompts")
    
    standard_prompt = prompts_dir / "standard" / "system_prompt.txt"
    reflective_prompt = prompts_dir / "reflective_loop_v1.txt"
    
    if not standard_prompt.exists():
        print(f"✗ Missing standard prompt: {standard_prompt}")
        return False
    
    if not reflective_prompt.exists():
        print(f"✗ Missing reflective prompt: {reflective_prompt}")
        return False
    
    # Verify content
    with open(standard_prompt, 'r') as f:
        standard_content = f.read()
    
    with open(reflective_prompt, 'r') as f:
        reflective_content = f.read()
    
    if len(standard_content) < 100:
        print(f"✗ Standard prompt too short: {len(standard_content)} chars")
        return False
    
    if len(reflective_content) < 500:
        print(f"✗ Reflective prompt too short: {len(reflective_content)} chars")
        return False
    
    # Check for key reflective loop stages
    required_stages = ["MIRROR", "MAP", "PATTERN-HUNT", "COUNTERFRAME", "INSIGHT-SEED", "SYNTHESIS"]
    for stage in required_stages:
        if stage not in reflective_content:
            print(f"✗ Missing reflective stage: {stage}")
            return False
    
    print("✓ Prompt files exist and contain expected content")
    return True


def test_contradiction_files_exist():
    """Test that contradiction JSON files are present and valid."""
    contradictions_dir = Path("contradictions")
    
    required_files = ["none.json", "mild.json", "moderate.json", "severe.json"]
    
    for filename in required_files:
        filepath = contradictions_dir / filename
        if not filepath.exists():
            print(f"✗ Missing contradiction file: {filepath}")
            return False
        
        # Validate JSON structure
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            if "contradiction_level" not in data:
                print(f"✗ Missing 'contradiction_level' in {filename}")
                return False
            
            if "scenarios" not in data:
                print(f"✗ Missing 'scenarios' in {filename}")
                return False
            
            if not isinstance(data["scenarios"], list):
                print(f"✗ 'scenarios' is not a list in {filename}")
                return False
            
            # Validate each scenario
            for scenario in data["scenarios"]:
                required_keys = ["id", "name", "instructions", "query", "expected_behavior"]
                for key in required_keys:
                    if key not in scenario:
                        print(f"✗ Scenario missing '{key}' in {filename}")
                        return False
            
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON in {filename}: {e}")
            return False
    
    print("✓ All contradiction files exist and are valid JSON")
    return True


def test_llm_config_creation():
    """Test LLMConfig creation."""
    from real_llm_runner import LLMConfig
    
    try:
        config = LLMConfig(
            provider="openai",
            model="gpt-4o",
            api_key="test-key",
            max_tokens=1000,
            temperature=0.7
        )
        
        assert config.provider == "openai"
        assert config.model == "gpt-4o"
        assert config.api_key == "test-key"
        
        print("✓ LLMConfig creation works")
        return True
    except Exception as e:
        print(f"✗ LLMConfig creation failed: {e}")
        return False


def test_runner_initialization_without_api_key():
    """Test that runner can be initialized without API key (will warn but not fail)."""
    from real_llm_runner import RealLLMRunner, LLMConfig
    
    try:
        config = LLMConfig(
            provider="openai",
            model="gpt-4o"
            # No API key - should work but log warning
        )
        
        # This should not fail even without API key
        runner = RealLLMRunner(config)
        
        print("✓ Runner initialization works (without API key)")
        return True
    except Exception as e:
        print(f"✗ Runner initialization failed: {e}")
        return False


def test_evaluation_prompt_exists():
    """Test that evaluation prompt is defined."""
    from evaluate_response import EVALUATION_PROMPT
    
    if not EVALUATION_PROMPT:
        print("✗ EVALUATION_PROMPT is empty")
        return False
    
    if len(EVALUATION_PROMPT) < 500:
        print(f"✗ EVALUATION_PROMPT too short: {len(EVALUATION_PROMPT)} chars")
        return False
    
    # Check for key components
    required_terms = ["coherence", "alignment", "resolved", "JSON"]
    for term in required_terms:
        if term.lower() not in EVALUATION_PROMPT.lower():
            print(f"✗ EVALUATION_PROMPT missing term: {term}")
            return False
    
    print("✓ Evaluation prompt exists and looks valid")
    return True


def test_experiment_config_creation():
    """Test ExperimentConfig creation."""
    from experiment_orchestrator import ExperimentConfig
    
    try:
        config = ExperimentConfig(
            test_provider="openai",
            test_model="gpt-4o",
            judge_provider="openai",
            judge_model="gpt-4o",
            n_trials=5
        )
        
        assert config.test_provider == "openai"
        assert config.n_trials == 5
        
        print("✓ ExperimentConfig creation works")
        return True
    except Exception as e:
        print(f"✗ ExperimentConfig creation failed: {e}")
        return False


def test_analyze_results_handles_simulation():
    """Test that analyze_results can load existing simulation results."""
    from analyze_results import load_results
    
    try:
        # Load existing simulation results
        results = load_results("experiment_results.json")
        
        if "_format" not in results:
            print("✗ Results missing _format field")
            return False
        
        if results["_format"] != "simulation":
            print(f"✗ Unexpected format: {results['_format']}")
            return False
        
        if "statistics" not in results:
            print("✗ Results missing statistics")
            return False
        
        print("✓ analyze_results handles simulation format")
        return True
    except Exception as e:
        print(f"✗ Failed to load simulation results: {e}")
        return False


def test_scenario_count():
    """Test that we have the expected number of scenarios."""
    contradictions_dir = Path("contradictions")
    
    total_scenarios = 0
    for filename in ["none.json", "mild.json", "moderate.json", "severe.json"]:
        filepath = contradictions_dir / filename
        with open(filepath, 'r') as f:
            data = json.load(f)
        total_scenarios += len(data["scenarios"])
    
    if total_scenarios < 10:
        print(f"✗ Expected at least 10 scenarios, found {total_scenarios}")
        return False
    
    print(f"✓ Found {total_scenarios} scenarios across all contradiction levels")
    return True


def run_all_tests():
    """Run all tests and report results."""
    print("=" * 70)
    print("Running Real LLM Validation Infrastructure Tests")
    print("=" * 70)
    print()
    
    tests = [
        ("Module imports", test_imports),
        ("Prompt files", test_prompt_files_exist),
        ("Contradiction files", test_contradiction_files_exist),
        ("LLMConfig creation", test_llm_config_creation),
        ("Runner initialization", test_runner_initialization_without_api_key),
        ("Evaluation prompt", test_evaluation_prompt_exists),
        ("ExperimentConfig creation", test_experiment_config_creation),
        ("Analyze simulation results", test_analyze_results_handles_simulation),
        ("Scenario count", test_scenario_count),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test '{test_name}' raised exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()
    
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
