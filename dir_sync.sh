#!/bin/bash

# Define the source and target directories
SOURCE_DIR="/home/gk8/TBTPTW/monitoring/Monitoring_20240505_PR"
TARGET_DIR="/home/gk8/local-repo/Nodes1/Monitoring"

# Function to display usage
usage() {
    echo -e "\e[33mUsage: $0"
    echo -e "Make sure to edit the paths inside this script before running:"
    echo -e "SOURCE_DIR: $SOURCE_DIR"
    echo -e "TARGET_DIR: $TARGET_DIR\e[0m"
    echo
    read -p "Are these paths correct? (yes/no): " confirmation
    if [ "$confirmation" != "yes" ]; then
        echo "Please edit the paths in the script and rerun."
        exit 1
    fi
}

# Confirm paths with the user
usage

# Function to handle file comparison and copying
handle_file() {
    local relative_path="${1#"$SOURCE_DIR/"}"  # Get the relative path of the file
    local src_file="$1"
    local target_file="$TARGET_DIR/$relative_path"

    # Check if file exists in the target and compare them
    if [ -f "$target_file" ]; then
        if ! diff -q "$src_file" "$target_file" > /dev/null; then
            echo -e "\n\e[36mDifferences found for: $relative_path\e[0m"
            show_options "$src_file" "$target_file"
        else
            echo -e "\n\e[32mNo differences for: $relative_path\e[0m"
        fi
    else
        echo -e "\n\e[31mFile does not exist in target: $target_file\e[0m"
        show_options "$src_file" "$target_file"
    fi
}

# Function to show options and handle user input
show_options() {
    local src_file="$1"
    local target_file="$2"

    # Show details of the source and target files
    echo "Source file details:"
    ls -l "$src_file"
    if [ -f "$target_file" ]; then
        echo "Target file details:"
        ls -l "$target_file"
    fi

    # Ask user for action
    echo "Options: 1) Edit both with nano, 2) View both with less, 3) Show diff"
    read -p "Choose an option (or press enter to skip): " option

    case $option in
        1) nano "$src_file"; [ -f "$target_file" ] && nano "$target_file";;
        2) less "$src_file"; [ -f "$target_file" ] && less "$target_file";;
        3) if [ -f "$target_file" ]; then
               diff -u "$target_file" "$src_file" | less
           else
               echo "Target file does not exist, nothing to compare."
           fi;;
        *) echo "Skipping..."; return;;
    esac

    # Ask if the user wants to replace the file
    read -p "Replace this file in the target directory? (y/n): " replace
    if [[ "$replace" == "y" ]]; then
        cp -f "$src_file" "$target_file"
        echo -e "\e[32mFile replaced: $target_file\e[0m"
    else
        echo "File not replaced."
    fi
}

# Export function to be used in find command
export -f handle_file show_options

# Start the process
find "$SOURCE_DIR" -type f -exec bash -c 'handle_file "$0"' {} \;
