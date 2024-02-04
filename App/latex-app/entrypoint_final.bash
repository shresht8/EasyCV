#!/bin/bash
# entrypoint.sh

set -e

WATCH_DIR="/app/output"
PDF_GENERATED=0

while true; do
  inotifywait -e create -e moved_to "$WATCH_DIR" --format '%f' | while read FILE
  do
    if [[ "$FILE" == "main.tex" ]]; then
      pdflatex -output-directory "$WATCH_DIR" "$WATCH_DIR/$FILE" || true
      if [ $? -eq 0 ]; then
        PDF_GENERATED=1
      else
        lualatex -output-directory "$WATCH_DIR" "$WATCH_DIR/$FILE" || true
        if [ $? -eq 0 ]; then
          PDF_GENERATED=1
        fi
      fi

      # Check if PDF was generated
      if [ $PDF_GENERATED -eq 1 ]; then
        # Call Python script for successful PDF generation
        python /path/to/upload_script.py --success
      else
        # Call Python script for failed PDF generation
        python /path/to/upload_script.py --failure
      fi
    fi
  done
done
