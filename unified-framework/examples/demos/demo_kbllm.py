#!/usr/bin/env python3
"""
KBLLM.txt Demo Script - Demonstrates knowledge base usage for LLM processing

This script shows how to parse and utilize the token-chain structured knowledge
base for automated LLM instruction generation and concept extraction.
"""

def parse_kbllm_file(filepath="docs/knowledge-base/KBLLM.txt"):
    """Parse KBLLM.txt file and extract structured knowledge."""
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Extract sections
    sections = {}
    current_section = None
    current_content = []
    
    for line in content.split('\n'):
        if line and not line.startswith(' ') and ('---' in line or '===' in line):
            continue
        elif line and not line.startswith(' ') and ':' not in line and line.isupper():
            # New section header
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = line.strip()
            current_content = []
        elif line.strip():
            current_content.append(line)
    
    # Add final section
    if current_section:
        sections[current_section] = '\n'.join(current_content)
    
    return sections

def extract_token_chains(text):
    """Extract token-chain sequences from text."""
    chains = []
    for line in text.split('\n'):
        if '→' in line:
            chains.append(line.strip())
    return chains

def get_empirical_validations(sections):
    """Extract empirical validation metrics."""
    validations = {}
    
    if 'EMPIRICAL VALIDATIONS (TC01-TC05 SUITE)' in sections:
        content = sections['EMPIRICAL VALIDATIONS (TC01-TC05 SUITE)']
        for line in content.split('\n'):
            if 'TC0' in line and ':' in line:
                parts = line.split(':')
                test_name = parts[0].strip()
                description = parts[1].strip() if len(parts) > 1 else ""
                validations[test_name] = description
    
    return validations

def main():
    """Demonstrate KBLLM.txt usage."""
    
    print("Z-FRAMEWORK KNOWLEDGE BASE DEMO")
    print("=" * 50)
    
    # Parse the knowledge base
    try:
        sections = parse_kbllm_file()
        print(f"✓ Successfully loaded {len(sections)} knowledge sections")
        
        # Show section overview
        print("\nKNOWLEDGE SECTIONS:")
        for i, section in enumerate(sections.keys(), 1):
            print(f"{i:2}. {section}")
        
        # Extract and display token chains
        print(f"\nTOKEN-CHAIN EXAMPLES:")
        all_chains = []
        for section_content in sections.values():
            all_chains.extend(extract_token_chains(section_content))
        
        # Show first 5 token chains
        for i, chain in enumerate(all_chains[:5], 1):
            print(f"{i}. {chain}")
        
        print(f"\nTotal token-chains found: {len(all_chains)}")
        
        # Show empirical validation summary
        validations = get_empirical_validations(sections)
        print(f"\nEMPIRICAL VALIDATIONS FOUND: {len(validations)}")
        for test, desc in validations.items():
            print(f"• {test}: {desc[:60]}...")
        
        # Show key metrics
        full_text = '\n'.join(sections.values())
        key_metrics = {
            'Optimal k*': 'k_star ≈ 0.3' in full_text,
            'Conditional Best-Bin Uplift': 'conditional_best_bin_uplift' in full_text,
            'Statistical Significance': 'p<10^-6' in full_text,
            'Zeta Correlation': 'pearson_r=0.93' in full_text,
            'High Precision': 'mpmath_dps=50' in full_text
        }
        
        print(f"\nKEY METRICS VALIDATION:")
        for metric, found in key_metrics.items():
            status = "✓" if found else "✗"
            print(f"{status} {metric}")
        
        print(f"\nKNOWLEDGE BASE READY FOR LLM PROCESSING")
        
    except FileNotFoundError:
        print("✗ KBLLM.txt not found. Please ensure file exists in docs/knowledge-base/ directory.")
    except Exception as e:
        print(f"✗ Error processing knowledge base: {e}")

if __name__ == "__main__":
    main()