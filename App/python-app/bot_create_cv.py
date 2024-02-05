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
import argparse

class JobDescription(BaseModel):
    """Extracting detailed information about a job description parsed from HTML text
    containing some relevant and some irrelevant text"""
    job_title: str = Field(..., description="The job title/position offered by company")
    job_overview: str = Field(..., description="Overview of the job")
    company_name: str = Field(..., description="Company name offering the job")
    about_company: str = Field(..., description="About the company")
    job_responsibilities: str = Field(..., description="responsibilities of the role. Use bullet points if possible")
    job_requirements: str = Field(..., description="requirements/experience/ to get the job. Use bullet points if you "
                                                   "can")
    skills_required: Optional[str] = Field(None, description="skills required for the job. Use bullet points if you can")
    salary_range: Optional[int] = Field(None, description="salary range for the job")
    company_perks: Optional[str] = Field(None, description="Benefits offered by the company for the role. Use bullet "
                                                           "points if you can")


class BotCreateCV():
    def __init__(self,latex_input_path , user_info_path, job_desc_link, output_path):
        print('hi')
        self.bucket = None
        self.client = None
        self.job_desc_str = None
        self.latex_content = None
        self.user_info_str = None
        self.latex_input_path = latex_input_path
        self.user_info_path = user_info_path
        self.job_desc_link = job_desc_link
        self.output_path = output_path
        self.init_gloud()
        self.preprocess_user_date()
        self.scrape_job_desc()
        self.read_cv_template()
        self.read_job_desc()
        self.download_bucket_folder()


    def init_gloud(self):
        try:
            credentials, project = default()
            print("Google cloud credentials initiated")
            self.client = storage.Client(credentials=credentials, project='KeyProject')
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
        path = os.path.join(self.user_info_path, 'user_professional_information.txt')
        path = path.replace('\\','/')
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
        print("CV Template {} used.".format(self.latex_input_path))
        path = os.path.join(self.latex_input_path, 'main.tex')
        path = path.replace('\\','/')
        blob = self.bucket.blob(path)
        try:
            with blob.open("r") as f:
                latex_content_bytes = f.read()
                print("CV template main.tex file successfully read")
            self.latex_content = latex_content_bytes
        except Exception as e:
            print("CV Template in input not found in blob")
        # self.latex_content = latex_content_bytes.decode('utf-8')

    def download_bucket_folder(self):
        """Download all files from a specific folder in the GCS bucket to the local directory."""

        source_folder = self.latex_input_path
        # Ensure the source folder path is correctly formatted
        if not self.latex_input_path.endswith('/'):
            source_folder = self.latex_input_path +  '/'

        blobs = self.bucket.list_blobs(prefix=source_folder)  # List blobs in the specific folder

        for blob in blobs:
            if blob.name.endswith('main.tex'):
                continue

            # Removing the source folder path from the blob name
            relative_path = blob.name[len(source_folder):]
            if not relative_path:  # Skip if it's just the folder itself
                continue

            # Create local path for blob
            local_path = os.path.join(self.output_path, relative_path)
            local_path = local_path.replace('\\', '/') # For deployment
            # local_path = local_path.replace("/", "\\") # For local
            # Create necessary local directories
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # Download the blob to the local path
            blob.download_to_filename(local_path)
            print(f"Downloaded {blob.name} to {local_path}")

    def read_job_desc(self):
        """reads the job description from the path"""
        job_desc_path = os.path.join(self.output_path, 'job_description.txt')
        job_desc_path = job_desc_path.replace('\\','/') # For deployment
        # Uncomment below line for local testing
        # job_desc_path = job_desc_path.replace('/', '\\') For local
        with open(job_desc_path, 'r') as file:
            # print(file)
            self.job_desc_str = file.read()
            print("job decription exists; read to string")

    def scrape_job_desc(self):
        """Scrapes job data from link and """
        job_desc_path = os.path.join(self.output_path, 'job_description.txt')
        job_desc_path = job_desc_path.replace('\\', '/')  # For deployment
        # Uncomment below line for local testing
        # job_desc_path = job_desc_path.replace('/', '\\') For local
        if not os.path.exists(job_desc_path):
            print("job description doesn't exist; Using OpenAI function to scrape JD to text file")
            url = [self.job_desc_link]
            loader = AsyncHtmlLoader(url)
            docs = loader.load()
            html2text = Html2TextTransformer()
            docs_transformed = html2text.transform_documents(docs)
            job_desc_obj = self.html_to_schema(docs_transformed)
            self.write_jd_to_txt(job_desc_path, job_desc_obj)

    def html_to_schema(self, html_text):
        """Extracts schema of job description from HTML to given schema"""
        llm = ChatOpenAI(model="gpt-4", temperature=0)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a world class algorithm for extracting information in structured formats."),
                ("human", "Use the given format to extract detailed information from the following input: {input}"),
                ("human", "Tip: Make sure to answer in the correct format"),
            ]
        )

        chain = create_structured_output_chain(JobDescription, llm, prompt, verbose=True)
        job_description = chain.run(html_text[0].page_content)
        return job_description

    def write_jd_to_txt(self, path, job_desc: JobDescription):
        """Write job description object to text file"""
        with open(path, 'w+', encoding='utf-8') as file:
            # print(job_desc.job_title)
            # print(job_desc.about_company)
            # print(job_desc.job_overview)
            # print(job_desc.job_responsibilities)
            # print(job_desc.job_requirements)
            # print(job_desc.skills_required)
            # print(job_desc.salary_range)
            # # print(job_desc.skills_required)
            # print(job_desc.company_perks)
            file.write("Job Title: {}\n".format(job_desc.job_title))
            file.write("\n")
            file.write("Company Overview:\n{}".format(job_desc.about_company))
            file.write("\n")
            file.write("------------------")
            file.write("\n")
            file.write("About the job:\n{}\n".format(job_desc.job_overview))
            file.write("\n")
            file.write("Job responsibilities:\n{}\n".format(job_desc.job_responsibilities))
            file.write("\n")
            file.write("Job requirements:\n{}\n".format(job_desc.job_requirements))
            file.write("\n")
            if job_desc.skills_required:
                file.write("Skills required:\n{}\n".format(job_desc.skills_required))
                file.write("\n")
            if job_desc.salary_range:
                file.write("Salary offered:\n{}\n".format(job_desc.salary_range))
                file.write("\n")
            if job_desc.company_perks:
                file.write("Company perks:\n{}\n".format(job_desc.company_perks))
                file.write("\n")
            print("JD written to text file")

    def generate_cv(self):
        """initializes llm, creates cv tex file and compiles it"""
        CV_EXPERT_BOT = CVExpertBot(self.user_info_str,
                                    self.job_desc_str,
                                    self.latex_content)
        CV_EXPERT_BOT.generate_latex_output(self.output_path)
        # CV_EXPERT_BOT.compile_tex_file(self.cv_template_path)

# if __name__ == '__main__':
#     os.environ['OPENAI_API_KEY'] = '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'
#     bot = BotCreateCV("cv_templates/cv_template_3","user/Shresht_Shetty",
#                 "https://www.seek.com.au/job/71297266?type=standard#sol=9a67e2171fa56642ab1b092d4ad01256cb8e6a6f",
#                 "C:\\Users\shres\Projects\EasyCV\App\python-app\output")
#     bot.generate_cv()


