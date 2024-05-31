# -*- coding: utf-8 -*-
"""Phi3-Mini-Llama-cpp-Langchain.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1QbzNxbjyJp6hdzxOrLWddcLgHKesiFPC
"""

!pip -q install langchain
!pip install llama-cpp-python
!pip install huggingface_hub
!pip install langchain-community

model_name_or_path = "microsoft/Phi-3-mini-4k-instruct-gguf"
model_basename = "Phi-3-mini-4k-instruct-q4.gguf" # the model is in bin format

!lscpu |grep 'Model name'

!lscpu | grep 'Number of Socket(s):'

!lscpu | grep 'Core(s) each processor has/per socket:'

!lscpu | grep 'Number of threads/core:'

from huggingface_hub import hf_hub_download

model_path = hf_hub_download(repo_id=model_name_or_path, filename=model_basename)

#from langchain.llms import LlamaCpp
from langchain_community.llms.llamacpp import LlamaCpp
from langchain import PromptTemplate, LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

#Stream tokens
# Callbacks support token-wise streaming
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
# Verbose is required to pass to the callback manager

llm = LlamaCpp(
      model_path=model_path,
      max_tokens=250,
      callback_manager=callback_manager,
      verbose=True,
      n_threads=2,
      #n_ctx=4096, # Context window
      stop = ['USER:'], # Dynamic stopping when such token is detected.
      temperature = 0.4,
  )

template = """''SYSTEM: You are a helpful assistant, and a expert in mushroom farming
USER: {question}
ASSISTANT: """
prompt = PromptTemplate(template=template, input_variables=["question"])

llm_chain = LLMChain(prompt=prompt, llm=llm)

question = "What do Mushrooms need to grow and reproduce?"

llm_chain.run(question)

#Snippet from

from operator import itemgetter

import panel as pn
from huggingface_hub import hf_hub_download
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_community.llms.llamacpp import LlamaCpp

pn.extension()

REPO_ID = "TheBloke/zephyr-7B-beta-GGUF"
FILENAME = "zephyr-7b-beta.Q5_K_M.gguf"
SYSTEM_PROMPT = "Try to be a silly comedian."


def load_llm(repo_id: str = REPO_ID, filename: str = FILENAME, **kwargs):
    model_path = hf_hub_download(repo_id=repo_id, filename=filename)
    llm = LlamaCpp(model_path=model_path, **kwargs)
    return llm


def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    message = ""
    inputs = {"input": contents}
    for token in chain.stream(inputs):
        message += token
        yield message
    memory.save_context(inputs, {"output": message})


model = load_llm(
    repo_id=REPO_ID,
    filename=FILENAME,
    streaming=True,
    n_gpu_layers=1,
    temperature=0.75,
    max_tokens=2000,
    top_p=1,
)

memory = ConversationSummaryBufferMemory(return_messages=True, llm=model)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)
output_parser = StrOutputParser()
chain = (
    RunnablePassthrough.assign(
        history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
    )
    | prompt
    | model
    | output_parser
)

chat_interface = pn.chat.ChatInterface(
    pn.chat.ChatMessage(
        "Offer a topic and Mistral will try to be funny!", user="System"
    ),
    callback=callback,
    callback_user="Mistral",
)
chat_interface.servable()

"""##### SERVER

"""

# Commented out IPython magic to ensure Python compatibility.
# Setup
# %cd /content/
!rm -rf llama.cpp
!git clone https://github.com/ggerganov/llama.cpp.git
# %cd llama.cpp
!make

# Phi3 -mini
!wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf

# Create a Llama.cpp server (click on the link below after starting inference)
from google.colab.output import eval_js
print(eval_js("google.colab.kernel.proxyPort(12345)"))

# Commented out IPython magic to ensure Python compatibility.
# inference
# %cd /content/llama.cpp
!./server -m Phi-3-mini-4k-instruct-q4.gguf -ngl 9999 -c 0 --port 12345