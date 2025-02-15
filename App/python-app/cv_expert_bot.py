import os
from PROMPT_FILE import test_prompt, COVER_LETTER_PROMPT
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
import re
from constants import PY_ENV, LATEX_API_URL
import requests
from urllib.parse import urljoin


def send_latex_compilation_request(path, compilation_type):
    """Sends a POST request to the LaTeX app for compilation"""
    # subdirectory = os.path.relpath(path, "/app/output")
    payload = {"subdirectory": path, "compilation_type": compilation_type}

    if PY_ENV == "test":
        try:
            response = requests.post(urljoin(LATEX_API_URL, "/compile"), json=payload)
            response.raise_for_status()
            result = response.json()
            print(f"LaTeX compilation result: {result}")
            return result
        except requests.RequestException as e:
            print(f"Error sending request to LaTeX app: {e}")
            return None
    else:
        print(f"Would send POST request to {LATEX_API_URL}")
        print(f"Payload: {payload}")


def extract_latex_output(input_string):
    # Define the regular expression pattern
    pattern = r"```latex(.+?)```"

    # Search for the pattern in the input string
    match = re.search(pattern, input_string, re.DOTALL)

    # If a match is found, return the extracted string, otherwise return the input string
    if match:
        return match.group(1).strip()
    else:
        return input_string.strip()


class CVExpertBot:
    def __init__(
        self,
        user_name: str,
        user_info_str: str,
        cv_prompt_str: str = None,
        jd_str: str = None,
        cl_template_str: str = None,
    ):
        self.job_desc_str = None
        self.test_prompt_full = None
        self.user_name = user_name
        self.user_info_str = user_info_str
        self.cv_prompt_str = cv_prompt_str
        self.jd_str = jd_str
        self.cl_latex_str = cl_template_str
        if self.cv_prompt_str:
            print("Initiating LLM and prompt for CV bot")
            self.__create_llm_chain()
            self.test_prompt = test_prompt.format(TEST_USER_INPUT=user_info_str)
            self.create_prompt_full()
        if self.cl_latex_str:
            print("Initiating LLM and prompt for CL bot")
            self._create_llm_chain_cl()

    def create_prompt_full(self):
        self.test_prompt_full = self.cv_prompt_str + self.test_prompt

    def __create_llm_chain(self):
        """initializes the llm chain"""
        llm = ChatOpenAI(model_name="gpt-4-0125-preview", temperature=0)
        system_prompt = """System Prompt: {System_prompt}"""
        prompt = ChatPromptTemplate.from_template(system_prompt)
        self.llm_chain_cv = (
            {
                "System_prompt": itemgetter("system_prompt"),
            }
            | prompt
            | llm
            | StrOutputParser()
        )

    def _create_llm_chain_cl(self):
        llm = ChatOpenAI(model_name="gpt-4", temperature=0)
        prompt = ChatPromptTemplate.from_template(COVER_LETTER_PROMPT)
        self.llm_chain_cl = (
            {
                "LATEX_TEMPLATE": itemgetter("LATEX_CODE"),
                "USER": itemgetter("USER_INFORMATION"),
                "JD": itemgetter("JOB_INFORMATION"),
            }
            | prompt
            | llm
            | StrOutputParser()
        )

    def generate_latex_output(self, path, compilation_type):
        """generates customised latex output using the llm chain"""
        output_str = self.llm_chain_cv.invoke({"system_prompt": self.test_prompt_full})
        output_str = extract_latex_output(output_str)
        output_file_path = os.path.join(path, "cv_main.tex")
        if PY_ENV == "test":
            output_file_path = output_file_path.replace("\\", "/")
        with open(output_file_path, "w+", encoding="utf-8") as tex_file:
            tex_file.write(output_str)
            print("main_cv.tex file has been written to {}.".format(path))

        # Send request to LaTeX app for compilation
        send_latex_compilation_request(path, compilation_type)

    def generate_cl_output(self, path, compilation_type):
        """generates the cover letter latex output for the user"""
        output_str = self.llm_chain_cl.invoke(
            {
                "LATEX_CODE": self.cl_latex_str,
                "USER_INFORMATION": self.user_info_str,
                "JOB_INFORMATION": self.job_desc_str,
            }
        )

        output_file_path = os.path.join(path, "cl_main.tex".format(name=self.user_name))
        if PY_ENV == "test":
            output_file_path = output_file_path.replace("\\", "/")
        with open(output_file_path, "w", encoding="utf-8") as tex_file:
            tex_file.write(output_str)
            print("main_cl.tex file has been written to {}.".format(path))

        # Send request to LaTeX app for compilation
        send_latex_compilation_request(path, compilation_type)
