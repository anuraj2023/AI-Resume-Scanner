import sys
sys.dont_write_bytecode = True

from langchain_openai.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.docstore.document import Document


class ChatBot():
  def __init__(self, api_key: str, model: str):
    self.llm = ChatOpenAI(
      model=model, 
      api_key=api_key, 
      temperature=0.1
    )

  def generate_message_stream(self, question: str, docs: list, history: list, prompt_cls: str):
    context = "\n\n".join(doc.page_content if isinstance(doc, Document) else str(doc) for doc in docs)
    if prompt_cls == "retrieve_matching_applicant_by_jd":
      system_message = SystemMessage(content="""
        You are an expert in talent acquisition that helps determine the best candidate among multiple suitable resumes.
        You should provide some detailed explanations for the best resume choice.
        If you don't know the answer, just say that you don't know, do not try to make up an answer.
        Do not answer any questions which is not related to the resumes and job description uploaded.
        If a question is asked about a resume which is not provided, do not answer, just  say I don't know.                                                           
      """)

      user_message = HumanMessage(content=f"""
        Chat history: {history}                            
        Context: {context}
        Question: {question}
      """)

    else:
      system_message = SystemMessage(content="""
        You are an expert in talent acquisition that helps analyze resumes to assist resume screening.
        You may use the following pieces of context and chat history to answer your question. 
        Do not mention in your response that you are provided with a chat history.
        If you don't know the answer, just say that you don't know, do not try to make up an answer.
        Do not answer any questions which is not related to the resumes and job description uploaded.
        If a question is asked about a resume which is not provided, do not answer, just  say I don't know. 
      """)

      user_message = HumanMessage(content=f"""
        Chat history: {history}
        Question: {question}
        Context: {context}
      """)

    #stream = self.llm.stream([system_message, user_message])
    stream = self.llm.invoke([system_message, user_message])
    print("stream is : ", stream)

    return stream