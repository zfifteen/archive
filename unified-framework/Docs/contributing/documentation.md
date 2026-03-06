# Documentation Guidelines

## Overview

Guidelines for writing and maintaining documentation for the Z Framework.

## Documentation Structure

### Organization
- Main documentation in `docs/` directory
- API reference in `docs/api/`
- User guides in `docs/guides/`
- Examples in `docs/examples/`

### File Naming
- Use lowercase with hyphens: `getting-started.md`
- Be descriptive and specific
- Group related documents in subdirectories

## Writing Style

### Scientific Accuracy
- All mathematical claims must be empirically validated
- Clearly distinguish between proven results and hypotheses
- Include statistical confidence intervals where applicable
- Use precise mathematical notation

### Clarity and Accessibility
- Write for both novice and expert users
- Include code examples for practical concepts
- Use clear, concise language
- Structure content with headings and lists

### Consistency
- Use consistent terminology throughout
- Follow the universal form notation: Z = A(B/c)
- Reference the same parameter names as in code

## Mathematical Documentation

### Equations
- Use LaTeX notation for mathematical expressions
- Include derivations for complex formulas
- Provide numerical examples

### Validation Results
- Include confidence intervals: CI [14.6%, 15.4%]
- Report statistical significance: p < 10⁻⁶
- Document test parameters and methodologies

## Code Documentation

### Examples
- Provide working code examples
- Include expected outputs
- Show both basic and advanced usage

### API Documentation
- Document all parameters and return values
- Include type hints
- Provide usage examples

## Link Guidelines

### Internal Links
- Use relative paths for internal links
- Keep links up to date with file reorganizations
- Test all links before committing

### External Links
- Verify external links are stable
- Include fallback documentation for critical external resources

## See Also

- [Contributing Guidelines](guidelines.md)
- [Code Standards](code-standards.md)