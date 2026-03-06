#!/usr/bin/env python3
"""
Comprehensive Measurement Methodology Audit Tool
================================================

Automated analysis tool for identifying measurement inconsistencies,
methodological gaps, and reliability issues across the Unified Framework.

Author: Copilot (GitHub Issue #391 Follow-up)
Date: 2025
"""

import os
import re
import ast
import json
import sys
from collections import defaultdict, Counter
from pathlib import Path
import datetime

class MeasurementMethodologyAuditor:
    """Comprehensive auditor for measurement methodologies across the framework"""
    
    def __init__(self, framework_root):
        """Initialize auditor with framework root directory"""
        self.framework_root = Path(framework_root)
        self.audit_results = {
            'metadata': {
                'audit_date': datetime.datetime.now().isoformat(),
                'framework_root': str(self.framework_root),
                'auditor_version': '1.0.0'
            },
            'findings': {},
            'recommendations': [],
            'severity_summary': {}
        }
        
        # Patterns to identify measurement/evaluation functions
        self.measurement_patterns = [
            r'def.*enhancement.*\(',
            r'def.*measure.*\(',
            r'def.*validate.*\(',
            r'def.*test.*\(',
            r'def.*metric.*\(',
            r'def.*performance.*\(',
            r'def.*correlation.*\(',
            r'def.*optimize.*\(',
            r'def.*bootstrap.*\(',
            r'def.*confidence.*\(',
        ]
        
        # Problematic calculation patterns
        self.problematic_patterns = {
            'enhancement_inconsistency': [
                r'enhancement.*=.*(max_density.*-.*mean_density).*/',
                r'enhancement.*=.*(prime_counts.*-.*expected).*/',
                r'enhancement.*=.*\(.*-.*\).*\*.*100',
                r'enhancement_ratio.*=.*max_density.*/',
            ],
            'missing_confidence_intervals': [
                r'def.*enhancement.*\(',
                r'return.*enhancement(?!.*confidence|.*ci|.*error)',
            ],
            'hardcoded_thresholds': [
                r'threshold.*=.*0\.\d+',
                r'if.*>.*0\.\d+:',
                r'target.*=.*0\.\d+',
            ],
            'missing_error_propagation': [
                r'np\.mean\(',
                r'np\.std\(',
                r'np\.var\(',
                r'(?!.*error|.*ci|.*confidence)',
            ],
            'parameter_optimization_issues': [
                r'k_values.*=.*np\.linspace\(.*,.*,.*\d\)',
                r'range.*=.*\(.*,.*\)',
                r'optimization_steps.*=.*\d+',
            ],
        }
        
    def audit_framework(self):
        """Run comprehensive audit of the framework"""
        print("Starting Comprehensive Measurement Methodology Audit...")
        print("=" * 60)
        
        # 1. Scan all Python files for measurement functions
        python_files = self._find_python_files()
        print(f"Found {len(python_files)} Python files to analyze")
        
        # 2. Analyze measurement methodologies
        self._analyze_measurement_functions(python_files)
        
        # 3. Detect enhancement calculation inconsistencies
        self._detect_enhancement_inconsistencies(python_files)
        
        # 4. Analyze statistical rigor
        self._analyze_statistical_rigor(python_files)
        
        # 5. Check parameter optimization procedures
        self._analyze_parameter_optimization(python_files)
        
        # 6. Analyze cross-file consistency
        self._analyze_cross_file_consistency()
        
        # 7. Generate severity assessment
        self._generate_severity_assessment()
        
        # 8. Generate recommendations
        self._generate_recommendations()
        
        print(f"\nAudit complete. Found {len(self.audit_results['findings'])} categories of issues.")
        return self.audit_results
    
    def _find_python_files(self):
        """Find all Python files in the framework"""
        python_files = []
        
        for root, dirs, files in os.walk(self.framework_root):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def _analyze_measurement_functions(self, python_files):
        """Analyze measurement and evaluation functions"""
        measurement_functions = []
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find measurement functions
                for pattern in self.measurement_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Extract function definition
                        lines = content[:match.start()].count('\n')
                        function_info = {
                            'file': str(file_path.relative_to(self.framework_root)),
                            'line': lines + 1,
                            'function': match.group(),
                            'pattern': pattern
                        }
                        measurement_functions.append(function_info)
            
            except Exception as e:
                print(f"Warning: Could not analyze {file_path}: {e}")
        
        self.audit_results['findings']['measurement_functions'] = {
            'total_functions': len(measurement_functions),
            'functions': measurement_functions,
            'files_with_measurements': len(set(f['file'] for f in measurement_functions))
        }
    
    def _detect_enhancement_inconsistencies(self, python_files):
        """Detect inconsistent enhancement calculation methods"""
        enhancement_methods = defaultdict(list)
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for different enhancement calculation patterns
                for method_type, patterns in self.problematic_patterns.items():
                    if 'enhancement' in method_type:
                        for pattern in patterns:
                            matches = re.finditer(pattern, content, re.IGNORECASE)
                            for match in matches:
                                lines = content[:match.start()].count('\n')
                                enhancement_methods[method_type].append({
                                    'file': str(file_path.relative_to(self.framework_root)),
                                    'line': lines + 1,
                                    'code': match.group(),
                                    'pattern': pattern
                                })
            
            except Exception as e:
                continue
        
        self.audit_results['findings']['enhancement_inconsistencies'] = dict(enhancement_methods)
    
    def _analyze_statistical_rigor(self, python_files):
        """Analyze statistical rigor of validation procedures"""
        statistical_issues = {
            'missing_hypothesis_tests': [],
            'missing_confidence_intervals': [],
            'hardcoded_thresholds': [],
            'missing_error_propagation': []
        }
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for statistical rigor issues
                if re.search(r'def.*test.*\(', content, re.IGNORECASE):
                    if not re.search(r'null.*hypothesis|h0|h1', content, re.IGNORECASE):
                        statistical_issues['missing_hypothesis_tests'].append({
                            'file': str(file_path.relative_to(self.framework_root)),
                            'issue': 'Test function without clear null hypothesis'
                        })
                
                # Check for confidence intervals
                if re.search(r'def.*enhancement|def.*correlation', content, re.IGNORECASE):
                    if not re.search(r'confidence|ci_|error|bootstrap', content, re.IGNORECASE):
                        statistical_issues['missing_confidence_intervals'].append({
                            'file': str(file_path.relative_to(self.framework_root)),
                            'issue': 'Enhancement/correlation without confidence intervals'
                        })
                
                # Check for hardcoded thresholds
                hardcoded_matches = re.finditer(r'if.*>.*0\.\d+|threshold.*=.*0\.\d+', content)
                for match in hardcoded_matches:
                    lines = content[:match.start()].count('\n')
                    statistical_issues['hardcoded_thresholds'].append({
                        'file': str(file_path.relative_to(self.framework_root)),
                        'line': lines + 1,
                        'code': match.group()
                    })
            
            except Exception as e:
                continue
        
        self.audit_results['findings']['statistical_rigor'] = statistical_issues
    
    def _analyze_parameter_optimization(self, python_files):
        """Analyze parameter optimization procedures"""
        optimization_issues = {
            'insufficient_grid_search': [],
            'missing_bounds': [],
            'inconsistent_methods': []
        }
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for parameter optimization
                k_optimization = re.finditer(r'k_values.*=.*np\.linspace\((.*?)\)', content)
                for match in k_optimization:
                    lines = content[:match.start()].count('\n')
                    params = match.group(1)
                    
                    # Parse linspace parameters
                    try:
                        # Simple parsing for common cases
                        if params.count(',') >= 2:
                            parts = [p.strip() for p in params.split(',')]
                            start = float(parts[0]) if parts[0].replace('.', '').isdigit() else None
                            end = float(parts[1]) if parts[1].replace('.', '').isdigit() else None
                            num_points = int(parts[2]) if parts[2].isdigit() else None
                            
                            if start is not None and end is not None and num_points is not None:
                                range_size = end - start
                                if range_size < 0.5:  # Too narrow range
                                    optimization_issues['insufficient_grid_search'].append({
                                        'file': str(file_path.relative_to(self.framework_root)),
                                        'line': lines + 1,
                                        'issue': f'Narrow k optimization range: {start}-{end}',
                                        'code': match.group()
                                    })
                                if num_points < 10:  # Too few points
                                    optimization_issues['insufficient_grid_search'].append({
                                        'file': str(file_path.relative_to(self.framework_root)),
                                        'line': lines + 1,
                                        'issue': f'Too few optimization points: {num_points}',
                                        'code': match.group()
                                    })
                    except:
                        optimization_issues['missing_bounds'].append({
                            'file': str(file_path.relative_to(self.framework_root)),
                            'line': lines + 1,
                            'issue': 'Could not parse optimization bounds',
                            'code': match.group()
                        })
            
            except Exception as e:
                continue
        
        self.audit_results['findings']['parameter_optimization'] = optimization_issues
    
    def _analyze_cross_file_consistency(self):
        """Analyze consistency across files"""
        # Collect all enhancement functions and their methods
        enhancement_functions = []
        if 'measurement_functions' in self.audit_results['findings']:
            for func in self.audit_results['findings']['measurement_functions']['functions']:
                if 'enhancement' in func['function'].lower():
                    enhancement_functions.append(func)
        
        # Collect all k optimization ranges
        optimization_ranges = []
        if 'parameter_optimization' in self.audit_results['findings']:
            for category in self.audit_results['findings']['parameter_optimization'].values():
                for issue in category:
                    if 'range' in issue.get('issue', ''):
                        optimization_ranges.append(issue)
        
        self.audit_results['findings']['cross_file_consistency'] = {
            'enhancement_function_count': len(enhancement_functions),
            'enhancement_method_variations': len(set(f['pattern'] for f in enhancement_functions)),
            'k_optimization_range_variations': len(optimization_ranges),
            'consistency_score': self._calculate_consistency_score()
        }
    
    def _calculate_consistency_score(self):
        """Calculate overall consistency score (0-100)"""
        total_issues = 0
        total_opportunities = 0
        
        # Count measurement functions as opportunities for consistency
        if 'measurement_functions' in self.audit_results['findings']:
            total_opportunities += self.audit_results['findings']['measurement_functions']['total_functions']
        
        # Count issues
        for category, findings in self.audit_results['findings'].items():
            if isinstance(findings, dict):
                for subcategory, issues in findings.items():
                    if isinstance(issues, list):
                        total_issues += len(issues)
            elif isinstance(findings, list):
                total_issues += len(findings)
        
        if total_opportunities == 0:
            return 0
        
        # Consistency score: (opportunities - issues) / opportunities * 100
        consistency_score = max(0, (total_opportunities - total_issues) / total_opportunities * 100)
        return round(consistency_score, 2)
    
    def _generate_severity_assessment(self):
        """Generate severity assessment of findings"""
        severity_levels = {
            'critical': 0,
            'high': 0, 
            'medium': 0,
            'low': 0
        }
        
        # Enhancement inconsistencies are critical
        if 'enhancement_inconsistencies' in self.audit_results['findings']:
            for method_type, issues in self.audit_results['findings']['enhancement_inconsistencies'].items():
                if len(issues) > 3:  # Multiple inconsistent methods
                    severity_levels['critical'] += 1
                elif len(issues) > 1:
                    severity_levels['high'] += 1
        
        # Statistical rigor issues
        if 'statistical_rigor' in self.audit_results['findings']:
            for issue_type, issues in self.audit_results['findings']['statistical_rigor'].items():
                if len(issues) > 5:
                    severity_levels['high'] += 1
                elif len(issues) > 2:
                    severity_levels['medium'] += 1
                else:
                    severity_levels['low'] += 1
        
        # Parameter optimization issues
        if 'parameter_optimization' in self.audit_results['findings']:
            for issue_type, issues in self.audit_results['findings']['parameter_optimization'].items():
                if len(issues) > 3:
                    severity_levels['medium'] += 1
                else:
                    severity_levels['low'] += 1
        
        self.audit_results['severity_summary'] = severity_levels
    
    def _generate_recommendations(self):
        """Generate specific recommendations based on findings"""
        recommendations = []
        
        # Enhancement calculation standardization
        if 'enhancement_inconsistencies' in self.audit_results['findings']:
            enhancement_methods = len(self.audit_results['findings']['enhancement_inconsistencies'])
            if enhancement_methods > 0:
                recommendations.append({
                    'priority': 'critical',
                    'category': 'enhancement_calculation',
                    'recommendation': 'Standardize enhancement calculation methods across all components',
                    'estimated_effort': 'high',
                    'affected_components': enhancement_methods
                })
        
        # Statistical rigor improvements
        if 'statistical_rigor' in self.audit_results['findings']:
            missing_ci = len(self.audit_results['findings']['statistical_rigor'].get('missing_confidence_intervals', []))
            if missing_ci > 5:
                recommendations.append({
                    'priority': 'high',
                    'category': 'statistical_rigor',
                    'recommendation': 'Add confidence intervals to all enhancement and correlation calculations',
                    'estimated_effort': 'medium',
                    'affected_components': missing_ci
                })
        
        # Parameter optimization improvements
        if 'parameter_optimization' in self.audit_results['findings']:
            insufficient_grid = len(self.audit_results['findings']['parameter_optimization'].get('insufficient_grid_search', []))
            if insufficient_grid > 2:
                recommendations.append({
                    'priority': 'high',
                    'category': 'parameter_optimization',
                    'recommendation': 'Expand parameter optimization grid search ranges and increase resolution',
                    'estimated_effort': 'medium',
                    'affected_components': insufficient_grid
                })
        
        # Cross-file consistency
        consistency_score = self.audit_results['findings'].get('cross_file_consistency', {}).get('consistency_score', 100)
        if consistency_score < 70:
            recommendations.append({
                'priority': 'medium',
                'category': 'consistency',
                'recommendation': 'Implement framework-wide measurement standards and validation protocols',
                'estimated_effort': 'high',
                'consistency_score': consistency_score
            })
        
        self.audit_results['recommendations'] = recommendations
    
    def save_audit_report(self, output_path):
        """Save comprehensive audit report"""
        with open(output_path, 'w') as f:
            json.dump(self.audit_results, f, indent=2, default=str)
        
        print(f"Comprehensive audit report saved to: {output_path}")
    
    def print_summary(self):
        """Print audit summary to console"""
        print("\n" + "=" * 60)
        print("COMPREHENSIVE MEASUREMENT METHODOLOGY AUDIT SUMMARY")
        print("=" * 60)
        
        # Severity summary
        print("\nSeverity Assessment:")
        for level, count in self.audit_results['severity_summary'].items():
            print(f"  {level.upper()}: {count} issues")
        
        # Key findings
        print(f"\nKey Findings:")
        findings = self.audit_results['findings']
        
        if 'measurement_functions' in findings:
            print(f"  - Found {findings['measurement_functions']['total_functions']} measurement functions")
            print(f"  - Across {findings['measurement_functions']['files_with_measurements']} files")
        
        if 'enhancement_inconsistencies' in findings:
            total_enhancement_issues = sum(len(issues) for issues in findings['enhancement_inconsistencies'].values())
            print(f"  - {total_enhancement_issues} enhancement calculation inconsistencies")
        
        if 'statistical_rigor' in findings:
            total_statistical_issues = sum(len(issues) for issues in findings['statistical_rigor'].values())
            print(f"  - {total_statistical_issues} statistical rigor deficiencies")
        
        if 'cross_file_consistency' in findings:
            consistency_score = findings['cross_file_consistency']['consistency_score']
            print(f"  - Framework consistency score: {consistency_score}%")
        
        # Recommendations
        print(f"\nTop Recommendations:")
        for i, rec in enumerate(self.audit_results['recommendations'][:3], 1):
            print(f"  {i}. [{rec['priority'].upper()}] {rec['recommendation']}")


def main():
    """Main function to run the comprehensive audit"""
    framework_root = os.path.abspath('.')
    
    print("Unified Framework Measurement Methodology Audit")
    print("=" * 50)
    print(f"Framework root: {framework_root}")
    print()
    
    # Run audit
    auditor = MeasurementMethodologyAuditor(framework_root)
    results = auditor.audit_framework()
    
    # Print summary
    auditor.print_summary()
    
    # Save detailed results
    output_file = 'comprehensive_measurement_audit_results.json'
    auditor.save_audit_report(output_file)
    
    return results


if __name__ == "__main__":
    results = main()