import os
from PROMPT_FILE import test_prompt
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser


class CVExpertBot:
    def __init__(self, user_name, user_info_str, cv_prompt_str):
        self.test_prompt_full = None
        self.user_name = user_name
        self.user_info_str = user_info_str
        self.cv_prompt_str = cv_prompt_str
        self.__create_llm_chain()
        self.test_prompt = test_prompt.format(TEST_USER_INPUT=user_info_str)
        self.create_prompt_full()

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

    def generate_latex_output(self, path):
        """generates customised latex output using the llm chain"""
        output_str = self.llm_chain.invoke({"system_prompt": self.test_prompt_full})
        # with open(os.path.join(path, '{name}_CV.tex'.format(name=self.user_name)), 'w', encoding='utf-8') as tex_file:
        with open(os.path.join(path, "main.tex"), "w+", encoding="utf-8") as tex_file:
            tex_file.write(output_str)
            print("main.tex file has been written to {}.".format(path))
