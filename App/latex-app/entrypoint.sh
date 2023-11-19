#!/bin/bash
# entrypoint.sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Directory to watch for modifications
WATCH_DIR="/app/output"

# Loop indefinitely
while true; do
  # Wait for a 'main.tex' file to appear in the directory
  inotifywait -e create -e moved_to "$WATCH_DIR" --format '%f' | while read FILE
  do
    if [[ "$FILE" == "main.tex" ]]; then
      # When 'main.tex' appears, run pdflatex
      pdflatex -output-directory "$WATCH_DIR" "$WATCH_DIR/$FILE"
      # You could also handle other tasks here if necessary
    fi
  done
done
