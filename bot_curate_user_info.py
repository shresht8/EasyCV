from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
import os
from PROMPT_FILE import CV_EXPERT_PROMPT


class CurateUserInfo:
    def __init__(self, user_info_path):
        self.llm_chain = None
        self.user_info_str = None
        self.user_info_path = user_info_path
        self.init_bot()

    def init_bot(self):
        llm = ChatOpenAI(model_name="gpt-4", temperature=0)
        prompt = ChatPromptTemplate.from_template(CV_EXPERT_PROMPT)
        self.llm_chain = (
            {"USER_INFORMATION": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

    def generate_output(self, output_path):
        with open(
            os.path.join(self.user_info_path, "User_Professional_Information.txt"),
            "r",
            encoding="utf-8",
        ) as file:
            user_info_str = file.read()
        output_str = self.llm_chain.invoke(user_info_str)
        with open(
            os.path.join(self.user_info_path, "Curated_User_Information.txt"),
            "w",
            encoding="utf-8",
        ) as file:
            file.write(output_str)
