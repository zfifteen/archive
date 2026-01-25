# LLM Comparative Experiment: Dirichlet's Theorem Computational Illustration

## Context

You are participating in a controlled experiment comparing three frontier LLMs (Grok, Claude, GPT-4) on a mathematical exposition and coding task. This experiment will be documented in a public GitHub repository for research purposes.

**Source Material**: 3Blue1Brown video "Why do prime numbers make these spirals?"
- URL: https://youtu.be/EK32jo7i5LQ?si=j6vIH12Enb2dPXtt
- Relevant segment: ~18:30-22:00 (Dirichlet's theorem explanation)

**Your Task**: Create a complete, executable computational illustration of Dirichlet's theorem on primes in arithmetic progressions, suitable for a GitHub Gist.

## Evaluation Criteria (Full Transparency)

Your output will be evaluated on:
1. **Mathematical Correctness**: Accurate statement and implementation of Dirichlet's theorem
2. **Code Quality**: Clean, efficient, well-documented, executable Python code
3. **Pedagogical Clarity**: Accessible explanations for senior undergrad/early grad level
4. **Visualization Effectiveness**: Clear, informative plots with proper labeling

## Required Deliverables

Create exactly these four files in the current directory:

### 1. `README.md`
Must contain:
- Brief introduction to Dirichlet's theorem (2-3 paragraphs)
- Formal statement of the theorem with mathematical notation
- Explanation of φ(N) (Euler's totient function)
- Description of the computational experiment methodology
- Instructions to run the code
- Section interpreting/explaining the results

Target audience: Senior undergraduate or early graduate student in mathematics

### 2. `primes_utils.py`
Must implement these three functions with NO placeholders:

```python
def sieve_of_eratosthenes(limit):
    """
    Generate all primes up to limit using Sieve of Eratosthenes.
    
    Args:
        limit (int): Upper bound for prime generation
        
    Returns:
        list: All primes <= limit
    """
    # Your implementation

def primes_by_residue_class(limit, modulus):
    """
    Partition primes by residue class modulo N.
    
    Args:
        limit (int): Upper bound for prime search
        modulus (int): The modulus N for residue classes
        
    Returns:
        dict: Maps residue class r to list of primes p where p ≡ r (mod N)
    """
    # Your implementation

def compute_empirical_density(limit, modulus):
    """
    Compute observed frequency of primes in each residue class.
    
    Args:
        limit (int): Upper bound for analysis
        modulus (int): The modulus N
        
    Returns:
        dict: Maps residue class r to empirical density (observed frequency)
    """
    # Your implementation
```

### 3. `visualizations.py`
Must generate exactly these 6 matplotlib figures and save them as PNG files:

1. **`convergence_N3.png`**: Line plot showing convergence for N=3
   - X-axis: upper limit of primes considered
   - Y-axis: empirical density for each residue class
   - Include horizontal line at theoretical value 1/φ(3) = 1/2
   - Show all valid residue classes coprime to 3

2. **`convergence_N4.png`**: Same as above for N=4
   - Theoretical value: 1/φ(4) = 1/2

3. **`convergence_N5.png`**: Same as above for N=5
   - Theoretical value: 1/φ(5) = 1/4

4. **`comparison_N12.png`**: Bar chart for N=12
   - Compare empirical vs theoretical densities side-by-side
   - Show all residue classes coprime to 12
   - Theoretical value: 1/φ(12) = 1/4

5. **`heatmap_multiple_N.png`**: Heatmap visualization
   - Rows: Different N values (suggest N = 3,4,5,6,8,10,12)
   - Columns: Residue classes (or standardized bins)
   - Color intensity: Prime counts or densities
   - Include colorbar with label

6. **`creative_visualization.png`**: One additional visualization of your choice
   - Use your judgment to create an insightful view of the theorem
   - Could be: spiral plot, error convergence, comparative analysis, etc.
   - Must be mathematically meaningful

All plots must have:
- Clear titles
- Labeled axes with units
- Legends where appropriate
- Professional appearance (appropriate figure size, readable fonts)

### 4. `requirements.txt`
List all Python dependencies needed to run your code.
Use specific version constraints (e.g., `numpy>=1.24.0`).

## Technical Constraints

- **Python Version**: 3.9+
- **Code must be immediately executable**: No placeholders, no "TODO" comments
- **Mathematical notation**: Use proper LaTeX formatting in README where appropriate
- **Computing limits**: Sieve should handle at least N=1,000,000 efficiently
- **No external data sources**: Generate all data computationally

## Experimental Parameters

- **Temperature**: 0.6
- **Execution**: Single-shot (no debugging iteration)
- **Output format**: Raw file creation in current directory

## Instructions

1. Create all four files with complete, production-ready code
2. Ensure all code is executable without modification
3. Write clear, accessible explanations in the README
4. Make visualizations publication-quality

Begin generating the deliverables now.
