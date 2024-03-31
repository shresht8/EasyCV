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
from PROMPT_FILE import test_prompt

# from langchain_community.document_loaders import AsyncHtmlLoader
# from langchain_community.document_transformers import Html2TextTransformer
# from langchain_openai import ChatOpenAI


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
    def __init__(self, user_name, user_info_path, cv_template_path):
        self.cv_prompt_str = None
        self.job_desc_str = None
        self.latex_content = None
        self.user_info_str = None
        self.user_name = user_name
        self.user_info_path = user_info_path
        self.cv_template_path = cv_template_path
        self.preprocess_user_date()
        self.read_cv_template()

    def preprocess_user_date(self):
        """reads and preprocesses user info, add logo metadata to user info doc"""
        with open(
            os.path.join(self.user_info_path, "User_Professional_Information.txt"),
            "r",
            encoding="utf-8",
        ) as file:
            self.user_info_str = file.read()

    def read_cv_template(self):
        """reads cv main.tex file from the directory"""
        with open(os.path.join(self.cv_template_path, "cv_prompt.txt"), "rb") as file:
            cv_prompt_bytes = file.read()
        self.cv_prompt_str = cv_prompt_bytes.decode("utf-8")

    def generate_cv(self):
        """initializes llm, creates cv tex file and compiles it"""
        CV_EXPERT_BOT = CVExpertBot(
            self.user_name, self.user_info_str, self.cv_prompt_str
        )
        CV_EXPERT_BOT.generate_latex_output(self.cv_template_path)

        # CV_EXPERT_BOT.compile_tex_file(self.cv_template_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generates CV latex code")
    parser.add_argument("arg1", help="Name of user")
    parser.add_argument("arg2", help="Path to user info directory")
    parser.add_argument("arg3", help="CV Template path")
    args = parser.parse_args()
    os.environ["OPENAI_API_KEY"] = "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"
    bot_create_cv = BotCreateCV(args.arg1, args.arg2, args.arg3)
    print("args passed")
    bot_create_cv.generate_cv()
    print("run completed")
