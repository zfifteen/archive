# Repository Cleanup and Standardization Plan

## Overview

This document outlines a comprehensive plan to clean up and standardize the unified-framework repository. The repository currently contains 287 Python files across 109MB of data, with scattered output directories, mixed demo files, and inconsistent organization that needs systematic reorganization.

## Current State Analysis

- **Total Size**: 109MB
- **Python Files**: 287 files
- **Major Issues**: 
  - Multiple output directories (demo_output, test_output, production_output, etc.)
  - Demo files scattered in root directory
  - Mixed src/ and direct module structure
  - Large HTML visualization files in root
  - Inconsistent naming conventions
  - JSON result files cluttering root

## 1. Create a "cleanup" Branch

Create a dedicated branch for cleanup work to ensure safe, reviewable changes.

```bash
# Create and switch to cleanup branch
git checkout -b cleanup/repository-standardization

# Verify branch creation
git branch --show-current
```

**Key Steps:**
- Ensure all current work is committed
- Create descriptive branch name following convention
- Set up tracking with remote
- Document branch purpose in initial commit

## 2. Audit & Inventory

### 2.1 File Type Analysis

```bash
# Analyze file types and sizes
find . -type f -exec ls -la {} \; | awk '{print $5, $9}' | sort -nr > /tmp/file_sizes.txt

# Count files by extension
find . -type f | sed 's/.*\.//' | sort | uniq -c | sort -nr > /tmp/file_types.txt

# Identify large files (>1MB)
find . -type f -size +1M -exec ls -lh {} \; | sort -k5 -hr
```

### 2.2 Directory Structure Assessment

Current problematic directories:
- `demo_5d_output/` - Demo output files
- `demo_output/` - More demo outputs  
- `example_advanced_3d_output/` - Example outputs
- `example_advanced_4d_output/` - Example outputs
- `example_advanced_5d_output/` - Example outputs
- `example_basic_output/` - Basic example outputs
- `production_output/` - Production outputs
- `test_output/` - Test outputs
- `validation_output/` - Validation outputs
- `variance_analysis_results/` - Analysis results
- `enhanced_variance_analysis_results/` - Enhanced analysis results

### 2.3 Code Organization Issues

```bash
# Identify Python files in root that should be organized
find . -maxdepth 1 -name "*.py" -type f

# Current structure shows:
# - cli_demo.py
# - demo_kbllm.py  
# - demo_z_framework.py
# - prime_compression_demo.py
# - run_variance_analysis.py
# - simple_compression_example.py
# - simple_demo.py
# - test_linear_scaling.py
# - validate_linear_scaling.py
```

## 3. Define the Target Layout

### 3.1 Proposed Directory Structure

```
unified-framework/
├── docs/                           # Documentation
│   ├── api/                       # API documentation
│   ├── guides/                    # User guides
│   ├── research/                  # Research papers and notes
│   └── examples/                  # Example documentation
├── src/                           # Main source code
│   ├── core/                      # Core Z framework
│   ├── analysis/                  # Analysis modules
│   ├── applications/              # Applications
│   ├── number_theory/             # Number theory modules
│   ├── statistical/               # Statistical modules
│   ├── symbolic/                  # Symbolic computation
│   ├── validation/                # Validation modules
│   └── visualization/             # Visualization modules
├── tests/                         # Test suite
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   ├── performance/               # Performance tests
│   └── fixtures/                  # Test fixtures and data
├── examples/                      # Code examples and demos
│   ├── basic/                     # Basic examples
│   ├── advanced/                  # Advanced examples
│   ├── demos/                     # Interactive demos
│   └── tutorials/                 # Tutorial code
├── scripts/                       # Utility scripts
│   ├── build/                     # Build scripts
│   ├── validation/                # Validation scripts
│   └── analysis/                  # Analysis scripts
├── data/                          # Data files (gitignored)
│   ├── input/                     # Input datasets
│   ├── output/                    # Generated outputs
│   ├── cache/                     # Cached computations
│   └── results/                   # Analysis results
├── tools/                         # Development tools
├── .github/                       # GitHub workflows
├── requirements/                  # Requirements files
│   ├── base.txt                   # Base requirements
│   ├── dev.txt                    # Development requirements
│   └── test.txt                   # Testing requirements
└── configs/                       # Configuration files
```

### 3.2 File Naming Conventions

- **Python modules**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case()`
- **Constants**: `UPPER_SNAKE_CASE`
- **Test files**: `test_*.py`
- **Example files**: `example_*.py`
- **Demo files**: `demo_*.py`

## 4. Map & Plan Moves

### 4.1 Root Level Cleanup

```bash
# Create mapping of current files to new locations
cat > /tmp/file_moves.txt << 'EOF'
# Root demo files → examples/demos/
cli_demo.py → examples/demos/cli_demo.py
demo_kbllm.py → examples/demos/demo_kbllm.py
demo_z_framework.py → examples/demos/demo_z_framework.py
prime_compression_demo.py → examples/demos/prime_compression_demo.py
simple_compression_example.py → examples/basic/simple_compression_example.py
simple_demo.py → examples/basic/simple_demo.py

# Validation scripts → scripts/validation/
run_variance_analysis.py → scripts/validation/run_variance_analysis.py
test_linear_scaling.py → scripts/validation/test_linear_scaling.py
validate_linear_scaling.py → scripts/validation/validate_linear_scaling.py

# Large HTML files → data/output/visualizations/
helix_parameter_sweep.html → data/output/visualizations/helix_parameter_sweep.html
interactive_helix_main.html → data/output/visualizations/interactive_helix_main.html
quantum_correlations.html → data/output/visualizations/quantum_correlations.html

# JSON results → data/output/results/
analysis_report.json → data/output/results/analysis_report.json
comprehensive_z_model_results.json → data/output/results/comprehensive_z_model_results.json
computational_validation_results.json → data/output/results/computational_validation_results.json
high_scale_validation_results.json → data/output/results/high_scale_validation_results.json
tc_inst_01_results_*.json → data/output/results/

# Log files → data/output/logs/
computational_validation.log → data/output/logs/computational_validation.log
high_scale_validation.log → data/output/logs/high_scale_validation.log
linear_scaling_validation_report.txt → data/output/logs/linear_scaling_validation_report.txt
EOF
```

### 4.2 Output Directory Consolidation

```bash
# Plan consolidation of output directories
cat > /tmp/output_moves.txt << 'EOF'
demo_5d_output/ → data/output/demos/5d/
demo_output/ → data/output/demos/basic/
example_advanced_3d_output/ → data/output/examples/advanced_3d/
example_advanced_4d_output/ → data/output/examples/advanced_4d/
example_advanced_5d_output/ → data/output/examples/advanced_5d/
example_basic_output/ → data/output/examples/basic/
production_output/ → data/output/production/
test_output/ → data/output/tests/
validation_output/ → data/output/validation/
variance_analysis_results/ → data/output/analysis/variance/
enhanced_variance_analysis_results/ → data/output/analysis/variance_enhanced/
EOF
```

## 5. Execute in Phases

### Phase A — Non-Code Assets

**Goal**: Move documentation, data files, and outputs without affecting code functionality.

#### A.1 Create New Directory Structure

```bash
# Create the new directory structure
mkdir -p data/output/{demos/{5d,basic},examples/{advanced_3d,advanced_4d,advanced_5d,basic},production,tests,validation,analysis/{variance,variance_enhanced},visualizations,results,logs}
mkdir -p examples/{basic,advanced,demos,tutorials}
mkdir -p scripts/{build,validation,analysis}
mkdir -p requirements
mkdir -p configs
mkdir -p tools
```

#### A.2 Move Output Directories

```bash
# Move output directories (safe operations)
mv demo_5d_output/* data/output/demos/5d/ 2>/dev/null || true
mv demo_output/* data/output/demos/basic/ 2>/dev/null || true
mv example_advanced_3d_output/* data/output/examples/advanced_3d/ 2>/dev/null || true
mv example_advanced_4d_output/* data/output/examples/advanced_4d/ 2>/dev/null || true
mv example_advanced_5d_output/* data/output/examples/advanced_5d/ 2>/dev/null || true
mv example_basic_output/* data/output/examples/basic/ 2>/dev/null || true
mv production_output/* data/output/production/ 2>/dev/null || true
mv test_output/* data/output/tests/ 2>/dev/null || true
mv validation_output/* data/output/validation/ 2>/dev/null || true
mv variance_analysis_results/* data/output/analysis/variance/ 2>/dev/null || true
mv enhanced_variance_analysis_results/* data/output/analysis/variance_enhanced/ 2>/dev/null || true

# Remove empty directories
rmdir demo_5d_output demo_output example_*_output production_output test_output validation_output variance_analysis_results enhanced_variance_analysis_results 2>/dev/null || true
```

#### A.3 Move Large Files and Results

```bash
# Move large visualization files
mv helix_parameter_sweep.html data/output/visualizations/
mv interactive_helix_main.html data/output/visualizations/
mv quantum_correlations.html data/output/visualizations/

# Move result and log files
mv analysis_report.json data/output/results/
mv comprehensive_z_model_results.json data/output/results/
mv computational_validation_results.json data/output/results/
mv high_scale_validation_results.json data/output/results/
mv tc_inst_01_results_*.json data/output/results/
mv computational_validation.log data/output/logs/
mv high_scale_validation.log data/output/logs/
mv linear_scaling_validation_report.txt data/output/logs/
```

### Phase B — Code & Tests

**Goal**: Reorganize code files while maintaining import functionality.

#### B.1 Move Demo and Example Files

```bash
# Move demo files
mv cli_demo.py examples/demos/
mv demo_kbllm.py examples/demos/
mv demo_z_framework.py examples/demos/
mv prime_compression_demo.py examples/demos/

# Move basic examples
mv simple_compression_example.py examples/basic/
mv simple_demo.py examples/basic/
```

#### B.2 Move Validation Scripts

```bash
# Move validation scripts
mv run_variance_analysis.py scripts/validation/
mv test_linear_scaling.py scripts/validation/
mv validate_linear_scaling.py scripts/validation/
```

#### B.3 Update Requirements

```bash
# Split requirements file
cp requirements.txt requirements/base.txt

# Create development requirements
cat > requirements/dev.txt << 'EOF'
-r base.txt
pytest>=7.0.0
pytest-cov>=4.0.0
black>=22.0.0
flake8>=5.0.0
mypy>=1.0.0
pre-commit>=2.20.0
EOF

# Create test requirements
cat > requirements/test.txt << 'EOF'
-r base.txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
pytest-benchmark>=4.0.0
EOF
```

### Phase C — Cleanup & Archive

**Goal**: Remove redundant files and update references.

#### C.1 Update .gitignore

```bash
# Update .gitignore for new structure
cat >> .gitignore << 'EOF'

# New data structure
/data/output/
/data/cache/
/data/input/*.csv
/data/results/

# IDE and editor files
.vscode/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Jupyter Notebook checkpoints
.ipynb_checkpoints/

# pytest cache
.pytest_cache/

# Coverage reports
htmlcov/
.coverage
.coverage.*
coverage.xml
*.cover
.hypothesis/

# mypy
.mypy_cache/
.dmypy.json
dmypy.json
EOF
```

#### C.2 Remove Duplicate Files

```bash
# Identify and remove duplicate files (after verification)
find . -name "*.py" -exec basename {} \; | sort | uniq -d > /tmp/potential_duplicates.txt

# Review and remove confirmed duplicates manually
# Example: if original requirements.txt is same as requirements/base.txt
# rm requirements.txt
```

## 6. Update Tooling & CI

### 6.1 Update Import Statements

Create a script to update import statements for moved files:

```python
# scripts/build/update_imports.py
import os
import re
import glob

def update_imports_in_file(filepath):
    """Update import statements in a Python file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Define import mappings
    mappings = {
        r'from cli_demo import': 'from examples.demos.cli_demo import',
        r'from demo_kbllm import': 'from examples.demos.demo_kbllm import',
        r'from demo_z_framework import': 'from examples.demos.demo_z_framework import',
        r'import cli_demo': 'import examples.demos.cli_demo',
        r'import demo_kbllm': 'import examples.demos.demo_kbllm',
        r'import demo_z_framework': 'import examples.demos.demo_z_framework',
    }
    
    modified = False
    for pattern, replacement in mappings.items():
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
    
    if modified:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated imports in {filepath}")

# Update all Python files
for py_file in glob.glob('**/*.py', recursive=True):
    update_imports_in_file(py_file)
```

### 6.2 Create Setup Configuration

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="unified-framework",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "mpmath>=1.2.0",
        "sympy>=1.8.0",
        "scikit-learn>=1.0.0",
        "statsmodels>=0.13.0",
        "scipy>=1.7.0",
        "seaborn>=0.11.0",
        "plotly>=5.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "pytest-benchmark>=4.0.0",
        ],
    },
)
```

### 6.3 Add Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: check-toml
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 22.12.0
    hooks:
      - id: black
        language_version: python3.8

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## 7. Documentation & Onboarding

### 7.1 Update README.md

Add new structure section to README.md:

```markdown
## Repository Structure

The repository is organized as follows:

- `src/` - Main source code modules
- `tests/` - Comprehensive test suite
- `examples/` - Code examples and demonstrations
- `scripts/` - Utility and build scripts
- `docs/` - Documentation and research papers
- `data/` - Data files and outputs (gitignored)
- `tools/` - Development and analysis tools
- `configs/` - Configuration files
- `requirements/` - Dependency specifications

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements/base.txt
   ```

2. Run basic examples:
   ```bash
   python examples/basic/simple_demo.py
   ```

3. Run comprehensive validation:
   ```bash
   python scripts/validation/validate_linear_scaling.py
   ```
```

### 7.2 Create Migration Guide

```markdown
# Migration Guide

## For Existing Users

If you have existing code that imports from the old structure:

### Old Import Style
```python
import cli_demo
from demo_z_framework import *
```

### New Import Style
```python
import examples.demos.cli_demo as cli_demo
from examples.demos.demo_z_framework import *
```

## Path Updates

- Demo files: `./demo_*.py` → `examples/demos/demo_*.py`
- Output data: `./demo_output/` → `data/output/demos/basic/`
- Validation scripts: `./validate_*.py` → `scripts/validation/validate_*.py`

## Environment Setup

1. Update your PYTHONPATH if needed:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   ```
```

### 7.3 Create Development Guide

```markdown
# Development Guide

## Setting Up Development Environment

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -r requirements/dev.txt
   ```
3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Code Organization

- **Core Framework**: `src/core/` - Fundamental Z framework components
- **Analysis**: `src/analysis/` - Mathematical analysis modules  
- **Applications**: `src/applications/` - Practical applications
- **Number Theory**: `src/number_theory/` - Prime and number theory modules
- **Visualization**: `src/visualization/` - Plotting and visualization tools

## Testing

Run tests with:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## Code Style

The project uses:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking
- **isort** for import sorting

Format code before committing:
```bash
black src/ tests/ examples/
flake8 src/ tests/ examples/
mypy src/
```
```

## 8. Review & Merge

### 8.1 Testing Phase

Before merging, run comprehensive tests:

```bash
# Run existing tests to ensure nothing broke
python -m pytest tests/ -v

# Test key demos still work
python examples/demos/simple_demo.py
python examples/demos/demo_z_framework.py

# Test validation scripts
python scripts/validation/test_linear_scaling.py

# Verify imports work correctly
python -c "from src.core.axioms import universal_invariance; print('Import successful')"
```

### 8.2 Code Review Checklist

- [ ] All files moved to appropriate directories
- [ ] Import statements updated correctly
- [ ] No broken relative imports
- [ ] Demo scripts still functional
- [ ] Tests pass
- [ ] Documentation updated
- [ ] .gitignore covers new structure
- [ ] No large files in repository
- [ ] Requirements files properly split

### 8.3 Gradual Rollout

Consider implementing changes gradually:

1. **Week 1**: Phase A (non-code assets)
2. **Week 2**: Phase B (code reorganization)  
3. **Week 3**: Phase C (cleanup and tooling)
4. **Week 4**: Documentation and testing

## 9. Post-Merge Actions

### 9.1 Update Documentation

- Update all wiki pages
- Update any external documentation
- Notify users of structure changes
- Update CI/CD pipelines if any

### 9.2 Cleanup Old References

```bash
# Search for any remaining old references
grep -r "demo_output" . --exclude-dir=.git
grep -r "test_output" . --exclude-dir=.git
grep -r "production_output" . --exclude-dir=.git

# Update any remaining references
```

### 9.3 Set Branch Protection

After successful merge:
- Set up branch protection rules
- Require PR reviews for main branch
- Enable status checks
- Require up-to-date branches

### 9.4 Archive Cleanup Branch

```bash
# After successful merge, clean up
git branch -d cleanup/repository-standardization
git push origin --delete cleanup/repository-standardization
```

## Success Metrics

The cleanup will be considered successful when:

- [ ] Repository size reduced by >20% (target: <87MB)
- [ ] All demo scripts work from new locations
- [ ] Import statements resolve correctly
- [ ] Test suite passes completely
- [ ] Documentation reflects new structure
- [ ] CI/CD pipelines updated
- [ ] No broken links in documentation
- [ ] Developer onboarding time reduced

## Risk Mitigation

- **Backup Strategy**: Keep cleanup branch until confirmed stable
- **Rollback Plan**: Document exact steps to revert changes
- **Testing Strategy**: Test each phase before proceeding
- **Communication**: Notify all contributors before major moves
- **Incremental Approach**: Implement in phases to minimize disruption

---

*This cleanup plan aims to transform the unified-framework repository into a well-organized, maintainable, and professional codebase while preserving all existing functionality.*