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
        
        # Use inotifywait to monitor all subdirectories for new or moved 'main.tex' files
        inotifywait -r -e create -e moved_to --format '%w%f' "$WATCH_DIR" | while IFS= read -r FILEPATH; do
            FILE=$(basename "$FILEPATH")
            DIR=$(dirname "$FILEPATH")
            log_message "Change detected in $FILEPATH"

            if [[ "$FILE" == "main.tex" ]]; then
                log_message "Found main.tex in $DIR. Attempting to compile with pdflatex."
                pushd "$DIR"
                if pdflatex "$FILE" >> "$LOG_FILE" 2>&1; then
                    PDF_GENERATED=1
                    log_message "pdflatex successfully generated PDF for $FILE in $DIR."
                else
                    log_message "pdflatex failed to compile $FILE in $DIR. Trying with lualatex."
                    if lualatex "$FILE" >> "$LOG_FILE" 2>&1; then
                        PDF_GENERATED=1
                        log_message "lualatex successfully generated PDF for $FILE in $DIR."
                    else
                        log_message "Both pdflatex and lualatex failed to compile $FILE in $DIR."
                    fi
                fi

                # Check if PDF was generated
                if [ $PDF_GENERATED -eq 1 ]; then
                    TIMESTAMP=$(date +%Y%m%d%H%M%S)
                    PDF_FILENAME="main.pdf"
                    PDF_FILE="${DIR}/${PDF_FILENAME}"
                    BUCKET_PATH="gs://${BUCKET_NAME}/${PDF_FILENAME}"
                    if [ -f "$PDF_FILE" ]; then

                        log_message "PDF generation successful. Uploading ${PDF_FILE} to GCS..."
                        # Upload the PDF to GCS with a unique filename
                        gcloud storage cp "${PDF_FILE}" "${BUCKET_PATH}" >> "$LOG_FILE" 2>&1
                        # Get a signed URL for the uploaded PDF
                        log_message "Generating signed URL for ${BUCKET_PATH}..."
                        SIGNED_URL=$(gcloud storage sign-url "${BUCKET_PATH}" --private-key-file="${PRIVATE_KEY_FILE}" --duration=10m --quiet)
                        log_message "Signed URL: ${SIGNED_URL}"
                    else
                        log_message "PDF file not found: ${PDF_FILE}"
                    fi
                else
                    log_message "PDF generation failed after attempting both pdflatex and lualatex. Notifying the failure..."
                fi
            fi
            popd
        done
    done
} >> "$LOG_FILE" 2>&1  # Redirect all output from the block to the log file
