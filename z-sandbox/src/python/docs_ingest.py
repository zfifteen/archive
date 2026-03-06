#!/usr/bin/env python3
"""
Ingest loose root-level Markdown files into docs/ directory structure.

Reads configuration from docs/ingest.yml and moves files according to
pattern-based rules. Supports dry-run mode for testing.
"""

import argparse
import fnmatch
import shutil
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


CONFIG_FILE = Path('docs/ingest.yml')


def load_config():
    """Load and validate ingestion configuration."""
    if not CONFIG_FILE.exists():
        print(f"ERROR: Configuration file not found: {CONFIG_FILE}", file=sys.stderr)
        sys.exit(1)

    with CONFIG_FILE.open('r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Validate structure
    if not isinstance(config.get('exclude_globs'), list):
        config['exclude_globs'] = []
    if not isinstance(config.get('destination_map'), list):
        config['destination_map'] = []
    if not config.get('default_dest'):
        config['default_dest'] = 'docs/misc/'

    return config


def should_exclude(filename: str, exclude_globs: list) -> bool:
    """Check if file matches any exclude pattern."""
    for pattern in exclude_globs:
        if fnmatch.fnmatch(filename, pattern):
            return True
    return False


def find_destination(filename: str, destination_map: list, default_dest: str) -> str:
    """Find destination directory based on pattern matching."""
    for rule in destination_map:
        pattern = rule.get('pattern')
        dest = rule.get('dest')
        if pattern and dest and fnmatch.fnmatch(filename, pattern):
            return dest
    return default_dest


def ingest_file(filepath: Path, destination: str, dry_run: bool) -> bool:
    """
    Move file to destination directory.

    Returns True if file was moved (or would be moved in dry-run).
    """
    dest_dir = Path(destination)
    dest_file = dest_dir / filepath.name

    if dest_file.exists():
        print(f"SKIP: {filepath} -> {dest_file} (already exists)")
        return False

    if dry_run:
        print(f"DRY-RUN: {filepath} -> {dest_file}")
        return True

    # Create destination directory if needed
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Move file
    shutil.move(str(filepath), str(dest_file))
    print(f"MOVED: {filepath} -> {dest_file}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Ingest loose root-level Markdown files into docs/ structure"
    )
    parser.add_argument(
        'files',
        nargs='+',
        help='Root-level .md files to ingest'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually moving files'
    )

    args = parser.parse_args()
    config = load_config()

    exclude_globs = config['exclude_globs']
    destination_map = config['destination_map']
    default_dest = config['default_dest']

    moves = 0

    for filename in args.files:
        filepath = Path(filename)

        # Validate file exists and is in root
        if not filepath.exists():
            print(f"WARNING: File not found: {filepath}", file=sys.stderr)
            continue

        if filepath.parent != Path('.'):
            print(f"SKIP: {filepath} (not in repository root)")
            continue

        # Check exclusions
        if should_exclude(filepath.name, exclude_globs):
            print(f"EXCLUDED: {filepath}")
            continue

        # Find destination
        destination = find_destination(filepath.name, destination_map, default_dest)

        # Ingest file
        if ingest_file(filepath, destination, args.dry_run):
            moves += 1

    print(f"INGEST_MOVES={moves}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
