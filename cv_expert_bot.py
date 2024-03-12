import os
from PROMPT_FILE import LATEX_PROMPT
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from transformers import GPT2Tokenizer
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser

# Initialize the tokenizer


class CVExpertBot:
    def __init__(self, user_name, user_info_str, job_desc_str, latex_code_str):
        self.user_name = user_name
        self.user_info_str = user_info_str
        self.job_desc_str = job_desc_str
        self.latex_code_str = latex_code_str
        self.__create_llm_chain()
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.count_input_tokens()

    def count_input_tokens(self):
        formatted_prompt = LATEX_PROMPT.format(
            LATEX_CODE=self.latex_code_str,
            USER_INFORMATION=self.user_info_str,
            JOB_INFORMATION=self.job_desc_str,
        )
        # Tokenize and count
        tokenized_prompt = self.tokenizer.encode(formatted_prompt)
        number_of_tokens = len(tokenized_prompt)

        print(f"Number of tokens in the prompt: {number_of_tokens}")

    def __create_llm_chain(self):
        """initializes the llm chain"""
        llm = ChatOpenAI(model_name="gpt-4", temperature=0)
        prompt = ChatPromptTemplate.from_template(LATEX_PROMPT)
        self.llm_chain = (
            {
                "LATEX_CODE": itemgetter("LATEX_CODE"),
                "USER_INFORMATION": itemgetter("USER_INFORMATION"),
                "JOB_INFORMATION": itemgetter("JOB_INFORMATION"),
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        # self.llm_chain = LLMChain(
        #     llm=llm,
        #     prompt=PromptTemplate(
        #         input_variables=["LATEX_CODE", "USER_INFORMATION", "JOB_INFORMATION"],
        #         template=LATEX_PROMPT,
        #     ),
        #     output_key="input_latex_code",
        # )

    def generate_latex_output(self, path):
        """generates customised latex output using the llm chain"""
        # output_str = self.overall_chain({"LATEX_CODE":self.latex_code_str, "USER_INFORMATION": self.user_info_str,
        #                                  "JOB_INFORMATION":self.job_desc_str})
        output_str = self.llm_chain.invoke(
            {
                "LATEX_CODE": self.latex_code_str,
                "USER_INFORMATION": self.user_info_str,
                "JOB_INFORMATION": self.job_desc_str,
            }
        )
        input_str = LATEX_PROMPT.format(
            LATEX_CODE=self.latex_code_str,
            USER_INFORMATION=self.user_info_str,
            JOB_INFORMATION=self.job_desc_str,
        )
        self.count_output_tokens(output_str)
        with open(
            os.path.join(path, "{name}_CV.tex".format(name=self.user_name)),
            "w",
            encoding="utf-8",
        ) as tex_file:
            # with open(os.path.join(path, 'main.tex'.format(name=self.user_name)), 'w', encoding='utf-8') as tex_file:
            tex_file.write(output_str)
        return input_str

    def count_output_tokens(self, output_string):
        # Tokenize and count
        tokenized_prompt = self.tokenizer.encode(output_string)
        number_of_tokens = len(tokenized_prompt)

        print(f"Number of tokens in the output: {number_of_tokens}")
