# RSA Weak Key Detector

## Overview

A cryptographic security tool that identifies potentially weak RSA keypairs by analyzing the prime gap distribution of their constituent primes against expected lognormal+ACF patterns.

## The Problem

RSA security depends on the computational difficulty of factoring the product of two large primes. However, not all prime pairs provide equal security:

- **Predictable Patterns**: If the primes used in RSA keys follow predictable gap distributions, they may be more susceptible to targeted attacks
- **Non-Random Selection**: Prime generation algorithms that don't produce truly random gap distributions create systematic weaknesses
- **Autocorrelation Vulnerabilities**: Strong autocorrelation in gap sequences indicates non-random prime selection that could be exploited

Traditional RSA key validation only checks primality and bit length—it doesn't validate the randomness of the underlying gap distribution.

## How It Works

### Detection Method

1. **Extract Primes**: Factor or extract the two primes from an RSA public key
2. **Analyze Local Gap Context**: Examine the prime gap distribution in the neighborhood of each prime
3. **Compare to Model**: Test whether the gap distribution matches the expected lognormal+ACF baseline established by zfifteen's research
4. **Flag Anomalies**: Identify keys whose primes fall in statistically suspicious regions of gap-space

### Statistical Tests

- **Lognormal Conformity**: Do the gaps around these primes fit the μ and σ parameters for their scale?
- **ACF Pattern Matching**: Does the gap sequence show the expected autocorrelation structure with lag-1 and lag-3 signatures?
- **Boundary Detection**: Are the primes suspiciously close to scale boundaries where distribution parameters shift?
- **Multi-Dimensional Deviation**: Does the 5-dimensional representation (Z5D) show anomalous clustering?

### Risk Scoring

Each keypair receives a composite risk score based on:
- Deviation from expected lognormal parameters (99.99% PNT accuracy baseline)
- Violation of 100% lognormal band containment
- Autocorrelation anomalies (expected 98%+ at specific lags)
- Proximity to known weak prime families

## Use Cases

### Key Generation Validation
- Validate newly generated RSA keys before deployment
- Audit key generation algorithms for statistical bias
- Ensure cryptographic libraries produce truly random primes

### Security Auditing
- Scan existing keypairs for potential weaknesses
- Identify keys that may be vulnerable to gap-pattern attacks
- Prioritize key rotation for high-risk certificates

### Cryptanalysis Research
- Study the relationship between gap distribution and factorability
- Identify patterns in successfully factored historical keys
- Develop new attack vectors based on statistical prime properties

### Compliance and Certification
- Meet requirements for cryptographic randomness
- Provide evidence of key quality for security certifications
- Document gap-distribution properties for compliance audits

## Implementation Architecture

### Input Layer
- PEM/DER public key parsing
- Manual (n, e) input
- Certificate chain analysis
- Bulk key scanning from directories

### Analysis Engine
- Prime extraction (if possible) or gap inference from modulus
- Local gap distribution calculation
- Statistical comparison to research baseline
- Multi-scale analysis for different bit-lengths

### Scoring System
- Individual prime risk assessment
- Keypair composite score
- Confidence intervals and error bounds
- Historical comparison database

### Output Layer
- Risk classification (Secure/Weak/Vulnerable)
- Detailed statistical report
- Visualization of gap distribution vs. expected
- Recommendations for key replacement

## Technical Requirements

### Performance
- Real-time analysis for standard RSA key sizes (2048-4096 bit)
- Batch processing capability for large key sets
- Scalable architecture for enterprise deployment

### Accuracy
- Leverage zfifteen's validated lognormal+ACF model
- Maintain 99.99% baseline accuracy from PNT
- Update model as new research findings emerge

### Integration
- Command-line interface for scripting
- REST API for service integration
- Library interface for embedded use
- Plugin architecture for key management systems

## Research Foundation

This application is made possible by zfifteen's empirical findings:
- **99.99% PNT accuracy**: High-precision prediction of expected gap distributions
- **100% lognormal band containment**: All observed gaps fit within distribution boundaries
- **98% ACF correlation**: Strong lag-1 and lag-3 autocorrelation signatures
- **Scale-dependent parameters**: μ and σ shift predictably with prime magnitude

Traditional cryptography assumes all large primes are equally random. This tool exploits the discovery that prime gap distributions follow predictable statistical patterns—and deviations from those patterns may indicate weakness.

## Future Enhancements

- Real-time certificate monitoring
- Integration with CT log scanning
- Machine learning for anomaly detection
- Gap-pattern attack simulation
- Quantum-resistance correlation analysis
