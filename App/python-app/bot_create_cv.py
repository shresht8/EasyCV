import time

from cv_expert_bot import CVExpertBot
from google.auth import default
from google.cloud import storage
import requests
from langchain.document_loaders import AsyncHtmlLoader
from langchain.document_transformers import Html2TextTransformer
from langchain.pydantic_v1 import BaseModel, Field
from typing import Optional
import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains.openai_functions import (
    create_openai_fn_chain,
    create_structured_output_chain,
)
import tempfile


class JobDescription(BaseModel):
    """Extracting detailed information about a job description parsed from HTML text
    containing some relevant and some irrelevant text"""

    job_title: str = Field(..., description="The job title/position offered by company")
    job_overview: str = Field(..., description="Overview of the job")
    company_name: str = Field(..., description="Company name offering the job")
    about_company: str = Field(..., description="About the company")
    job_responsibilities: str = Field(
        ..., description="responsibilities of the role. Use bullet points if possible"
    )
    job_requirements: str = Field(
        ...,
        description="requirements/experience/ to get the job. Use bullet points if you "
        "can",
    )
    skills_required: Optional[str] = Field(
        None, description="skills required for the job. Use bullet points if you can"
    )
    salary_range: Optional[int] = Field(None, description="salary range for the job")
    company_perks: Optional[str] = Field(
        None,
        description="Benefits offered by the company for the role. Use bullet "
        "points if you can",
    )


class BotCreateCV:
    def __init__(self, user_name, user_info_path, cv_template_path, compilation_type):
        print("hi")
        self.bucket = None
        self.client = None
        self.latex_content = None
        self.user_info_str = None
        output_path = "/app/output/"
        self.compilation_type = compilation_type
        self.user_name = user_name
        self.user_info_path = user_info_path
        self.cv_template_path = cv_template_path
        self.output_path = self.create_temp_dir(output_path)
        self.init_gloud()
        self.preprocess_user_date()
        self.read_cv_template()
        self.download_bucket_folder()
        self.write_compilation_type()

    def create_temp_dir(self, shared_output_path):
        """
        Creates a temporary sub-directory within the specified parent path.

        :param shared_output_path: The path of the parent directory where the temporary directory will be created.
        :return: The path of the newly created temporary directory.
        """
        # Ensure the parent path exists
        if not os.path.exists(shared_output_path):
            raise ValueError(
                f"The specified parent path does not exist: {shared_output_path}"
            )
        # Create a temporary directory within the specified parent path and return its name
        temp_dir_path = tempfile.mkdtemp(dir=shared_output_path)
        print(f"Temporary directory created at: {temp_dir_path}")
        return temp_dir_path

    def write_compilation_type(self):
        compilation_file_path = os.path.join(self.output_path, "compilation_type.txt")
        compilation_file_path = compilation_file_path.replace("\\", "/")
        with open(compilation_file_path, "w", encoding="utf-8") as file:
            file.write(self.compilation_type)

    def init_gloud(self):
        try:
            credentials, project = default()
            print("Google cloud credentials initiated")
            self.client = storage.Client(credentials=credentials, project="KeyProject")
            self.bucket = self.client.get_bucket("easy-cv-bucket")
            # List all the objects in the bucket "easy-cv-bucket"
            blobs = self.client.list_blobs(bucket_or_name="easy-cv-bucket")
        except Exception as e:
            print("Google cloud credentials not found")

        # Print the names of the objects
        # for blob in blobs:
        #     print(blob.name)

    def preprocess_user_date(self):
        """reads and preprocesses user info, add logo metadata to user info doc"""
        # Get the text document object.
        path = os.path.join(self.user_info_path, "user_professional_information.txt")
        path = path.replace("\\", "/")
        try:
            blob = self.bucket.blob(path)
            with blob.open("r") as f:
                self.user_info_str = f.read()
                print("user professional information successfully read")
        except Exception as e:
            print("user professional information path not found in blob")
        # with open(os.path.join(self.user_info_path, 'user_professional_information.txt'), 'rb') as file:
        #     self.user_info_str = file.read()

    def read_cv_template(self):
        """reads cv main.tex file from the directory"""
        # with open(os.path.join(self.latex_input_path, 'main.tex'), 'rb') as file:
        #     latex_content_bytes = file.read()
        print("CV Template {} used.".format(self.cv_template_path))
        path = os.path.join(self.cv_template_path, "cv_prompt.txt")
        path = path.replace("\\", "/")
        blob = self.bucket.blob(path)
        try:
            with blob.open("r") as f:
                latex_content_bytes = f.read()
                print("CV template cv_prompt.txt file successfully read")
            self.cv_prompt_str = latex_content_bytes
        except Exception as e:
            print("CV Template in input not found in blob")
        # self.latex_content = latex_content_bytes.decode('utf-8')

    def download_bucket_folder(self):
        """Download all files from a specific folder in the GCS bucket to the local directory."""

        source_folder = self.cv_template_path
        # Ensure the source folder path is correctly formatted
        if not self.cv_template_path.endswith("/"):
            source_folder = self.cv_template_path + "/"

        blobs = self.bucket.list_blobs(
            prefix=source_folder
        )  # List blobs in the specific folder

        for blob in blobs:
            if blob.name.endswith("main.tex"):
                continue

            # Removing the source folder path from the blob name
            relative_path = blob.name[len(source_folder) :]
            if not relative_path:  # Skip if it's just the folder itself
                continue

            # Create local path for blob
            local_path = os.path.join(self.output_path, relative_path)
            local_path = local_path.replace("\\", "/")  # For deployment
            # local_path = local_path.replace("/", "\\") # For local
            # Create necessary local directories
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # Download the blob to the local path
            blob.download_to_filename(local_path)
            print(f"Downloaded {blob.name} to {local_path}")

    def generate_cv(self):
        """initializes llm, creates cv tex file and compiles it"""
        CV_EXPERT_BOT = CVExpertBot(
            self.user_name, self.user_info_str, self.cv_prompt_str
        )
        CV_EXPERT_BOT.generate_latex_output(self.cv_template_path)
        # CV_EXPERT_BOT.compile_tex_file(self.cv_template_path)


# if __name__ == '__main__':
#     os.environ['OPENAI_API_KEY'] = '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'
#     bot = BotCreateCV("cv_templates/cv_template_3","user/Shresht_Shetty",
#                 "https://www.seek.com.au/job/71297266?type=standard#sol=9a67e2171fa56642ab1b092d4ad01256cb8e6a6f",
#                 "C:\\Users\shres\Projects\EasyCV\App\python-app\output")
#     bot.generate_cv()
