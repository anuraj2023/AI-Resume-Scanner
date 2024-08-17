from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
import json
from typing import Dict, Any
from app.resume_structure import resume_structure

def format_resumes(resumes):
        return "\n\n".join([f"Resume {i+1}:\n\n{resume}" for i, resume in enumerate(resumes)])


def extract_resume_data(multiple_resumes: list, llm: ChatOpenAI) -> Dict[str, Any]:
    
    resume_content_list = []
    
    for i in range(len(multiple_resumes)):
        resume_content_list.append(multiple_resumes[i]["Content"])
    
    prompt_template = PromptTemplate.from_template("""
    Extract the following information from all the given resumes text and format them as JSON objects inside JSON array. 
    Calculate total work experience by adding up the experience at different companies. In case, if you are not able to calculate, state it as NA. 
    Only include fields that are present in the resume. If a field is not present, mark the value of that field as NA in JSON.

    {resume_text}

    Format the extracted information as JSON array, following this structure:
    {json_structure}

    Ensure the output is valid JSON array without back-ticks and contains only the extracted information without any additional text.
    """)
    chain = (
    {"resume_text": RunnablePassthrough(), "json_structure": lambda _: json.dumps(resume_structure, indent=2)}
    | prompt_template
    | llm
    | JsonOutputParser()
    )

    # Run the chain
    try:
        resumes = format_resumes(resume_content_list)
        result = chain.invoke({"resume_text":resumes})
        return result
    except Exception as e:
        return {
            "error": f"An error occurred while converting resume to JSON: {str(e)}"
        }
