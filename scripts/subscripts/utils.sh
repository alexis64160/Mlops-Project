#!/usr/bin/env bash

find_project_root() {
    local marker_name=".dsdc_project_root"
    local start_points=("$@")

    # For each starting point, walk up the directory tree
    for start in "${start_points[@]}"; do
        local dir="$start"
        while true; do
            if [ -f "$dir/$marker_name" ]; then
                echo "$dir"
                return 0
            fi
            local parent="$(dirname "$dir")"
            if [ "$parent" = "$dir" ]; then
                break  # Reached the filesystem root
            fi
            dir="$parent"
        done
    done

    return 1  # target file not found
}

check_python_version() {
    local required_major=3
    local required_minor=13
    local py_exec="${1:-${DSDC_PYTHON:-}}"  # Optional first arg: python executable path
    # If no python path given, try to find python3 or python in PATH
    if [[ -z "$py_exec" ]]; then
        if command -v python3 &>/dev/null; then
            py_exec=$(command -v python3)
        elif command -v python &>/dev/null; then
            py_exec=$(command -v python)
        else
            echo "🛑 Error: Python is not installed or not in PATH." >&2
            return 1
        fi
    else
        # If py_exec is given but maybe relative, resolve full path if possible
        if command -v "$py_exec" &>/dev/null; then
            py_exec=$(command -v "$py_exec")
        else
            echo "🛑 Error: Python executable '$py_exec' not found or not executable." >&2
            return 1
        fi
    fi

    # Get version string (e.g. "3.13.2")
    local version_str
    version_str=$("$py_exec" --version 2>&1 | awk '{print $2}')

    # Parse major, minor, patch
    IFS='.' read -r major minor patch <<< "$version_str"
    if [[ "$major" -eq "$required_major" && "$minor" -eq "$required_minor" ]]; then
        echo $py_exec
        return 0
    else
        echo "🛑 Error: Python version must be ${required_major}.${required_minor}.x, but found $version_str" >&2
        return 1
    fi
}