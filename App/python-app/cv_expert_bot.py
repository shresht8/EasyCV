import os
from PROMPT_FILE import test_prompt, COVER_LETTER_PROMPT
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser


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
            self.__create_llm_chain()
            self.test_prompt = test_prompt.format(TEST_USER_INPUT=user_info_str)
            self.create_prompt_full()
        if self.cl_latex_str:
            self._create_llm_chain_cl()

    def create_prompt_full(self):
        self.test_prompt_full = self.cv_prompt_str + self.test_prompt

    def __create_llm_chain(self):
        """initializes the llm chain"""
        llm = ChatOpenAI(model_name="gpt-4-0125-preview", temperature=0)
        system_prompt = """System Prompt: {System_prompt}"""
        prompt = ChatPromptTemplate.from_template(system_prompt)
        self.llm_chain = (
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
        self.llm_chain = (
            {
                "LATEX_TEMPLATE": itemgetter("LATEX_CODE"),
                "USER": itemgetter("USER_INFORMATION"),
                "JD": itemgetter("JOB_INFORMATION"),
            }
            | prompt
            | llm
            | StrOutputParser()
        )

    def generate_latex_output(self, path):
        """generates customised latex output using the llm chain"""
        output_str = self.llm_chain.invoke({"system_prompt": self.test_prompt_full})
        # with open(os.path.join(path, '{name}_CV.tex'.format(name=self.user_name)), 'w', encoding='utf-8') as tex_file:
        with open(
            os.path.join(path, "main_cv.tex"), "w+", encoding="utf-8"
        ) as tex_file:
            tex_file.write(output_str)
            print("main_cv.tex file has been written to {}.".format(path))

    def generate_cl_output(self, path):
        """generates the cover letter latex output for the user"""
        output_str = self.llm_chain.invoke(
            {
                "LATEX_CODE": self.cl_latex_str,
                "USER_INFORMATION": self.user_info_str,
                "JOB_INFORMATION": self.job_desc_str,
            }
        )

        with open(
            os.path.join(path, "main_cl.tex".format(name=self.user_name)),
            "w",
            encoding="utf-8",
        ) as tex_file:
            # with open(os.path.join(path, 'main.tex'.format(name=self.user_name)), 'w', encoding='utf-8') as tex_file:
            tex_file.write(output_str)
            print("main_cl.tex file has been written to {}.".format(path))
