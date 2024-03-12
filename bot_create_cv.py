from cv_expert_bot import CVExpertBot
from langchain.document_loaders import AsyncHtmlLoader
from langchain.document_transformers import Html2TextTransformer
from langchain.pydantic_v1 import BaseModel, Field
from typing import Optional
import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains.openai_functions import (
    create_extraction_chain_pydantic,
)
import argparse


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
    def __init__(self, user_name, user_info_path, job_desc_link, cv_template_path):
        self.job_desc_str = None
        self.latex_content = None
        self.user_info_str = None
        self.user_name = user_name
        self.user_info_path = user_info_path
        self.job_desc_link = job_desc_link
        self.cv_template_path = cv_template_path
        self.preprocess_user_date()
        self.scrape_job_desc()
        self.read_cv_template()
        self.read_job_desc()

    def preprocess_user_date(self):
        """reads and preprocesses user info, add logo metadata to user info doc"""
        with open(
            os.path.join(self.user_info_path, "Curated_User_Information.txt"),
            "r",
            encoding="utf-8",
        ) as file:
            self.user_info_str = file.read()

    def read_cv_template(self):
        """reads cv main.tex file from the directory"""
        with open(os.path.join(self.cv_template_path, "main.tex"), "rb") as file:
            latex_content_bytes = file.read()
        self.latex_content = latex_content_bytes.decode("utf-8")

    def read_job_desc(self):
        """reads the job description from the path"""
        with open(
            os.path.join(self.user_info_path, f"{self.user_name}_job_description.txt"),
            "r",
        ) as file:
            self.job_desc_str = file.read()

    def scrape_job_desc(self):
        """Scrapes job data from link and"""
        if not os.path.exists(
            os.path.join(self.user_info_path, f"{self.user_name}_job_description.txt")
        ):
            url = [self.job_desc_link]
            loader = AsyncHtmlLoader(url)
            docs = loader.load()
            html2text = Html2TextTransformer()
            docs_transformed = html2text.transform_documents(docs)
            job_desc_obj = self.html_to_schema(docs_transformed)
            self.write_jd_to_txt(job_desc_obj)

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
            os.path.join(self.user_info_path, f"{self.user_name}_job_description.txt"),
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
        CV_EXPERT_BOT = CVExpertBot(
            self.user_name, self.user_info_str, self.job_desc_str, self.latex_content
        )
        prompt_str_input = CV_EXPERT_BOT.generate_latex_output(self.cv_template_path)
        return prompt_str_input
        # CV_EXPERT_BOT.compile_tex_file(self.cv_template_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generates CV latex code")
    parser.add_argument("arg1", help="Name of user")
    parser.add_argument("arg2", help="Path to user info directory")
    parser.add_argument("arg3", help="Job URL")
    parser.add_argument("arg4", help="CV Template path")
    args = parser.parse_args()
    os.environ["OPENAI_API_KEY"] = "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"
    bot_create_cv = BotCreateCV(args.arg1, args.arg2, args.arg3, args.arg4)
    print("args passed")
    prompt_str = bot_create_cv.generate_cv()
    print("run completed")
