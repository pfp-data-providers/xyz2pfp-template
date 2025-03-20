#!/bin/bash

# Help function
show_help() {
    echo "Usage: $(basename $0) <replacement_text>"
    echo
    echo "This script replaces all occurrences of 'xyz' with the provided replacement text"
    echo "in all files within the current directory and subdirectories,"
    echo "excluding .git, venv directories and this script itself."
    echo "It also removes the usage section from README.md"
    echo
    echo "Arguments:"
    echo "  replacement_text    The text that will replace 'xyz' in all files"
    echo
    echo "Example:"
    echo "  ./$(basename $0) new-project-name"
    echo
    exit 1
}

# Show help if -h or --help is provided
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    show_help
fi

# Check if argument is provided
if [ $# -ne 1 ]; then
    echo "Error: Missing replacement text"
    echo "For help, use: $0 --help"
    exit 1
fi

REPLACEMENT=$1
SCRIPT_NAME=$(basename "$0")

# Remove usage section from README.md if it exists
if [ -f "README.md" ]; then
    sed -i '/^### Usage/,$d' README.md
    echo "Removed usage section from README.md"
fi

# Find all files excluding .git, venv directories and this script, then perform replacement
find . -type f \
    -not -path "./.git/*" \
    -not -path "./venv/*" \
    -not -name "$SCRIPT_NAME" \
    -exec grep -l "xyz" {} \; | \
while read file; do
    echo "Processing: $file"
    sed -i "s@xyz@$REPLACEMENT@g" "$file"
done

echo "Replacement complete: 'xyz' → '$REPLACEMENT'"