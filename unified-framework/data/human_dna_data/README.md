# Human DNA Dataset Documentation

## Overview
This dataset contains authentic human DNA sequences from NCBI RefSeq for use in DNA experiments within the unified framework.

## Ethical Compliance
- **Source**: NCBI RefSeq public reference sequences
- **Privacy**: No personal identifying information
- **Consent**: Public domain sequences, no consent required
- **Usage**: Educational and research purposes
- **Compliance**: Follows open science principles and ethical guidelines

## Data Sources
All sequences are canonical reference sequences from NCBI RefSeq:

| Gene  | RefSeq ID    | Description | Clinical Relevance |
|-------|--------------|-------------|-------------------|
| BRCA1 | NM_007294.4  | DNA repair associated | Mutations increase breast and ovarian cancer risk |
| TP53  | NM_000546.6  | Tumor protein p53 | Mutations involved in majority of human cancers |
| CFTR  | NM_000492.4  | Cystic fibrosis transmembrane conductance regulator | Mutations cause cystic fibrosis |
| PCSK9 | NM_174936.4  | Proprotein convertase subtilisin/kexin type 9 | Mutations affect LDL cholesterol levels |
| APOE  | NM_000041.4  | Apolipoprotein E | Variants affect Alzheimer's disease risk |

## Sequence Details
- **Fragment Size**: 500 base pairs from 5' end of coding sequence
- **Quality**: Canonical reference sequences from NCBI
- **Format**: Both JSON and FASTA formats provided
- **Validation**: Cross-referenced with NCBI RefSeq database

## Usage Instructions
1. Sequences are ready for immediate use in experiments
2. Use `human_dna_sequences.json` for programmatic access
3. Use `human_dna_sequences.fasta` for sequence analysis tools
4. Individual gene files available for specific analyses

## File Structure
```
human_dna_data/
├── README.md                      # This documentation
├── human_dna_sequences.json       # Combined sequences in JSON format
├── human_dna_sequences.fasta      # Combined sequences in FASTA format
├── brca1_human_sequence.json      # Individual gene files
├── tp53_human_sequence.json
├── cftr_human_sequence.json
├── pcsk9_human_sequence.json
└── apoe_human_sequence.json
```

## Reproducibility
These sequences can be verified by:
1. Checking RefSeq IDs against NCBI database
2. Comparing with sequences in NCBI GenBank
3. Using NCBI BLAST to confirm sequence identity

## Quality Assurance
- All sequences manually verified against NCBI RefSeq
- RefSeq IDs are stable and version-specific
- Sequences represent canonical human reference genome

## License and Terms
- Public domain sequences from NCBI RefSeq
- No licensing restrictions for research and educational use
- Attribution to NCBI RefSeq appreciated but not required

## Contact
For questions about this dataset, refer to the unified-framework documentation.
