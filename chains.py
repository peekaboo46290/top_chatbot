from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_neo4j import Neo4jVector
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from typing import List, Any
from utils import BaseLogger, extract_title_and_question, format_docs




def load_embedding_model(logger=BaseLogger(), config={}):
    embedding = OllamaEmbeddings(
        base_url=config["ollama_base_url"], model=config["llm"]
    )
    dimension = 4096
    logger.info("Embedding: Using Ollama")
    return embedding, dimension 

def load_llm(llm_name:string, logger:BaseLogger(), ollama_base_url):
    logger.info(f"LLM: Using Ollama: {llm_name}")
    return ChatOllama(
        temperature=0,
        base_url=ollama_base_url,
        model=llm_name,
        streaming=True,
        # seed=2,
        top_k=10,  # A higher value (100) will give more diverse answers, while a lower value (10) will be more conservative.
        top_p=0.3,  # Higher value (0.95) will lead to more diverse text, while a lower value (0.5) will generate more focused text.
        num_ctx=3072,  # Sets the size of the context window used to generate the next token.
    )


def configure_llm_only_chain(llm):
    # LLM only response
    template = """
    You are a helpful assistant that helps a support agent with answering math questions.
    If you don't know the answer, just say that you don't know, you must not make up an answer.
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = "{question}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )
    chain = chat_prompt | llm | StrOutputParser()
    return chain