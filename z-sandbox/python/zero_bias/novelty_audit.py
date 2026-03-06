"""
Novelty audit utilities for zero-bias resonance validation.

Scans codebase for classical factoring algorithm references.
"""

import os
import re
from typing import List, Dict

def scan_for_classical_algorithms(search_paths: List[str], output_path: str) -> Dict:
    """
    Scan codebase for classical factoring algorithm references.

    Args:
        search_paths: List of directories to scan
        output_path: Path to save audit results

    Returns:
        Audit results dictionary
    """
    forbidden_patterns = [
        r'ECM|ecm',
        r'Pollard|pollard',
        r'rho',
        r'NFS|nfs',
        r'MPQS|msieve',
        r'qsieve',
        r'yafu',
        r'nextProbablePrime',
        r'probablePrime'  # Allow only in verifier, not factorization
    ]

    hits = []
    files_scanned = 0

    for path in search_paths:
        if not os.path.exists(path):
            continue

        for root, dirs, files in os.walk(path):
            # Skip certain directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'build', 'target']]

            for file in files:
                if not file.endswith(('.java', '.py', '.cpp', '.c')):
                    continue

                files_scanned += 1
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                        for pattern in forbidden_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                hits.append({
                                    'file': file_path,
                                    'pattern': pattern,
                                    'matches': matches
                                })
                except Exception as e:
                    # Skip files that can't be read
                    continue

    result = {
        "audit_id": "novelty_audit_001",
        "grep_terms": forbidden_patterns,
        "files_scanned": files_scanned,
        "hits": hits,
        "generated_at": "2025-11-08T12:00:00Z",  # Would use actual timestamp
        "output_path": output_path
    }

    # Save results
    import json
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    return result