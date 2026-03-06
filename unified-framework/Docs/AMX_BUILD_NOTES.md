# AMX Build Notes

## Issue Resolution

The reported build error with `amx.h` not being found appears to have been resolved. The current codebase does not contain any references to `amx.h` includes.

## Proper AMX Target Usage

### From Main Project Directory (Recommended)
```bash
cd /path/to/unified-framework
make test-amx                 # Run AMX functionality tests
make test-amx-integration     # Run AMX integration tests
make bench-amx               # Run AMX performance benchmarks
make amx-build               # Build with AMX optimization
```

### From src/c Directory (Now Supported)
```bash
cd /path/to/unified-framework/src/c
make test-amx                 # Run AMX functionality tests
make test-amx-integration     # Run AMX integration tests
make bench-amx               # Run AMX performance benchmarks
make amx-build               # Build with AMX optimization
```

## Build Requirements

- Apple M1 Max for optimal AMX performance
- Standard C compiler (clang recommended)
- No external AMX libraries required (uses built-in intrinsics)

## Troubleshooting

1. **"No rule to make target 'test-amx'"**: 
   - Ensure you're using the updated Makefile
   - Try running from the main project directory

2. **"amx.h file not found"**:
   - This error should no longer occur in the current codebase
   - Clean build artifacts: `make clean`
   - Check for old cached files

3. **OpenMP errors on non-macOS platforms**:
   - Install OpenMP development libraries
   - Or build with OpenMP disabled: `make CFLAGS="-DZ5D_USE_OMP=0"`

## Files Modified

- `src/c/Makefile`: Added AMX targets and executables
- Enhanced AMX target documentation in help
- Added proper AMX build instructions