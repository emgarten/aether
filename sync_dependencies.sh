#!/bin/bash

set -e  # Exit immediately if a command fails

# Parse the --lock flag
RUN_LOCK=false
for arg in "$@"; do
  if [[ "$arg" == "--lock" ]]; then
    RUN_LOCK=true
  fi
done

# Find all pyproject.toml files at any depth, but exclude the one in the root directory
find . -name "pyproject.toml" | while read -r file; do
  # Get the directory containing the pyproject.toml file
  dir=$(dirname "$file")

  # Skip the root directory
  if [[ "$dir" == "." ]]; then
    echo "Skipping pyproject.toml in root directory"
    continue
  fi

  echo "Processing $dir"

  # Run poetry lock if the --lock flag was given
  if [[ "$RUN_LOCK" == true ]]; then
    echo "Running poetry lock for $dir"
    (cd "$dir" && poetry lock)
  fi

  # Run poetry install
  echo "Running poetry install for $dir"
  (cd "$dir" && poetry install)
done
