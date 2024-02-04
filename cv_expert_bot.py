from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
from PROMPT_FILE import LATEX_PROMPT, CHECK_SYNTAX_PROMPT
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.chains import SequentialChain
from transformers import GPT2Tokenizer

# Initialize the tokenizer



class CVExpertBot():
    def __init__(self, user_name ,user_info_str, job_desc_str, latex_code_str):
        self.user_name = user_name
        self.user_info_str = user_info_str
        self.job_desc_str = job_desc_str
        self.latex_code_str = latex_code_str
        self.__create_llm_chain()
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.count_input_tokens()

    def count_input_tokens(self):
        formatted_prompt = LATEX_PROMPT.format(LATEX_CODE=self.latex_code_str, USER_INFORMATION=self.user_info_str,
                                         JOB_INFORMATION=self.job_desc_str)
        # Tokenize and count
        tokenized_prompt = self.tokenizer.encode(formatted_prompt)
        number_of_tokens = len(tokenized_prompt)

        print(f"Number of tokens in the prompt: {number_of_tokens}")


    def __create_llm_chain(self):
        """initializes the llm chain"""
        llm = ChatOpenAI(model_name='gpt-4', temperature=0)
        self.llm_chain = LLMChain(
            llm=llm,
            prompt=PromptTemplate(input_variables=['LATEX_CODE', 'USER_INFORMATION', 'JOB_INFORMATION'],
                                  template=LATEX_PROMPT),
            output_key='input_latex_code'
        )
        self.correction_chain = LLMChain(
            llm=llm,
            prompt=PromptTemplate(input_variables=['input_latex_code'], template=CHECK_SYNTAX_PROMPT),
            output_key="output_latex_code"
        )
        self.overall_chain = SequentialChain(chains=[self.llm_chain, self.correction_chain],
                                             input_variables=['LATEX_CODE', 'USER_INFORMATION', 'JOB_INFORMATION'],
                                             output_variables=['output_latex_code'],
                                             verbose=True)

    def generate_latex_output(self, path):
        """generates customised latex output using the llm chain"""
        # output_str = self.overall_chain({"LATEX_CODE":self.latex_code_str, "USER_INFORMATION": self.user_info_str,
        #                                  "JOB_INFORMATION":self.job_desc_str})
        output_str = self.llm_chain.predict(LATEX_CODE=self.latex_code_str, USER_INFORMATION=self.user_info_str,
                                         JOB_INFORMATION=self.job_desc_str)
        self.count_output_tokens(output_str)
        with open(os.path.join(path, '{name}_CV.tex'.format(name=self.user_name)), 'w', encoding='utf-8') as tex_file:
        # with open(os.path.join(path, 'main.tex'.format(name=self.user_name)), 'w', encoding='utf-8') as tex_file:
            tex_file.write(output_str)

    def count_output_tokens(self, output_string):
        # Tokenize and count
        tokenized_prompt = self.tokenizer.encode(output_string)
        number_of_tokens = len(tokenized_prompt)

        print(f"Number of tokens in the output: {number_of_tokens}")


