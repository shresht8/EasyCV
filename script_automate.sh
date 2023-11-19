#!/bin/bash

# Check if the required number of arguments are provided
if [ "$#" -ne 5 ]; then
    echo "Usage: $0 arg1 arg2 arg3 arg4 result_directory"
    exit 1
fi

# Assign arguments to variables
arg1="$1"
arg2="$2"
arg3="$3"
arg4="$4"
result_directory="$5"

# Define the LaTeX file name based on arg1
latex_file="${arg1}_CV.tex"

# Run your Python script with arguments in the first directory
python bot_create_cv.py "$arg1" "$arg2" "$arg3" "$arg4"

# Check if the Python script was successful
if [ $? -eq 0 ]; then
    # Change to the result directory
    cd "$result_directory"

    # Check if the change of directory was successful
    if [ $? -eq 0 ]; then
        # Run pdflatex on the dynamically generated TeX file
        pdflatex "$latex_file"

        # Check if pdflatex was successful
        if [ $? -eq 0 ]; then
            echo "pdflatex was successful."
        else
            echo "pdflatex failed."
        fi
    else
        echo "Failed to change to the result directory: $result_directory"
    fi
else
    echo "Python script failed. Aborting pdflatex."
fi

