"""
Bootstrap Validation Module
===========================

Bootstrap and resampling methods for robust statistical validation
of Z Framework empirical results.
"""

import numpy as np
import scipy.stats as stats
from sklearn.utils import resample
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.metrics import accuracy_score, precision_score, recall_score
import warnings

def bootstrap_confidence_intervals(data, statistic_func, confidence_level=0.95, 
                                 n_bootstrap=1000, method='percentile'):
    """
    Compute bootstrap confidence intervals for any statistic.
    
    Args:
        data: Input data array or arrays (can be tuple for multi-sample statistics)
        statistic_func: Function that computes the statistic of interest
        confidence_level: Confidence level (default 0.95 for 95% CI)
        n_bootstrap: Number of bootstrap samples
        method: CI method ('percentile', 'bias_corrected', 'accelerated')
        
    Returns:
        dict: Bootstrap confidence interval results
    """
    # Handle single array vs multiple arrays
    if isinstance(data, tuple):
        # Multiple data arrays
        original_stat = statistic_func(*data)
        bootstrap_stats = []
        
        for _ in range(n_bootstrap):
            # Bootstrap sample each array
            boot_samples = []
            for arr in data:
                boot_indices = np.random.choice(len(arr), len(arr), replace=True)
                boot_samples.append(np.array(arr)[boot_indices])
            
            try:
                boot_stat = statistic_func(*boot_samples)
                bootstrap_stats.append(boot_stat)
            except:
                continue  # Skip failed bootstrap samples
                
    else:
        # Single data array
        data = np.array(data)
        original_stat = statistic_func(data)
        bootstrap_stats = []
        
        for _ in range(n_bootstrap):
            boot_indices = np.random.choice(len(data), len(data), replace=True)
            boot_sample = data[boot_indices]
            
            try:
                boot_stat = statistic_func(boot_sample)
                bootstrap_stats.append(boot_stat)
            except:
                continue  # Skip failed bootstrap samples
    
    bootstrap_stats = np.array(bootstrap_stats)
    
    if len(bootstrap_stats) == 0:
        return {
            'error': 'No successful bootstrap samples',
            'original_statistic': original_stat
        }
    
    alpha = 1 - confidence_level
    
    if method == 'percentile':
        # Simple percentile method
        ci_lower = np.percentile(bootstrap_stats, (alpha/2) * 100)
        ci_upper = np.percentile(bootstrap_stats, (1 - alpha/2) * 100)
        
    elif method == 'bias_corrected':
        # Bias-corrected percentile method
        # Count how many bootstrap statistics are less than original
        p_less = np.mean(bootstrap_stats < original_stat)
        
        # Bias correction
        z0 = stats.norm.ppf(p_less) if 0 < p_less < 1 else 0
        
        # Adjusted percentiles
        z_alpha = stats.norm.ppf(alpha/2)
        z_1_alpha = stats.norm.ppf(1 - alpha/2)
        
        p_lower = stats.norm.cdf(2*z0 + z_alpha)
        p_upper = stats.norm.cdf(2*z0 + z_1_alpha)
        
        # Ensure percentiles are within [0, 1]
        p_lower = max(0, min(1, p_lower))
        p_upper = max(0, min(1, p_upper))
        
        ci_lower = np.percentile(bootstrap_stats, p_lower * 100)
        ci_upper = np.percentile(bootstrap_stats, p_upper * 100)
        
    elif method == 'accelerated':
        # BCa (bias-corrected and accelerated) - simplified version
        # This would require jackknife estimation for full implementation
        # For now, use bias-corrected method
        return bootstrap_confidence_intervals(data, statistic_func, confidence_level, 
                                            n_bootstrap, method='bias_corrected')
    
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # Bootstrap statistics
    bootstrap_mean = np.mean(bootstrap_stats)
    bootstrap_std = np.std(bootstrap_stats)
    bootstrap_bias = bootstrap_mean - original_stat
    
    return {
        'original_statistic': original_stat,
        'bootstrap_statistics': bootstrap_stats.tolist(),
        'confidence_interval': (ci_lower, ci_upper),
        'confidence_level': confidence_level,
        'method': method,
        'bootstrap_summary': {
            'n_bootstrap': len(bootstrap_stats),
            'mean': bootstrap_mean,
            'std': bootstrap_std,
            'bias': bootstrap_bias,
            'successful_samples': len(bootstrap_stats),
            'total_attempts': n_bootstrap
        },
        'interval_interpretation': {
            'contains_original': ci_lower <= original_stat <= ci_upper,
            'interval_width': ci_upper - ci_lower,
            'relative_width': (ci_upper - ci_lower) / abs(original_stat) if original_stat != 0 else np.inf
        }
    }

def validate_reproducibility(experiment_func, n_replications=100, **experiment_kwargs):
    """
    Validate reproducibility of experimental results through repeated execution.
    
    Args:
        experiment_func: Function that performs the experiment
        n_replications: Number of independent replications
        **experiment_kwargs: Arguments to pass to experiment function
        
    Returns:
        dict: Reproducibility validation results
    """
    results = []
    successful_runs = 0
    
    for i in range(n_replications):
        try:
            # Set different random seed for each replication
            np.random.seed(i * 42)  # Deterministic but different seeds
            
            result = experiment_func(**experiment_kwargs)
            results.append(result)
            successful_runs += 1
            
        except Exception as e:
            print(f"Replication {i+1} failed: {str(e)}")
            continue
    
    if successful_runs == 0:
        return {
            'error': 'No successful replications',
            'attempted_replications': n_replications
        }
    
    # Convert results to numpy array if possible
    try:
        results_array = np.array(results)
        
        # Compute reproducibility statistics
        mean_result = np.mean(results_array, axis=0)
        std_result = np.std(results_array, axis=0)
        cv_result = std_result / np.abs(mean_result) if np.all(mean_result != 0) else np.inf
        
        # Test for consistency (low coefficient of variation)
        reproducible = np.all(cv_result < 0.1) if np.isfinite(cv_result).all() else False
        
        reproducibility_stats = {
            'mean': mean_result.tolist() if hasattr(mean_result, 'tolist') else mean_result,
            'std': std_result.tolist() if hasattr(std_result, 'tolist') else std_result,
            'coefficient_of_variation': cv_result.tolist() if hasattr(cv_result, 'tolist') else cv_result,
            'is_reproducible': reproducible
        }
        
    except:
        # Handle case where results are not arrays (e.g., dictionaries)
        if isinstance(results[0], dict):
            # Extract common numeric values from dictionaries
            reproducibility_stats = {}
            for key in results[0].keys():
                try:
                    values = [r[key] for r in results if key in r and isinstance(r[key], (int, float))]
                    if values:
                        reproducibility_stats[key] = {
                            'mean': np.mean(values),
                            'std': np.std(values),
                            'cv': np.std(values) / np.abs(np.mean(values)) if np.mean(values) != 0 else np.inf,
                            'values': values
                        }
                except:
                    continue
        else:
            # Handle other result types
            reproducibility_stats = {
                'note': 'Results not suitable for automatic statistical analysis',
                'all_results': results
            }
    
    # Compute confidence intervals for key statistics
    confidence_intervals = {}
    if isinstance(results[0], (int, float)):
        # Simple numeric results
        ci_result = bootstrap_confidence_intervals(
            results, 
            lambda x: np.mean(x), 
            n_bootstrap=min(1000, successful_runs * 10)
        )
        confidence_intervals['mean'] = ci_result['confidence_interval']
    
    return {
        'experiment_summary': {
            'successful_replications': successful_runs,
            'attempted_replications': n_replications,
            'success_rate': successful_runs / n_replications,
            'experiment_function': experiment_func.__name__
        },
        'reproducibility_analysis': reproducibility_stats,
        'confidence_intervals': confidence_intervals,
        'all_results': results,
        'reproducibility_assessment': {
            'highly_reproducible': successful_runs >= 0.95 * n_replications,
            'moderately_reproducible': successful_runs >= 0.8 * n_replications,
            'poorly_reproducible': successful_runs < 0.8 * n_replications,
            'recommendation': (
                'Results are highly reproducible' if successful_runs >= 0.95 * n_replications else
                'Results are moderately reproducible' if successful_runs >= 0.8 * n_replications else
                'Results show poor reproducibility - investigate sources of variation'
            )
        }
    }

def cross_validation_analysis(X, y, model, cv_folds=5, scoring='accuracy', 
                            stratified=True, **model_kwargs):
    """
    Perform cross-validation analysis for model validation.
    
    Args:
        X: Feature matrix
        y: Target values
        model: Scikit-learn compatible model
        cv_folds: Number of cross-validation folds
        scoring: Scoring metric
        stratified: Use stratified CV for classification
        **model_kwargs: Additional model parameters
        
    Returns:
        dict: Cross-validation analysis results
    """
    X = np.array(X)
    y = np.array(y)
    
    # Determine if this is classification or regression
    is_classification = len(np.unique(y)) < len(y) * 0.5 and len(np.unique(y)) <= 20
    
    # Choose cross-validation strategy
    if is_classification and stratified:
        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
    else:
        cv = KFold(n_splits=cv_folds, shuffle=True, random_state=42)
    
    # Perform cross-validation
    from sklearn.model_selection import cross_validate
    
    # Multiple scoring metrics
    if is_classification:
        scoring_metrics = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
    else:
        scoring_metrics = ['r2', 'neg_mean_squared_error', 'neg_mean_absolute_error']
    
    # Ensure the requested scoring is in the list
    if scoring not in scoring_metrics:
        scoring_metrics.append(scoring)
    
    cv_results = cross_validate(
        model, X, y, 
        cv=cv, 
        scoring=scoring_metrics,
        return_train_score=True,
        return_estimator=True
    )
    
    # Extract scores
    results_summary = {}
    for metric in scoring_metrics:
        test_scores = cv_results[f'test_{metric}']
        train_scores = cv_results[f'train_{metric}']
        
        results_summary[metric] = {
            'test_scores': test_scores.tolist(),
            'train_scores': train_scores.tolist(),
            'test_mean': np.mean(test_scores),
            'test_std': np.std(test_scores),
            'train_mean': np.mean(train_scores),
            'train_std': np.std(train_scores),
            'overfitting': np.mean(train_scores) - np.mean(test_scores)
        }
    
    # Model stability analysis
    estimators = cv_results['estimator']
    
    # Extract model parameters if available
    parameter_consistency = {}
    if hasattr(estimators[0], 'coef_'):
        # Linear models
        coefficients = [est.coef_ for est in estimators]
        if len(coefficients) > 0:
            coefficients = np.array(coefficients)
            parameter_consistency['coefficients'] = {
                'mean': np.mean(coefficients, axis=0).tolist(),
                'std': np.std(coefficients, axis=0).tolist(),
                'cv': np.std(coefficients, axis=0) / np.abs(np.mean(coefficients, axis=0))
            }
    
    # Prediction consistency analysis
    from sklearn.model_selection import cross_val_predict
    predictions = cross_val_predict(model, X, y, cv=cv)
    
    if is_classification:
        # Classification metrics
        accuracy = accuracy_score(y, predictions)
        precision = precision_score(y, predictions, average='macro', zero_division=0)
        recall = recall_score(y, predictions, average='macro', zero_division=0)
        
        prediction_analysis = {
            'overall_accuracy': accuracy,
            'overall_precision': precision,
            'overall_recall': recall,
            'prediction_type': 'classification'
        }
    else:
        # Regression metrics
        from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
        
        r2 = r2_score(y, predictions)
        mse = mean_squared_error(y, predictions)
        mae = mean_absolute_error(y, predictions)
        
        prediction_analysis = {
            'r_squared': r2,
            'mse': mse,
            'mae': mae,
            'rmse': np.sqrt(mse),
            'prediction_type': 'regression'
        }
    
    # Overall model assessment
    primary_metric = scoring if scoring in results_summary else scoring_metrics[0]
    test_performance = results_summary[primary_metric]['test_mean']
    performance_std = results_summary[primary_metric]['test_std']
    
    model_quality = {
        'performance_score': test_performance,
        'performance_std': performance_std,
        'performance_cv': performance_std / abs(test_performance) if test_performance != 0 else np.inf,
        'stable_performance': performance_std / abs(test_performance) < 0.1 if test_performance != 0 else False,
        'overfitting_detected': results_summary[primary_metric]['overfitting'] > 0.1
    }
    
    return {
        'cross_validation_setup': {
            'cv_folds': cv_folds,
            'scoring_metrics': scoring_metrics,
            'is_classification': is_classification,
            'stratified': stratified,
            'sample_size': len(X),
            'feature_count': X.shape[1] if len(X.shape) > 1 else 1
        },
        'cv_results': results_summary,
        'parameter_consistency': parameter_consistency,
        'prediction_analysis': prediction_analysis,
        'model_quality': model_quality,
        'recommendations': [
            f"Primary metric ({primary_metric}): {test_performance:.3f} ± {performance_std:.3f}",
            f"Performance stability: {'Good' if model_quality['stable_performance'] else 'Poor'}",
            f"Overfitting: {'Detected' if model_quality['overfitting_detected'] else 'Not detected'}",
            f"Model recommendation: {'Acceptable' if test_performance > 0.7 else 'Needs improvement'}"
        ]
    }

def permutation_test_significance(group1, group2, statistic_func=None, 
                                n_permutations=10000, alternative='two-sided'):
    """
    Perform permutation test to assess significance of group differences.
    
    Args:
        group1, group2: Data arrays for comparison
        statistic_func: Function to compute test statistic (default: mean difference)
        n_permutations: Number of permutation samples
        alternative: Test alternative ('two-sided', 'greater', 'less')
        
    Returns:
        dict: Permutation test results
    """
    if statistic_func is None:
        statistic_func = lambda x, y: np.mean(x) - np.mean(y)
    
    group1 = np.array(group1)
    group2 = np.array(group2)
    
    # Observed test statistic
    observed_stat = statistic_func(group1, group2)
    
    # Combined data for permutation
    combined_data = np.concatenate([group1, group2])
    n1 = len(group1)
    n2 = len(group2)
    
    # Permutation test
    permutation_stats = []
    
    for _ in range(n_permutations):
        # Randomly permute combined data
        permuted_data = np.random.permutation(combined_data)
        
        # Split into two groups of original sizes
        perm_group1 = permuted_data[:n1]
        perm_group2 = permuted_data[n1:n1+n2]
        
        # Compute test statistic
        perm_stat = statistic_func(perm_group1, perm_group2)
        permutation_stats.append(perm_stat)
    
    permutation_stats = np.array(permutation_stats)
    
    # Calculate p-value based on alternative hypothesis
    if alternative == 'two-sided':
        p_value = np.mean(np.abs(permutation_stats) >= np.abs(observed_stat))
    elif alternative == 'greater':
        p_value = np.mean(permutation_stats >= observed_stat)
    elif alternative == 'less':
        p_value = np.mean(permutation_stats <= observed_stat)
    else:
        raise ValueError(f"Unknown alternative: {alternative}")
    
    # Effect size (standardized difference)
    pooled_std = np.sqrt(((n1 - 1) * np.var(group1) + (n2 - 1) * np.var(group2)) / (n1 + n2 - 2))
    effect_size = observed_stat / pooled_std if pooled_std > 0 else 0
    
    # Confidence interval for test statistic
    ci_lower = np.percentile(permutation_stats, 2.5)
    ci_upper = np.percentile(permutation_stats, 97.5)
    
    return {
        'test_setup': {
            'group1_size': n1,
            'group2_size': n2,
            'n_permutations': n_permutations,
            'alternative': alternative,
            'statistic_function': statistic_func.__name__ if hasattr(statistic_func, '__name__') else 'custom'
        },
        'test_results': {
            'observed_statistic': observed_stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'effect_size': effect_size,
            'effect_interpretation': (
                'Large' if abs(effect_size) > 0.8 else
                'Medium' if abs(effect_size) > 0.5 else
                'Small' if abs(effect_size) > 0.2 else
                'Negligible'
            )
        },
        'permutation_distribution': {
            'permutation_statistics': permutation_stats.tolist(),
            'mean': np.mean(permutation_stats),
            'std': np.std(permutation_stats),
            'confidence_interval': (ci_lower, ci_upper),
            'observed_in_ci': ci_lower <= observed_stat <= ci_upper
        },
        'interpretation': {
            'null_hypothesis': f"No difference between groups (statistic = 0)",
            'alternative_hypothesis': f"Groups differ ({alternative})",
            'conclusion': f"{'Reject' if p_value < 0.05 else 'Fail to reject'} null hypothesis",
            'practical_significance': f"Effect size: {abs(effect_size):.3f} ({('Large' if abs(effect_size) > 0.8 else 'Medium' if abs(effect_size) > 0.5 else 'Small' if abs(effect_size) > 0.2 else 'Negligible')})"
        }
    }

def bootstrap_hypothesis_test(sample_data, null_value, test_statistic='mean', 
                            alternative='two-sided', n_bootstrap=10000):
    """
    Bootstrap hypothesis test for single sample against null value.
    
    Args:
        sample_data: Sample data array
        null_value: Null hypothesis value
        test_statistic: Test statistic ('mean', 'median', 'std')
        alternative: Alternative hypothesis ('two-sided', 'greater', 'less')
        n_bootstrap: Number of bootstrap samples
        
    Returns:
        dict: Bootstrap hypothesis test results
    """
    sample_data = np.array(sample_data)
    
    # Define statistic function
    if test_statistic == 'mean':
        stat_func = np.mean
    elif test_statistic == 'median':
        stat_func = np.median
    elif test_statistic == 'std':
        stat_func = np.std
    else:
        raise ValueError(f"Unknown test statistic: {test_statistic}")
    
    # Observed statistic
    observed_stat = stat_func(sample_data)
    
    # Center data around null value for bootstrap
    centered_data = sample_data - (observed_stat - null_value)
    
    # Bootstrap test
    bootstrap_stats = []
    
    for _ in range(n_bootstrap):
        # Bootstrap sample from centered data
        boot_indices = np.random.choice(len(centered_data), len(centered_data), replace=True)
        boot_sample = centered_data[boot_indices]
        
        # Compute statistic
        boot_stat = stat_func(boot_sample)
        bootstrap_stats.append(boot_stat)
    
    bootstrap_stats = np.array(bootstrap_stats)
    
    # Calculate p-value
    if alternative == 'two-sided':
        p_value = np.mean(np.abs(bootstrap_stats - null_value) >= np.abs(observed_stat - null_value))
    elif alternative == 'greater':
        p_value = np.mean(bootstrap_stats >= observed_stat)
    elif alternative == 'less':
        p_value = np.mean(bootstrap_stats <= observed_stat)
    else:
        raise ValueError(f"Unknown alternative: {alternative}")
    
    # Bootstrap confidence interval for the statistic
    ci_lower = np.percentile(bootstrap_stats, 2.5)
    ci_upper = np.percentile(bootstrap_stats, 97.5)
    
    return {
        'test_setup': {
            'sample_size': len(sample_data),
            'null_value': null_value,
            'test_statistic': test_statistic,
            'alternative': alternative,
            'n_bootstrap': n_bootstrap
        },
        'test_results': {
            'observed_statistic': observed_stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'confidence_interval': (ci_lower, ci_upper),
            'null_in_ci': ci_lower <= null_value <= ci_upper
        },
        'bootstrap_distribution': {
            'bootstrap_statistics': bootstrap_stats.tolist(),
            'mean': np.mean(bootstrap_stats),
            'std': np.std(bootstrap_stats)
        },
        'interpretation': {
            'null_hypothesis': f"{test_statistic.capitalize()} = {null_value}",
            'alternative_hypothesis': f"{test_statistic.capitalize()} {alternative} {null_value}",
            'conclusion': f"{'Reject' if p_value < 0.05 else 'Fail to reject'} null hypothesis at α = 0.05",
            'practical_interpretation': f"Observed {test_statistic}: {observed_stat:.4f}, 95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]"
        }
    }