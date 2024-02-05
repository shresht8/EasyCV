#!/bin/bash
# entrypoint_final.sh

set -e

WATCH_DIR="/app/output"
PDF_GENERATED=0

while true; do
  inotifywait -e create -e moved_to "$WATCH_DIR" --format '%f' | while read FILE
  do
    if [[ "$FILE" == "main.tex" ]]; then
      echo "Attempting to compile $FILE with pdflatex..."
      pdflatex -output-directory "$WATCH_DIR" "$WATCH_DIR/$FILE" || true
      if [ $? -eq 0 ]; then
        PDF_GENERATED=1
        echo "pdflatex successfully generated the PDF."
      else
        echo "pdflatex failed to compile $FILE, trying with lualatex..."
        lualatex -output-directory "$WATCH_DIR" "$WATCH_DIR/$FILE" || true
        if [ $? -eq 0 ]; then
          PDF_GENERATED=1
          echo "lualatex successfully generated the PDF."
        else
          echo "lualatex also failed to compile $FILE. PDF could not be generated."
        fi
      fi

      # Check if PDF was generated
      if [ $PDF_GENERATED -eq 1 ]; then
        echo "PDF generation successful. Uploading to GCS..."
        # Call Python script for successful PDF generation
        python /path/to/upload_script.py --success
      else
        echo "PDF generation failed after attempting both pdflatex and lualatex. Notifying the failure..."
        # Call Python script for failed PDF generation
        python /path/to/upload_script.py --failure
      fi
    fi
  done
done
