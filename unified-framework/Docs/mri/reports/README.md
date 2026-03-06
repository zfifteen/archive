# MRI Reports

This directory contains generated MRI analysis reports from the MRI Enhancement Tool.

## Structure

```
docs/mri/reports/
├── patient_a/
│   ├── spine_mri_analysis_report.pdf    # Main analysis report
│   └── annotations/                     # Annotated images with overlays
│       └── [series_uid]/
│           └── *.png                    # Individual annotated slices
```

## Report Generation

Reports are automatically generated via GitHub Actions workflow when:
- Manual trigger via `workflow_dispatch`
- Changes to MRI enhancement code or workflows

The analysis uses anonymized DICOM data and provides:
- Comprehensive PDF report with clinical findings
- Annotated PNG images with visual overlays
- Differentiation between traumatic vs degenerative changes
- Clinical validation metrics and references

## Data Security

- Patient data is anonymized by default (HIPAA compliant)
- PHI removal is enforced unless explicitly overridden with proper authorization
- All outputs are safe for documentation and version control