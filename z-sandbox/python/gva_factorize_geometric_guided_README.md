# Geometric-Guided GVA Factorization

This module demonstrates **true geometric-guided factorization** where torus embeddings and geodesic distances are used to **prioritize candidates BEFORE** divisibility testing.

## Key Distinction

### Traditional GVA (`gva_factorize.py`)
```
Classical search → N % p test → Primality → Balance → THEN geometry validation
```
Geometry validates factors found classically; it does NOT guide the search.

### Geometric-Guided GVA (this module)
```
Generate all candidates → Compute ALL embeddings → Sort by geodesic distance → 
Test N % p in GEOMETRY-ORDERED sequence
```
Geometry orders the search, prioritizing geometrically plausible candidates.

## Usage

```python
from gva_factorize_geometric_guided import gva_factorize_geometric_guided

# Factor a 64-bit semiprime with geometry guiding the search
N = 18446736050711510819  # Example
p, q, dist, tried = gva_factorize_geometric_guided(N, R=100000, top_k=5000)

if p:
    print(f"Found: {p} × {q}")
    print(f"Tested {tried} candidates (geometry-ordered)")
else:
    print("Factor not found in top geometric candidates")
```

## Parameters

- `N`: Semiprime to factor
- `R`: Search radius around sqrt(N) (default: 10,000,000)
- `top_k`: Number of top geometric candidates to test (default: 1,000)

## Performance

The method:
1. **Phase 1**: Computes torus embeddings for all 2R+1 candidates (parallelized)
2. **Phase 2**: Sorts candidates by geodesic distance (O(n log n))
3. **Phase 3**: Tests divisibility in geometry-ordered sequence

This demonstrates geometry actively guiding the factor search, not just validating after the fact.

## Example Output

```
GEOMETRIC-GUIDED GVA: N = 143 (8 bits)
Computing embeddings for 11 candidates...
Valid candidates: 11
Testing top 5 geometric candidates in distance-ordered sequence...
GEOMETRIC VICTORY after 1 candidates!
True factor found at geometry rank 1/11
SUCCESS: 11 × 13 = 143
```

The output shows:
- Geometry placed the true factor at rank 1 (top of the list)
- Only 1 candidate needed testing (vs. linear scan which might test many)
- This demonstrates geometry successfully guiding the search

## Limitations

- Computational cost: O(2R+1) embeddings must be computed upfront
- Not guaranteed: Geometry may not always place true factors in top-k
- Works best for balanced semiprimes where geometric structure is clearer

## Honest Assessment

This implementation demonstrates that **geometry CAN guide factor search** when:
1. The geometric embedding captures relevant structure
2. True factors have distinct geodesic signatures
3. The search radius R is appropriate

However, it's computationally expensive (must compute all embeddings first) and 
not guaranteed to succeed. It represents a research direction, not a production 
factorization method.

## Comparison to Classical GVA

| Aspect | Classical GVA | Geometric-Guided |
|--------|---------------|------------------|
| Search order | Linear (sqrt(N) ± d) | Geometry-ordered |
| When geometry used | After divisibility test | Before divisibility test |
| Claim accuracy | "Geometric validation" ✓ | "Geometric guidance" ✓ |
| Computational cost | Low (only test what divides) | High (compute all embeddings) |
| Success guarantee | Same as linear scan | Depends on top_k size |

## Testing

Run the test suite:
```bash
python3 tests/test_gva_geometric_guided.py
```

This verifies that:
- Embeddings are computed for all candidates before testing
- Candidates are sorted by geodesic distance
- Divisibility testing follows geometry-ordered sequence
