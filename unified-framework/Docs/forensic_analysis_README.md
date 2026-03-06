# Forensic Claim Analysis System

This system analyzes medical forensic reports and generates traceability reports mapping claims against VA findings to identify discrepancies and contradictions in medical assessments.

## Features

- **Medical Forensic Report Parsing**: Extracts structured claims from narrative forensic reports
- **Claim Categorization**: Classifies claims (traumatic, degenerative, methodological critique, etc.)
- **VA Findings Mapping**: Maps forensic claims against corresponding VA report findings
- **Contradiction Detection**: Identifies high-confidence contradictions between assessments
- **Professional PDF Reports**: Generates comprehensive traceability reports with analysis and recommendations

## Quick Start - Patient A Analysis

Generate the traceability report for Patient A:

```bash
python generate_patient_a_report_standalone.py
```

This will:
1. Analyze the medical forensic report from the issue description
2. Extract and categorize medical claims
3. Map claims against VA findings 
4. Generate a comprehensive PDF traceability report in `reports/`

## Generated Report Contents

The PDF report includes:

- **Executive Summary**: Overview of contradictions and discrepancies
- **Claims Analysis**: Detailed breakdown of forensic claims by category
- **Traceability Mapping**: Claim-to-findings mapping with status and confidence scores
- **Detailed Comparisons**: In-depth analysis of contradicted findings
- **Conclusions & Recommendations**: Clinical significance and next steps

## Key Results for Patient A

- **9 medical claims** extracted from forensic evaluation
- **4 high-confidence contradictions** identified with VA assessments
- **11 specific discrepancies** documented across anatomical regions
- **Primary contradictions**: Vertebral morphology (wedge deformities vs "normal heights")
- **Methodological critiques**: Imaging protocol limitations in VA assessments

## System Architecture

```
src/applications/forensic_claim_analysis/
├── claim_analyzer.py      # Extracts and categorizes medical claims
├── findings_mapper.py     # Maps claims to VA findings  
├── report_generator.py    # Generates professional PDF reports
└── __init__.py           # Module interface
```

## Testing

Validate the system functionality:

```bash
python test_forensic_analysis.py
```

## Dependencies

- `reportlab` - PDF generation
- `pandas` - Data processing  
- `numpy` - Numerical operations

## Clinical Applications

This system addresses critical needs in:

- **Medical-Legal Analysis**: Objective comparison of conflicting medical assessments
- **Quality Assurance**: Identification of diagnostic discrepancies in healthcare systems
- **Disability Evaluations**: Evidence-based assessment of claim validity
- **Healthcare Improvement**: Systematic identification of diagnostic gaps and methodological issues

The forensic analysis system provides objective, traceable evidence to support medical decision-making and improve diagnostic accuracy.