# AMX-Lab

A research repository for Apple Matrix Extension (AMX) on Apple Silicon (M1-M4). This project implements AMX-accelerated mathematical algorithms using tiled outer products and matrix operations.

## Overview

AMX-Lab provides repository-agnostic agent definitions for math-heavy code optimization on Apple Silicon. The focus is on designing and implementing AMX-first algorithms that treat the Apple AMX matrix coprocessor as the primary execution target.

## What is AMX?

AMX (Apple Matrix Extension) is a hardware matrix/outer-product coprocessor integrated into Apple Silicon processors (M1, M2, M3, M4 families). Key characteristics:

- Operates on tiles of data stored in dedicated X/Y/Z register files
- Excels at small matrix multiplies and outer products via specialized instructions
- Designed for batched, tiled matrix operations with regular access patterns and high arithmetic intensity

## Features

- **AMX-First Design**: All mathematical algorithms prioritize AMX implementation
- **Tile-Based Operations**: Algorithms structured for AMX's tile-based execution model
- **Repository-Agnostic**: Agent definitions can be reused across projects involving math-heavy code
- **Precision Control**: Explicit handling of accumulator widths, overflow, and rounding strategies
- **Validation Framework**: Includes correctness checks and deterministic comparisons

## Getting Started

### Prerequisites

- Apple Silicon Mac (M1, M2, M3, or M4)
- C/C++ compiler with inline assembly support
- Basic understanding of matrix operations and tiling strategies

### Project Structure

```
amx-lab/
├── .github/
│   └── META.md          # Repository metadata
├── AGENTS.md            # AMX Math Expert agent definition
├── experiments/         # AMX algorithm implementations
└── README.md           # This file
```

## Agent Definition

The repository includes a comprehensive AMX Math Expert agent (`AGENTS.md`) that:

- Enforces AMX-first implementation strategies
- Requires explanation-then-implementation workflow
- Maintains strict precision and correctness policies
- Provides decision checklists and validation expectations
- Integrates with the Z mathematical framework

## Design Principles

1. **AMX-First Mandate**: Prioritize AMX implementations for all substantial math operations
2. **Explain Then Implement**: Always provide natural-language explanation before code
3. **Precision Policy**: Explicitly state accumulator widths, overflow handling, and rounding
4. **No Fallbacks**: If AMX cannot be used, provide analysis instead of scalar alternatives
5. **Validation**: Include minimal correctness checks with deterministic comparisons

## Experiments

Work is organized under the `experiments/` directory with descriptive, incrementally-numbered folders:

- `001_<description>` - First experiment
- `002_<description>` - Second experiment
- etc.

Each experiment is self-contained and must not modify files outside its directory.

## Related Projects

- [corsix/amx](https://github.com/corsix/amx) - Apple AMX Instruction Set reference
- [z-amx](https://github.com/zfifteen/z-amx) - AMX framework (preferred when available)

## Contributing

This is a research repository focused on AMX algorithm development. Contributions should:

- Follow the AMX-first mandate
- Include both explanation and implementation
- Provide validation and correctness checks
- Document precision and performance characteristics

## License

See repository for license information.

## References

- Apple AMX Instruction Set: https://github.com/corsix/amx
- Z Framework Integration: See `AGENTS.md` for Z-specific guidance
