#!/bin/bash
# entrypoint_final.sh

set -e
set -x

WATCH_DIR="/app/output"
PDF_GENERATED=0
LOG_FILE="/app/output/inotify_output.log"
BUCKET_NAME="easy-cv-bucket/output"
PRIVATE_KEY_FILE="/var/secrets/google/key.json"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Initial log message
log_message "Script started"

{
    while true; do
        # Log the contents of the directory before watching
        log_message "Contents of ${WATCH_DIR} before watching:"
        ls -l "${WATCH_DIR}" >> "$LOG_FILE" 2>&1
        
        # Use inotifywait to monitor directory and read output in a while loop
        inotifywait -e create -e moved_to "$WATCH_DIR" --format '%f' | while IFS= read -r FILE; do
            log_message "Detected change in file: $FILE"

            if [[ "$FILE" == "main.tex" ]]; then
                log_message "Attempting to compile $FILE with pdflatex..."
                if pdflatex -output-directory "$WATCH_DIR" "$WATCH_DIR/$FILE" >> "$LOG_FILE" 2>&1; then
                    PDF_GENERATED=1
                    log_message "pdflatex successfully generated the PDF."
                else
                    log_message "pdflatex failed to compile $FILE, trying with lualatex..."
                    if lualatex -output-directory "$WATCH_DIR" "$WATCH_DIR/$FILE" >> "$LOG_FILE" 2>&1; then
                        PDF_GENERATED=1
                        log_message "lualatex successfully generated the PDF."
                    else
                        log_message "lualatex also failed to compile $FILE. PDF could not be generated."
                    fi
                fi

                # Check if PDF was generated
                if [ $PDF_GENERATED -eq 1 ]; then
                    PDF_FILE="${WATCH_DIR}/main.pdf"
                    log_message "PDF generation successful. Uploading to GCS..."
                    # Upload the PDF to GCS
                    gcloud storage cp "${PDF_FILE}" "gs://${BUCKET_NAME}" >> "$LOG_FILE" 2>&1
                    # Get a signed URL for the uploaded PDF
                    log_message "Generating signed URL for ${PDF_FILE}..."
                    gcloud storage sign-url "gs://${BUCKET_NAME}/${PDF_FILE}" --private-key-file="${PRIVATE_KEY_FILE}" --duration=10m >> "$LOG_FILE" 2>&1
                else
                    log_message "PDF generation failed after attempting both pdflatex and lualatex. Notifying the failure..."
                fi
            fi
        done
    done
} >> "$LOG_FILE" 2>&1  # Redirect all output from the block to the log file
