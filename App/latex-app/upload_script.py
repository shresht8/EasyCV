import argparse
from google.cloud import storage
from google.cloud.storage.blob import Blob
import datetime
from google.auth import default

import sys
def write_status_to_file(status_message, file_path):
    with open(file_path, 'w') as file:
        file.write(status_message)

def upload_to_gcs(source_file_name, destination_blob_name):
    # storage_client = storage.Client()
    # bucket = storage_client.bucket(bucket_name)
    credentials, project = default()
    client = storage.Client(credentials=credentials, project='KeyProject')
    bucket = client.get_bucket("easy-cv-bucket")
    blob = Blob(destination_blob_name, bucket)

    blob.upload_from_filename(source_file_name)

    # Create a signed URL
    url = blob.generate_signed_url(expiration=datetime.timedelta(hours=1), method='GET')
    return url

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--success', action='store_true')
    parser.add_argument('--failure', action='store_true')
    args = parser.parse_args()
    status_file_path = "/app/output/pdf_generation_status.txt"
    if args.success:
        # Logic for successful PDF generation
        # Assuming the PDF filename is known
        url = upload_to_gcs("/app/output/main.pdf", "main.pdf")
        # Return or send the signed URL
        status_message = f"Success: PDF generated successfully. Download link: {url}"
        write_status_to_file(status_message, status_file_path)
    elif args.failure:
        # Logic for failed PDF generation
        status_message = "Failure: PDF could not be generated."
        # Send notification of failure
        write_status_to_file(status_message, status_file_path)
        pass

if __name__ == "__main__":
    main()
