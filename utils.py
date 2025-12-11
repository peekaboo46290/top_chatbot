import json
import fitz  
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from loader import Theorem

class BaseLogger:
    def __init__(self) -> None:
        self.info = print

def extract_title_and_question(input_string:str):
    lines = input_string.strip().split('\n')
    
    title = ""
    question = ""
    is_question = False
    
    for line in lines:
        if line.startswith("Title:"):
            title = line.split("Title: ", 1)[1].strip()
        elif line.startswith("Question:"):
            question +=  line.split("Question: ", 1)[1].strip()
            is_question = True
        elif is_question:
            question += "\n" + line.strip()

    return title, question


def read_pdf_pymupdf(pdf_path: str) -> str:
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text() + "\n\n"
    doc.close()
    return text


def initialize_smth(driver, logger= BaseLogger()):
    constraints_and_indexes = [
        "CREATE CONSTRAINT theorem_name IF NOT EXISTS FOR (t:Theorem) REQUIRE t.name IS UNIQUE",
        "CREATE INDEX subject_name IF NOT EXISTS FOR (s:Subject) ON (s.name)",
        "CREATE INDEX domain_name IF NOT EXISTS FOR (d:Domain) ON (d.name)",
        "CREATE INDEX theorem_type IF NOT EXISTS FOR (t:Theorem) ON (t.type)"
    ]
    for query in constraints_and_indexes:
        try:
            driver.query(query)
        except Exception as e:
            logger.info(f"Schema element already exists or error: {e}")


def extract_from_text(chain, text: str, logger= BaseLogger()) -> List[Theorem]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2500,
        chunk_overlap=250,
        separators=["\n\n\n", "\n\n", "\n", ". ", " ", ""],
        length_function=len
    )
    
    chunks = text_splitter.split_text(text)
    logger.info(f"Split text into {len(chunks)} chunks")
    
    all_theorems = []
    for i, chunk in enumerate(chunks, 1):
        logger.info(f"Processing chunk {i}/{len(chunks)}")
        theorems = extract_from_chunk(chain, chunk)
        all_theorems.extend(theorems)
        logger.info(f"Extracted {len(theorems)} theorems from chunk {i}")
    
    # Remove duplicates based on name
    unique_theorems = {t.name: t for t in all_theorems}.values()
    logger.info(f"Total unique theorems extracted: {len(unique_theorems)}")
    
    return list(unique_theorems)

def extract_from_chunk(chain, chunk: str, logger= BaseLogger()) -> List[Theorem]:
        try:
            response = chain.run(text=chunk)
            return parse_response(response, logger)
        except Exception as e:
            logger.error(f"Error extracting from chunk: {e}")
            return []

def parse_response(response:str, logger= BaseLogger()):
    try:
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            logger.warning("No JSON found in response")
            return []
        
        data = json.loads(json_match.group())
        
        theorems = []
        for thm_data in data.get('theorems', []):
            try:
                theorem = Theorem(**thm_data)
                theorems.append(theorem)
            except Exception as e:
                logger.warning(f"Failed to validate theorem: {e}")
                continue
        
        return theorems
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error parsing response: {e}")
        return []