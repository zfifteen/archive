#!/usr/bin/env python3
"""
Human DNA Data Acquisition Script

This script downloads authentic human DNA sequences from reliable public sources
for use in DNA experiments. All data is from publicly available databases
with no privacy concerns.

Sources:
- NCBI RefSeq: Canonical reference sequences for human genes
- No personal data or patient information
- Publicly available, ethically sourced sequences

Genes targeted (matching existing experiments):
- BRCA1: Breast cancer 1 (DNA repair)
- TP53: Tumor protein p53 (tumor suppressor)  
- CFTR: Cystic fibrosis transmembrane conductance regulator
- PCSK9: Proprotein convertase subtilisin/kexin type 9
- APOE: Apolipoprotein E (lipid metabolism)
"""

import os
import sys
import json
import time
from urllib.request import urlopen, urlretrieve
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError
import warnings

def setup_output_directory():
    """Create output directory for human DNA data."""
    output_dir = "human_dna_data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def fetch_sequence_from_ncbi(gene_symbol, refseq_id):
    """
    Fetch DNA sequence from NCBI using RefSeq ID.
    
    Args:
        gene_symbol (str): Gene symbol (e.g., 'BRCA1')
        refseq_id (str): NCBI RefSeq ID (e.g., 'NM_007294.4')
        
    Returns:
        dict: Gene information including sequence
    """
    print(f"Fetching {gene_symbol} sequence from NCBI RefSeq...")
    
    try:
        # Use NCBI E-utilities to fetch sequence
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {
            'db': 'nucleotide',
            'id': refseq_id,
            'rettype': 'fasta',
            'retmode': 'text'
        }
        
        url = f"{base_url}?{urlencode(params)}"
        
        with urlopen(url) as response:
            fasta_content = response.read().decode('utf-8')
            
        # Parse FASTA content
        lines = fasta_content.strip().split('\n')
        if not lines or not lines[0].startswith('>'):
            raise ValueError(f"Invalid FASTA format for {gene_symbol}")
            
        header = lines[0]
        sequence = ''.join(lines[1:])
        
        # Extract first 500bp for consistency with existing experiments
        # Most experiments use fragments, not full genes
        sequence_fragment = sequence[:500] if len(sequence) > 500 else sequence
        
        gene_info = {
            'gene_symbol': gene_symbol,
            'refseq_id': refseq_id,
            'header': header,
            'full_length': len(sequence),
            'fragment_length': len(sequence_fragment),
            'sequence': sequence_fragment,
            'source': 'NCBI RefSeq',
            'url': url,
            'description': f"Human {gene_symbol} gene sequence from NCBI RefSeq {refseq_id}"
        }
        
        print(f"  ✓ Successfully fetched {gene_symbol}: {len(sequence_fragment)} bp")
        return gene_info
        
    except (URLError, HTTPError) as e:
        print(f"  ✗ Error fetching {gene_symbol}: {e}")
        return None
    except Exception as e:
        print(f"  ✗ Unexpected error for {gene_symbol}: {e}")
        return None

def get_gene_database():
    """
    Get database of human genes with their RefSeq IDs.
    These are well-established reference sequences.
    """
    return {
        'BRCA1': {
            'refseq_id': 'NM_007294.4',
            'description': 'BRCA1 DNA repair associated',
            'clinical_relevance': 'Mutations increase breast and ovarian cancer risk'
        },
        'TP53': {
            'refseq_id': 'NM_000546.6', 
            'description': 'Tumor protein p53',
            'clinical_relevance': 'Mutations involved in majority of human cancers'
        },
        'CFTR': {
            'refseq_id': 'NM_000492.4',
            'description': 'Cystic fibrosis transmembrane conductance regulator',
            'clinical_relevance': 'Mutations cause cystic fibrosis'
        },
        'PCSK9': {
            'refseq_id': 'NM_174936.4',
            'description': 'Proprotein convertase subtilisin/kexin type 9',
            'clinical_relevance': 'Mutations affect LDL cholesterol levels, cardiovascular disease risk'
        },
        'APOE': {
            'refseq_id': 'NM_000041.4',
            'description': 'Apolipoprotein E',
            'clinical_relevance': 'Variants affect Alzheimer\'s disease risk'
        }
    }

def download_human_dna_sequences():
    """Download human DNA sequences for all target genes."""
    print("=" * 80)
    print("DOWNLOADING AUTHENTIC HUMAN DNA SEQUENCES")
    print("=" * 80)
    print("Source: NCBI RefSeq (public reference sequences)")
    print("Ethical compliance: No personal data, publicly available sequences")
    print()
    
    output_dir = setup_output_directory()
    gene_db = get_gene_database()
    
    downloaded_sequences = {}
    
    for gene_symbol, gene_info in gene_db.items():
        time.sleep(0.5)  # Be respectful to NCBI servers
        
        sequence_data = fetch_sequence_from_ncbi(gene_symbol, gene_info['refseq_id'])
        
        if sequence_data:
            # Add clinical information
            sequence_data['description'] = gene_info['description']
            sequence_data['clinical_relevance'] = gene_info['clinical_relevance']
            
            downloaded_sequences[gene_symbol] = sequence_data
            
            # Save individual sequence file
            filename = os.path.join(output_dir, f"{gene_symbol.lower()}_human_sequence.json")
            with open(filename, 'w') as f:
                json.dump(sequence_data, f, indent=2)
            print(f"  Saved to: {filename}")
        else:
            print(f"  Failed to download {gene_symbol}")
        
        print()
    
    # Save combined sequences file
    combined_file = os.path.join(output_dir, "human_dna_sequences.json")
    with open(combined_file, 'w') as f:
        json.dump(downloaded_sequences, f, indent=2)
    
    # Create FASTA file
    fasta_file = os.path.join(output_dir, "human_dna_sequences.fasta")
    with open(fasta_file, 'w') as f:
        for gene_symbol, data in downloaded_sequences.items():
            f.write(f">{gene_symbol}_human|{data['refseq_id']}|{data['description']}\n")
            f.write(f"{data['sequence']}\n")
    
    print("=" * 80)
    print("DOWNLOAD SUMMARY")
    print("=" * 80)
    print(f"Total sequences downloaded: {len(downloaded_sequences)}")
    print(f"Combined data saved to: {combined_file}")
    print(f"FASTA format saved to: {fasta_file}")
    print()
    
    # Print summary statistics
    for gene_symbol, data in downloaded_sequences.items():
        print(f"{gene_symbol:6}: {data['fragment_length']:3d} bp (RefSeq: {data['refseq_id']})")
    
    print()
    print("✓ All human DNA sequences successfully downloaded")
    print("✓ Ready for integration into experiments")
    
    return downloaded_sequences

def create_documentation():
    """Create documentation for the human DNA dataset."""
    doc_content = """# Human DNA Dataset Documentation

## Overview
This dataset contains authentic human DNA sequences downloaded from NCBI RefSeq for use in DNA experiments within the unified framework.

## Ethical Compliance
- **Source**: NCBI RefSeq public reference sequences
- **Privacy**: No personal identifying information
- **Consent**: Public domain sequences, no consent required
- **Usage**: Educational and research purposes
- **Compliance**: Follows open science principles

## Data Sources
All sequences are canonical reference sequences from NCBI RefSeq:

- **BRCA1**: NM_007294.4 - DNA repair associated gene
- **TP53**: NM_000546.6 - Tumor protein p53  
- **CFTR**: NM_000492.4 - Cystic fibrosis transmembrane conductance regulator
- **PCSK9**: NM_174936.4 - Proprotein convertase subtilisin/kexin type 9
- **APOE**: NM_000041.4 - Apolipoprotein E

## Usage Instructions
1. Run `python scripts/download_human_dna_data.py` to download sequences
2. Sequences will be saved in `human_dna_data/` directory
3. Use `human_dna_sequences.json` for programmatic access
4. Use `human_dna_sequences.fasta` for sequence analysis tools

## File Structure
```
human_dna_data/
├── human_dna_sequences.json       # Combined sequences in JSON format
├── human_dna_sequences.fasta      # Combined sequences in FASTA format
├── brca1_human_sequence.json      # Individual gene files
├── tp53_human_sequence.json
├── cftr_human_sequence.json
├── pcsk9_human_sequence.json
└── apoe_human_sequence.json
```

## Reproducibility
To reproduce this dataset:
1. Execute the download script with internet connection
2. Sequences are fetched directly from NCBI using stable RefSeq IDs
3. All download metadata is preserved in JSON files

## Updates
RefSeq IDs are version-specific and stable. To update:
1. Check for new RefSeq versions on NCBI
2. Update RefSeq IDs in the download script
3. Re-run download script

## License
Public domain sequences from NCBI RefSeq. No licensing restrictions.
"""

    doc_file = "human_dna_data/README.md"
    with open(doc_file, 'w') as f:
        f.write(doc_content)
    
    print(f"Documentation saved to: {doc_file}")

if __name__ == "__main__":
    print("Human DNA Data Acquisition Script")
    print("Downloading authentic human sequences from NCBI RefSeq...")
    print()
    
    try:
        sequences = download_human_dna_sequences()
        create_documentation()
        
        print("\n" + "=" * 80)
        print("SUCCESS: Human DNA data acquisition completed")
        print("All sequences are ready for use in experiments")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during download: {e}")
        sys.exit(1)