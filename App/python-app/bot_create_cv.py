from cv_expert_bot import CVExpertBot
from google.auth import default
from google.cloud import storage
import os
import tempfile
from langchain_community.document_transformers import Html2TextTransformer
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains.openai_functions import (
    create_extraction_chain_pydantic,
)
from langchain.pydantic_v1 import BaseModel, Field
from typing import Optional, List
from pydantic import BaseModel
import json
from typing import List, Optional
from constants import PY_ENV

# Import the UserInfo class and other necessary classes
from models import UserInfo, Education, Experience, Project


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
    def __init__(
        self,
        user_name: str,
        user_info_path: UserInfo,
        cv_template_path: Optional[str] = None,
        cl_template_path: Optional[str] = None,
        job_desc_link: Optional[str] = None,
        cv_compilation_type: Optional[str] = None,
        cl_compilation_type: Optional[str] = None,
    ):
        self.cv_prompt_str = None
        self.job_desc_str = None
        self.cl_prompt_str = None
        print("hi")
        self.bucket = None
        self.client = None
        self.latex_content = None
        self.user_info_str = None
        output_path = "C:\\Users\\shres\\Projects\\EasyCV\\App\\python-app\\app\\output"
        if PY_ENV == "test":
            output_path = "/app/output"
        self.cv_compilation_type = cv_compilation_type
        self.cl_compilation_type = cl_compilation_type
        self.user_name = user_name
        self.user_info = user_info_path  # Store the UserInfo object
        self.cv_template_path = cv_template_path
        self.cl_template_path = cl_template_path
        self.job_desc_link = job_desc_link
        self.output_path = self.create_temp_dir(output_path)
        self.init_gloud()
        self.preprocess_user_data()  # Rename this method
        self.download_bucket_folder()
        if self.cv_template_path:
            print("Initiating CV pipeline")
            self.read_cv_template()
            self.write_cv_compilation_type()
        if self.cl_template_path:
            print("Initiating CL pipeline")
            self.write_cl_compilation_type()
            self.jd_path = os.path.join(
                self.output_path, f"{self.user_name}_job_description.txt"
            )
            if PY_ENV == "test":
                self.jd_path = self.jd_path.replace("\\", "/")
            self.scrape_job_desc()
            self.read_job_desc()
            self.read_cl_template()

    @staticmethod
    def create_temp_dir(shared_output_path):
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
        if PY_ENV == "test":
            temp_dir_path = temp_dir_path.replace("\\", "/")
        print(f"Temporary directory created at: {temp_dir_path}")
        return temp_dir_path

    def write_cv_compilation_type(self):
        try:
            compilation_file_path = os.path.join(
                self.output_path, "cv_compilation_type.txt"
            )
            if PY_ENV == "test":
                compilation_file_path = compilation_file_path.replace("\\", "/")
            with open(compilation_file_path, "w", encoding="utf-8") as file:
                print("cv compilation type:", self.cv_compilation_type)
                file.write(self.cv_compilation_type)
            print(f"cv compilation type written to: {self.output_path}")
        except Exception as e:
            print("incorrect output path to write cv compilation type")

    def write_cl_compilation_type(self):
        try:
            compilation_file_path = os.path.join(
                self.output_path, "cl_compilation_type.txt"
            )
            if PY_ENV == "test":
                compilation_file_path = compilation_file_path.replace("\\", "/")
            with open(compilation_file_path, "w", encoding="utf-8") as file:
                file.write(self.cl_compilation_type)
            print(f"cl compilation type written to: {self.output_path}")
        except Exception as e:
            print("incorrect output path to write cl compilation type")

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

    def _format_education(self, education_list: List[Education]) -> str:
        return "\n".join(
            f"- {edu.degree} from {edu.university}\n  ({edu.start_year} - {edu.end_year})"
            for edu in education_list
        )

    def _format_experience(self, experience_list: List[Experience]) -> str:
        return "\n".join(
            f"- {exp.position} at {exp.company}\n  ({exp.start_year} - {exp.end_year})\n  Summary: {exp.summary}"
            for exp in experience_list
        )

    def _format_projects(self, project_list: List[Project]) -> str:
        project_strings = []
        for project in project_list:
            project_str = f"- {project.title}\n  Role: {project.role}\n  Description: {project.description}\n  Responsibilities:"
            for resp in project.responsibilities:
                project_str += f"\n    • {resp}"
            project_strings.append(project_str)
        return "\n\n".join(project_strings)

    def _format_multiline(self, text: str, indent: str = "  ") -> str:
        return "\n".join(f"{indent}{line}" for line in text.split("\n"))

    def _format_list(self, items: List[str]) -> str:
        return "\n".join(f"- {item}" for item in items)

    def preprocess_user_data(self):
        """Converts UserInfo object to a formatted string"""
        user_info = self.user_info
        self.user_info_str = f"""Name: {user_info.first_name} {user_info.last_name}
        Email: {user_info.email}
        Contact: {user_info.contact_no}
        Address: {user_info.address}
    
        Bio:
        {self._format_multiline(user_info.bio)}
    
        Education:
        {self._format_education(user_info.education)}
    
        Experience:
        {self._format_experience(user_info.experience)}
    
        Projects:
        {self._format_projects(user_info.projects)}
    
        Skills:
        {self._format_list(user_info.skills)}
    
        Certifications:
        {self._format_list(user_info.certifications) if user_info.certifications else "None"}
    
        Image URL: {user_info.image if user_info.image else "Not provided"}
        Website: {user_info.website if user_info.website else "Not provided"}
        LinkedIn: {user_info.linkedin if user_info.linkedin else "Not provided"}
        Calendly: {user_info.calendly_url if user_info.calendly_url else "Not provided"}
        """
        print(self.user_info_str)

    def read_cv_template(self):
        """reads cv main.tex file from the directory"""
        # with open(os.path.join(self.latex_input_path, 'main.tex'), 'rb') as file:
        #     latex_content_bytes = file.read()
        print("CV Template {} used.".format(self.cv_template_path))
        path = os.path.join(self.cv_template_path, "cv_prompt.txt")
        path = path.replace("\\", "/")
        # print(path)
        blob = self.bucket.blob(path)
        try:
            with blob.open("r", encoding="utf-8") as f:
                latex_content_bytes = f.read()
                print("CV template cv_prompt.txt file successfully read")
            self.cv_prompt_str = latex_content_bytes
        except Exception as e:
            print("CV Template in input not found in blob")
        # self.latex_content = latex_content_bytes.decode('utf-8')

    def read_cl_template(self):
        """reads the main tex file as the latex template for the model"""
        print("CL Template {} used.".format(self.cl_template_path))
        path = os.path.join(self.cl_template_path, "main.tex")
        path = path.replace("\\", "/")
        blob = self.bucket.blob(path)
        try:
            with blob.open("r", encoding="utf-8") as f:
                self.cl_prompt_str = f.read()
                print("CL template main.tex file successfully read")
        except Exception as e:
            print("CL Template in input not found in blob")

    def download_files_from_path(self, source_path):
        blobs = self.bucket.list_blobs(
            prefix=source_path
        )  # List blobs in the specific folder

        for blob in blobs:
            if blob.name.endswith("main.tex"):
                continue

            # Removing the source folder path from the blob name
            relative_path = blob.name[len(source_path) :]
            if not relative_path:  # Skip if it's just the folder itself
                continue

            # Create local path for blob
            local_path = os.path.join(self.output_path, relative_path)
            if PY_ENV == "test":
                local_path = local_path.replace("\\", "/")
            # local_path = local_path.replace("/", "\\") # For local
            # Create necessary local directories
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # Download the blob to the local path
            blob.download_to_filename(local_path)
            print(f"Downloaded {blob.name} to {local_path}")

    def download_bucket_folder(self):
        """Download all files from a specific folder in the GCS bucket to the local directory."""
        if self.cl_template_path:
            source_folder = self.cl_template_path
            # Ensure the source folder path is correctly formatted
            if not self.cl_template_path.endswith("/"):
                source_folder = self.cl_template_path + "/"
                self.download_files_from_path(source_folder)

        if self.cv_template_path:
            source_folder = self.cv_template_path
            # Ensure the source folder path is correctly formatted
            if not self.cv_template_path.endswith("/"):
                source_folder = self.cv_template_path + "/"
                self.download_files_from_path(source_folder)

    def read_job_desc(self):
        """reads the job description from the path"""
        with open(
            self.jd_path,
            "r",
        ) as file:
            self.job_desc_str = file.read()

    def scrape_job_desc(self):
        """Scrapes job data from link and"""
        if not os.path.exists(self.jd_path):
            url = [self.job_desc_link]
            loader = AsyncHtmlLoader(url)
            docs = loader.load()
            html2text = Html2TextTransformer()
            docs_transformed = html2text.transform_documents(docs)
            job_desc_obj = self.html_to_schema(docs_transformed)
            self.write_jd_to_txt(job_desc_obj["text"][0])
            print("JD successfully scraped")

    def html_to_schema(self, html_text):
        """Extracts schema of job description from HTML to given schema"""
        llm = ChatOpenAI(model="gpt-4", temperature=0)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a world class algorithm for extracting information in structured formats.",
                ),
                (
                    "human",
                    "Use the given format to extract detailed information from the following input: {input}",
                ),
                ("human", "Tip: Make sure to answer in the correct format"),
            ]
        )

        chain = create_extraction_chain_pydantic(
            JobDescription, llm, prompt, verbose=True
        )
        job_description = chain.invoke(html_text[0].page_content)
        return job_description

    def write_jd_to_txt(self, job_desc: JobDescription):
        """Write job description object to text file"""
        with open(
            self.jd_path,
            "w",
        ) as file:
            file.write("Job Title: {}\n".format(job_desc.job_title))
            file.write("\n")
            file.write("Company Overview:\n{}".format(job_desc.about_company))
            file.write("\n")
            file.write("------------------")
            file.write("\n")
            file.write("About the job:\n{}\n".format(job_desc.job_overview))
            file.write("\n")
            file.write(
                "Job responsibilities:\n{}\n".format(job_desc.job_responsibilities)
            )
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

    def generate_cv(self):
        """initializes llm, creates cv tex file and compiles it"""
        print(f"user name: {self.user_name}")
        print(f"user info str: {self.user_info_str}")
        print(f"cv prompt: {self.cv_prompt_str}")
        CV_EXPERT_BOT = CVExpertBot(
            user_name=self.user_name,
            user_info_str=self.user_info_str,
            cv_prompt_str=self.cv_prompt_str,
        )
        print("Initiating CV tex file creation")
        CV_EXPERT_BOT.generate_latex_output(self.output_path, self.cv_compilation_type)
        # CV_EXPERT_BOT.compile_tex_file(self.cv_template_path)

    def generate_cl(self):
        CV_EXPERT_BOT = CVExpertBot(
            user_name=self.user_name,
            user_info_str=self.user_info_str,
            cl_template_str=self.cl_prompt_str,
            jd_str=self.job_desc_str,
        )
        print("Initiating CL tex file creation")
        CV_EXPERT_BOT.generate_cl_output(self.output_path, self.cl_compilation_type)


# if __name__ == '__main__':
#     os.environ['OPENAI_API_KEY'] = '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'
#     bot = BotCreateCV("cv_templates/cv_template_3","user/Shresht_Shetty",
#                 "https://www.seek.com.au/job/71297266?type=standard#sol=9a67e2171fa56642ab1b092d4ad01256cb8e6a6f",
#                 "C:\\Users\shres\Projects\EasyCV\App\python-app\output")
#     bot.generate_cv()
