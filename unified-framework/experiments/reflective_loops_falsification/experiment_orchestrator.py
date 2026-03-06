"""
Experiment Orchestrator for Real LLM Reflective Loops Testing

This orchestrates the full experiment:
- 10 scenarios (from contradiction JSON files)
- 4 contradiction levels (none, mild, moderate, severe)
- 2 conditions (control vs reflective)
- 50 trials per scenario

Total: 10 × 2 × 50 = 1,000 LLM calls + 1,000 evaluation calls
"""

import json
import os
import time
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from real_llm_runner import RealLLMRunner, LLMConfig, create_runner_from_env, load_prompt
from evaluate_response import ResponseEvaluator, create_evaluator_from_env, EvaluationScores

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ExperimentConfig:
    """Configuration for the experiment."""
    # Model configurations
    test_provider: str = "openai"  # Provider for models being tested
    test_model: str = "gpt-4o"
    judge_provider: str = "openai"  # Provider for judge model
    judge_model: str = "gpt-4o"
    
    # Experiment parameters
    n_trials: int = 50  # Trials per scenario
    
    # Paths
    prompts_dir: str = "prompts"
    contradictions_dir: str = "contradictions"
    results_dir: str = "real_experiment_results"
    
    # Rate limiting
    calls_per_minute: int = 60
    delay_between_calls: float = 1.0  # seconds


@dataclass
class TrialResult:
    """Result from a single trial."""
    scenario_id: str
    scenario_name: str
    trial_number: int
    prompt_type: str  # 'control' or 'reflective'
    contradiction_level: str
    
    # Model response
    response_text: str
    response_error: Optional[str]
    response_latency_ms: float
    
    # Evaluation scores
    coherence_score: float
    alignment_score: float
    resolved_coherently: bool
    evaluation_explanation: str
    detected_contradictions: List[str]
    
    # Metadata
    timestamp: str
    model: str
    judge_model: str


class ExperimentOrchestrator:
    """Orchestrates the full reflective loops experiment with real LLMs."""
    
    def __init__(self, config: ExperimentConfig):
        """Initialize orchestrator with configuration."""
        self.config = config
        
        # Create results directory
        Path(config.results_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize runners
        logger.info(f"Initializing test runner: {config.test_provider}/{config.test_model}")
        self.test_runner = create_runner_from_env(
            provider=config.test_provider,
            model=config.test_model
        )
        
        logger.info(f"Initializing judge: {config.judge_provider}/{config.judge_model}")
        self.evaluator = create_evaluator_from_env(
            provider=config.judge_provider,
            model=config.judge_model
        )
        
        # Load prompts
        self.standard_prompt = load_prompt(
            os.path.join(config.prompts_dir, "standard", "system_prompt.txt")
        )
        self.reflective_prompt = load_prompt(
            os.path.join(config.prompts_dir, "reflective_loop_v1.txt")
        )
        
        # Load scenarios
        self.scenarios = self._load_scenarios()
        logger.info(f"Loaded {len(self.scenarios)} scenarios")
        
        # Rate limiting
        self.last_call_time = 0
    
    def _load_scenarios(self) -> List[Dict]:
        """Load all scenarios from contradiction JSON files."""
        scenarios = []
        
        contradiction_files = [
            "none.json",
            "mild.json",
            "moderate.json",
            "severe.json"
        ]
        
        for filename in contradiction_files:
            filepath = os.path.join(self.config.contradictions_dir, filename)
            if not os.path.exists(filepath):
                logger.warning(f"Contradiction file not found: {filepath}")
                continue
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            for scenario in data["scenarios"]:
                scenario["contradiction_level"] = data["contradiction_level"]
                scenarios.append(scenario)
        
        return scenarios
    
    def _rate_limit(self):
        """Implement rate limiting between API calls."""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.config.delay_between_calls:
            time.sleep(self.config.delay_between_calls - elapsed)
        self.last_call_time = time.time()
    
    def run_single_trial(
        self,
        scenario: Dict,
        trial_number: int,
        prompt_type: str
    ) -> TrialResult:
        """
        Run a single trial: call LLM and evaluate response.
        
        Args:
            scenario: Scenario dict from contradiction JSON
            trial_number: Trial number (1 to n_trials)
            prompt_type: 'control' or 'reflective'
        
        Returns:
            TrialResult with response and evaluation
        """
        # Select prompt
        system_prompt = (
            self.standard_prompt if prompt_type == "control"
            else self.reflective_prompt
        )
        
        # Call LLM
        self._rate_limit()
        logger.info(
            f"Trial {trial_number}: {scenario['name']} ({prompt_type})"
        )
        
        response = self.test_runner.call_llm(
            system_prompt=system_prompt,
            user_message=scenario["query"],
            additional_instructions=scenario["instructions"]
        )
        
        # Evaluate response
        self._rate_limit()
        if response.error:
            # Use default low scores if LLM call failed
            scores = EvaluationScores(
                coherence_score=0.0,
                alignment_score=0.0,
                resolved_coherently=False,
                explanation=f"LLM call failed: {response.error}",
                detected_contradictions=[]
            )
        else:
            scores = self.evaluator.evaluate_response(
                instructions=scenario["instructions"],
                query=scenario["query"],
                response=response.text,
                expected_behavior=scenario["expected_behavior"],
                contradiction_level=scenario["contradiction_level"]
            )
        
        # Create result
        result = TrialResult(
            scenario_id=scenario["id"],
            scenario_name=scenario["name"],
            trial_number=trial_number,
            prompt_type=prompt_type,
            contradiction_level=scenario["contradiction_level"],
            response_text=response.text,
            response_error=response.error,
            response_latency_ms=response.latency_ms or 0.0,
            coherence_score=scores.coherence_score,
            alignment_score=scores.alignment_score,
            resolved_coherently=scores.resolved_coherently,
            evaluation_explanation=scores.explanation,
            detected_contradictions=scores.detected_contradictions,
            timestamp=datetime.now().isoformat(),
            model=self.config.test_model,
            judge_model=self.config.judge_model
        )
        
        return result
    
    def run_experiment(self) -> Dict:
        """
        Run the full experiment.
        
        Returns:
            Dictionary with all results and metadata
        """
        results = {
            "metadata": {
                "test_model": self.config.test_model,
                "test_provider": self.config.test_provider,
                "judge_model": self.config.judge_model,
                "judge_provider": self.config.judge_provider,
                "n_trials": self.config.n_trials,
                "n_scenarios": len(self.scenarios),
                "start_time": datetime.now().isoformat(),
            },
            "config": asdict(self.config),
            "scenarios": self.scenarios,
            "trials": []
        }
        
        total_trials = len(self.scenarios) * 2 * self.config.n_trials
        completed = 0
        
        logger.info(f"Starting experiment: {total_trials} total trials")
        logger.info(f"Estimated time: {total_trials * 2 * self.config.delay_between_calls / 60:.1f} minutes")
        
        try:
            # Run trials for each scenario
            for scenario in self.scenarios:
                logger.info(f"\nScenario: {scenario['name']} ({scenario['contradiction_level']})")
                
                for trial_num in range(1, self.config.n_trials + 1):
                    # Control condition
                    result_control = self.run_single_trial(
                        scenario=scenario,
                        trial_number=trial_num,
                        prompt_type="control"
                    )
                    results["trials"].append(asdict(result_control))
                    completed += 1
                    
                    # Reflective condition
                    result_reflective = self.run_single_trial(
                        scenario=scenario,
                        trial_number=trial_num,
                        prompt_type="reflective"
                    )
                    results["trials"].append(asdict(result_reflective))
                    completed += 1
                    
                    # Progress update
                    if completed % 10 == 0:
                        progress = 100 * completed / total_trials
                        logger.info(f"Progress: {completed}/{total_trials} ({progress:.1f}%)")
                    
                    # Save intermediate results every 20 trials
                    if completed % 20 == 0:
                        self._save_results(results, suffix="_intermediate")
        
        except KeyboardInterrupt:
            logger.warning("Experiment interrupted by user")
        except Exception as e:
            logger.error(f"Experiment failed: {e}", exc_info=True)
        
        # Add end time
        results["metadata"]["end_time"] = datetime.now().isoformat()
        results["metadata"]["completed_trials"] = completed
        
        # Save final results
        self._save_results(results)
        
        logger.info(f"\nExperiment complete: {completed}/{total_trials} trials")
        return results
    
    def _save_results(self, results: Dict, suffix: str = ""):
        """Save results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"experiment_results{suffix}_{timestamp}.json"
        filepath = os.path.join(self.config.results_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to: {filepath}")


def run_full_experiment(
    test_provider: str = "openai",
    test_model: str = "gpt-4o",
    judge_provider: str = "openai",
    judge_model: str = "gpt-4o",
    n_trials: int = 50
) -> Dict:
    """
    Run the full experiment with specified configuration.
    
    Args:
        test_provider: Provider for models being tested
        test_model: Model being tested
        judge_provider: Provider for judge model
        judge_model: Model used as judge
        n_trials: Number of trials per scenario
    
    Returns:
        Complete results dictionary
    """
    config = ExperimentConfig(
        test_provider=test_provider,
        test_model=test_model,
        judge_provider=judge_provider,
        judge_model=judge_model,
        n_trials=n_trials
    )
    
    orchestrator = ExperimentOrchestrator(config)
    return orchestrator.run_experiment()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run reflective loops experiment with real LLMs"
    )
    parser.add_argument(
        "--test-provider",
        default="openai",
        choices=["openai", "anthropic", "xai"],
        help="Provider for model being tested"
    )
    parser.add_argument(
        "--test-model",
        default="gpt-4o",
        help="Model being tested (e.g., gpt-4o, claude-3-5-sonnet-20241022, grok-2-1212)"
    )
    parser.add_argument(
        "--judge-provider",
        default="openai",
        choices=["openai", "anthropic", "xai"],
        help="Provider for judge model"
    )
    parser.add_argument(
        "--judge-model",
        default="gpt-4o",
        help="Model used as judge"
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=50,
        help="Number of trials per scenario"
    )
    parser.add_argument(
        "--quick-test",
        action="store_true",
        help="Run quick test with only 2 trials per scenario"
    )
    
    args = parser.parse_args()
    
    n_trials = 2 if args.quick_test else args.trials
    
    print("=" * 70)
    print("REFLECTIVE LOOPS FALSIFICATION EXPERIMENT")
    print("Real LLM Validation")
    print("=" * 70)
    print(f"Test Model: {args.test_provider}/{args.test_model}")
    print(f"Judge Model: {args.judge_provider}/{args.judge_model}")
    print(f"Trials per scenario: {n_trials}")
    print("=" * 70)
    print()
    
    results = run_full_experiment(
        test_provider=args.test_provider,
        test_model=args.test_model,
        judge_provider=args.judge_provider,
        judge_model=args.judge_model,
        n_trials=n_trials
    )
    
    print("\n" + "=" * 70)
    print("EXPERIMENT COMPLETE")
    print("=" * 70)
    print(f"Total trials completed: {results['metadata']['completed_trials']}")
    print(f"Results saved to: {ExperimentConfig().results_dir}")
    print("\nRun analyze_results.py to generate findings report.")
