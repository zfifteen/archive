# Changelog

All notable changes to the unified-framework project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **Phase-2 candidate parity leak fixed**: z5d_phase2 now properly enforces odd candidates before Miller-Rabin testing. All pre-MR candidates are guaranteed to be odd through surgical parity enforcement in candidate generation logic.

### Added
- New comprehensive parity test suite (`tests/test_phase2_parity.c`) that validates ≥1e6 candidates
- Debug residue counters (compiled with `-DZ5D_DEBUG_RESIDUES`) to track mod 4 residue distribution
- Hard pre-MR assertion guards to prevent even candidates from reaching Miller-Rabin
- Geodesic delta computation with proper odd step enforcement

### Changed
- Candidate base generation now uses `base |= 1ULL` (bit-set) instead of toggle operations
- All increment/step/delta values are forced odd before addition to base
- Enhanced candidate generation in `next_phase2_candidate()` with parity-safe arithmetic

### Performance
- **Quarantined**: Previous `bench_z5d_phase2.out.txt` marked for performance/residue analysis verification
- Note: Prime values in quarantined benchmarks may still be correct but require separate re-verification due to residue distribution changes

## [Previous Versions]
- See git history for previous changes prior to parity leak fix