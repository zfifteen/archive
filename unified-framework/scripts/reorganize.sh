 #!/bin/bash
 
 # Unified-Framework Repository Reorganization Script
 # This script moves all loose files into appropriate directories
 
 echo "Starting repository reorganization..."
 
 # Create standard directories
 mkdir -p docs scripts tests data results bin docs/assets
 echo "Created directories: docs/, scripts/, tests/, data/, results/, bin/, docs/assets/"
 
 # Move documentation files (keep README.md and AGENTS.md in root)
 echo "Moving documentation files..."
 find . -maxdepth 1 -name "*.md" ! -name "README.md" ! -name "AGENTS.md" -exec mv {} docs/ \;
 
 # Move Python files by category
 echo "Moving Python files..."
 for file in demo_*.py; do [ -f "$file" ] && mv "$file" scripts/ && echo "Moved $file to scripts/"; done
 for file in test_*.py validate_*.py; do [ -f "$file" ] && mv "$file" tests/ && echo "Moved $file to tests/"; done
 find . -maxdepth 1 -name "*.py" -exec mv {} src/ \; 2>/dev/null
 
 # Move data files
 echo "Moving data files..."
 find . -maxdepth 1 \( -name "*.csv" -o -name "*.json" \) -exec mv {} data/ \;
 find . -maxdepth 1 -name "*log*.txt" -o -name "*results*.txt" -o -name "*bench*.txt" -exec mv {} results/ \;
 
 # Move source code
 echo "Moving source code..."
 find . -maxdepth 1 \( -name "*.c" -o -name "*.h" \) -exec mv {} src/c/ \;
 
 # Move executables
 echo "Moving executables..."
 find . -maxdepth 1 -type f -executable ! -name ".*" -exec mv {} bin/ \;
 
 # Move images
 echo "Moving images..."
 find . -maxdepth 1 -name "*.png" -exec mv {} docs/assets/ \;
 
 # Move remaining files
 echo "Moving remaining files..."
 find . -maxdepth 1 -name "*.txt" -exec mv {} results/ \; 2>/dev/null
 find . -maxdepth 1 -name "*.json" -exec mv {} data/ \; 2>/dev/null
 find . -maxdepth 1 -name "*.md" ! -name "README.md" ! -name "AGENTS.md" -exec mv {} docs/ \; 2>/dev/null
 
 echo "Repository reorganization complete!"
 echo ""
 echo "Final structure:"
 echo "├── src/           # Source code"
 echo "├── docs/          # Documentation"
 echo "├── scripts/       # Demo scripts"
 echo "├── tests/         # Test files"
 echo "├── data/          # Data files"
 echo "├── results/       # Logs and results"
 echo "├── bin/           # Executables"
 echo "└── [clean root]   # Only essential files"
