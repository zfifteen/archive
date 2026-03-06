#!/usr/bin/env python3
"""
Mission Charter Compliance Validator

This tool validates that deliverables conform to the 10-point Mission Charter.
It checks for the presence and completeness of all required charter elements.

Usage:
    python tools/validate_charter.py <deliverable_file> [options]

Options:
    --strict            Fail on warnings (default: False)
    --manifest-only     Generate manifest without validation (default: False)
    --output FILE       Output manifest to FILE (default: stdout)
    --template TYPE     Deliverable type for validation (default: auto-detect)
"""

import sys
import argparse
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional


# Charter element patterns - headings that indicate presence of each element
CHARTER_ELEMENTS = {
    "first_principles": [
        r"#+\s*First\s+Principles",
        r"#+\s*Axioms",
        r"#+\s*Definitions",
    ],
    "ground_truth": [
        r"#+\s*Ground\s+Truth",
        r"#+\s*Provenance",
        r"#+\s*Ground\s+Truth\s+(&|and)\s+Provenance",
    ],
    "reproducibility": [
        r"#+\s*Reproducibility",
        r"#+\s*Reproduction",
        r"#+\s*How\s+to\s+Reproduce",
    ],
    "failure_knowledge": [
        r"#+\s*Failure\s+Knowledge",
        r"#+\s*Failure\s+Modes?",
        r"#+\s*Known\s+Issues",
        r"#+\s*Limitations",
    ],
    "constraints": [
        r"#+\s*Constraints",
        r"#+\s*Legal\s+(&|and)\s+Ethical",
        r"#+\s*Compliance",
    ],
    "context": [
        r"#+\s*Context",
        r"#+\s*Background",
        r"#+\s*Motivation",
    ],
    "models_limits": [
        r"#+\s*Models?\s+(&|and)\s+Limits",
        r"#+\s*Assumptions",
        r"#+\s*Validity\s+Range",
    ],
    "interfaces": [
        r"#+\s*Interfaces?",
        r"#+\s*Commands?",
        r"#+\s*API",
        r"#+\s*I/?O",
    ],
    "calibration": [
        r"#+\s*Calibration",
        r"#+\s*Parameters?",
        r"#+\s*Tuning",
    ],
    "purpose": [
        r"#+\s*Purpose",
        r"#+\s*Goals?",
        r"#+\s*Success\s+Criteria",
        r"#+\s*Objectives?",
    ],
}

# Required sub-elements for each charter element (for completeness scoring)
REQUIRED_CONTENT = {
    "first_principles": ["axiom", "definition", "unit"],
    "ground_truth": ["source", "timestamp", "author"],
    "reproducibility": ["command", "version", "seed", "environment"],
    "failure_knowledge": ["failure", "diagnostic", "mitigation"],
    "constraints": ["legal", "ethical", "safety"],
    "context": ["who", "what", "when", "where", "why"],
    "models_limits": ["assumption", "validity", "range"],
    "interfaces": ["command", "environment", "path"],
    "calibration": ["value", "rationale", "validation"],
    "purpose": ["goal", "metric", "success"],
}


def parse_deliverable(content: str) -> Dict[str, List[Tuple[int, str]]]:
    """
    Parse deliverable content and identify charter elements.
    
    Returns:
        Dict mapping element names to list of (line_number, heading) tuples
    """
    elements_found = {element: [] for element in CHARTER_ELEMENTS}
    
    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        for element, patterns in CHARTER_ELEMENTS.items():
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    elements_found[element].append((line_num, line.strip()))
                    break
    
    return elements_found


def extract_section_content(content: str, start_line: int) -> str:
    """
    Extract content of a section starting at start_line until next heading.
    
    Args:
        content: Full document content
        start_line: Line number from parse_deliverable() - this is 1-indexed
                   from enumerate(lines, 1)
    
    Returns:
        Section content as string (excluding the heading itself)
    
    Indexing Explanation:
        parse_deliverable() uses enumerate(lines, 1) which returns:
          - line_num=1 for lines[0]
          - line_num=2 for lines[1]  <- If this is the heading
          - line_num=3 for lines[2]  <- First content line
        
        So when start_line=2 (heading at array index 1):
          lines[start_line:] = lines[2:] starts from array index 2
        This correctly skips the heading and gets content.
    """
    lines = content.split('\n')
    section_lines = []
    
    # start_line from enumerate(lines, 1) is offset by +1 from array index
    # So lines[start_line:] correctly starts after the heading
    for line in lines[start_line:]:
        # Stop at next heading (markdown # or ##)
        if line.strip().startswith('#'):
            break
        section_lines.append(line)
    
    return '\n'.join(section_lines)


def calculate_completeness(element: str, section_content: str) -> float:
    """
    Calculate completeness score for a charter element (0.0 to 1.0).
    
    Based on presence of required content keywords.
    """
    if element not in REQUIRED_CONTENT:
        return 1.0
    
    required = REQUIRED_CONTENT[element]
    found_count = 0
    
    content_lower = section_content.lower()
    for keyword in required:
        if keyword in content_lower:
            found_count += 1
    
    return found_count / len(required) if required else 1.0


def validate_charter_compliance(
    file_path: Path,
    strict: bool = False
) -> Tuple[Dict, List[str], List[str]]:
    """
    Validate a deliverable for charter compliance.
    
    Returns:
        (compliance_dict, missing_elements, warnings)
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Deliverable file not found: {file_path}")
    
    content = file_path.read_text(encoding='utf-8')
    elements_found = parse_deliverable(content)
    
    compliance = {}
    missing_elements = []
    warnings = []
    
    for element in CHARTER_ELEMENTS.keys():
        if elements_found[element]:
            # Element is present
            line_num, heading = elements_found[element][0]
            section_content = extract_section_content(content, line_num)
            completeness = calculate_completeness(element, section_content)
            
            compliance[element] = {
                "present": True,
                "location": f"{heading} (line {line_num})",
                "completeness": completeness,
                "notes": ""
            }
            
            # Add warning if completeness is low
            if completeness < 0.7:
                warning = f"{element}: Section may be incomplete (completeness: {completeness:.1%})"
                warnings.append(warning)
                compliance[element]["notes"] = f"Low completeness score: {completeness:.1%}"
        else:
            # Element is missing
            compliance[element] = {
                "present": False,
                "location": "NOT FOUND",
                "completeness": 0.0,
                "notes": "Required element missing"
            }
            missing_elements.append(element)
    
    return compliance, missing_elements, warnings


def generate_manifest(
    file_path: Path,
    compliance: Dict,
    missing_elements: List[str],
    warnings: List[str],
    deliverable_type: Optional[str] = None,
    author: Optional[str] = None
) -> Dict:
    """
    Generate a charter compliance manifest.
    """
    manifest = {
        "manifest_version": "1.0.0",
        "deliverable_id": file_path.stem,
        "deliverable_type": deliverable_type or "unknown",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "author": author or "unknown",
        "charter_compliance": compliance,
        "validation_result": {
            "is_compliant": len(missing_elements) == 0,
            "missing_elements": missing_elements,
            "warnings": warnings
        }
    }
    
    return manifest


def main():
    parser = argparse.ArgumentParser(
        description="Validate deliverable for Mission Charter compliance"
    )
    parser.add_argument(
        "deliverable",
        type=Path,
        help="Path to deliverable file (markdown)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on warnings (not just missing elements)"
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Generate manifest without validation messages"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output manifest to file (default: stdout)"
    )
    parser.add_argument(
        "--template",
        choices=["spec", "pr", "code", "research_note", "log", "runbook", "design", "plan", "report"],
        help="Deliverable type"
    )
    parser.add_argument(
        "--author",
        default="unknown",
        help="Author/creator of deliverable"
    )
    
    args = parser.parse_args()
    
    try:
        # Validate charter compliance
        compliance, missing_elements, warnings = validate_charter_compliance(
            args.deliverable,
            strict=args.strict
        )
        
        # Generate manifest
        manifest = generate_manifest(
            args.deliverable,
            compliance,
            missing_elements,
            warnings,
            deliverable_type=args.template,
            author=args.author
        )
        
        # Output manifest
        manifest_json = json.dumps(manifest, indent=2)
        
        if args.output:
            args.output.write_text(manifest_json, encoding='utf-8')
            if not args.manifest_only:
                print(f"Manifest written to: {args.output}")
        else:
            if not args.manifest_only:
                print("=" * 70)
                print("MISSION CHARTER COMPLIANCE VALIDATION")
                print("=" * 70)
                print()
            print(manifest_json)
            if not args.manifest_only:
                print()
        
        # Print validation summary (if not manifest-only)
        if not args.manifest_only:
            print("=" * 70)
            print("VALIDATION SUMMARY")
            print("=" * 70)
            
            if manifest["validation_result"]["is_compliant"]:
                print("✓ COMPLIANT: All charter elements present")
            else:
                print("✗ NON-COMPLIANT: Missing required elements")
            
            print()
            print(f"File: {args.deliverable}")
            print(f"Elements Present: {sum(1 for e in compliance.values() if e['present'])}/10")
            print(f"Missing Elements: {len(missing_elements)}")
            print(f"Warnings: {len(warnings)}")
            
            if missing_elements:
                print()
                print("MISSING ELEMENTS:")
                for element in missing_elements:
                    print(f"  - {element}")
            
            if warnings:
                print()
                print("WARNINGS:")
                for warning in warnings:
                    print(f"  - {warning}")
            
            print()
        
        # Exit code
        if missing_elements:
            sys.exit(1)
        elif args.strict and warnings:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
