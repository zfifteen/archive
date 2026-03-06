#!/bin/bash
# Freeze context script for zero-bias validation reproducibility

echo "Freezing context for zero-bias validation..."

# Record commit SHA
git rev-parse HEAD | tee specs/001-zero-bias-validation/validation/commit.txt

# Record JVM version
java -version 2>&1 | tee specs/001-zero-bias-validation/validation/jvm_version.txt

# Record Gradle version
./gradlew -v 2>&1 | tee specs/001-zero-bias-validation/validation/gradle_version.txt

# Record Python version
python3 --version 2>&1 | tee specs/001-zero-bias-validation/validation/python_version.txt

echo "Context frozen. Files saved in specs/001-zero-bias-validation/validation/"