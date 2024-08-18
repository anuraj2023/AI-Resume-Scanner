from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from app.jd_structure import jd_structure
from app.logging_config import logger



def extract_jd_data(jd_content: str, llm: ChatOpenAI) -> str:
    
    prompt_template = PromptTemplate.from_template("""
    Extract the following information from the given job description text and format them as another text with given set of items.
    Only include fields that are present in the resume. If a field is not present, mark the value of that field as NA.

    {jd_content}

    Format the extracted information as per the below given sample structure:
    {jd_structure}
                                                   
    """)
    
    chain = (
    prompt_template
    | llm
    | StrOutputParser()
    )

    try:
        logger.info("Invoking the chain")
        result = chain.invoke({"jd_content":jd_content,"jd_structure": jd_structure})
        return result
    except Exception as e:
        logger.exception(f"An error occurred while extracting information from JD: {str(e)}")
        return "Error"