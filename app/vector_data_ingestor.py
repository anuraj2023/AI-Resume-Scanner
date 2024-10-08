import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Milvus
from langchain_community.document_loaders import DataFrameLoader
from tqdm import tqdm
# from pymilvus import connections
#from app.milvus import connections
from config import get_env_vars
from app.logging_config import logger

env_vars = get_env_vars()
MILVUS_URI = env_vars['MILVUS_URI']
MILVUS_API_KEY = env_vars['MILVUS_API_KEY'] 

def ingest(df: pd.DataFrame, content_column: str, embedding_model, batch_size: int = 1000):
    try:
        if content_column not in df.columns:
            raise ValueError(f"Column '{content_column}' not found in DataFrame")

        logger.info(f"DataFrame shape: {df.shape}")
        logger.info(f"Columns: {df.columns.tolist()}")
        logger.info(f"Sample data from '{content_column}': {df[content_column].head()}")

        loader = DataFrameLoader(df, page_content_column=content_column)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50,
            length_function=len
        )
        documents = loader.load()
        logger.info(f"Number of documents loaded: {len(documents)}")

        if not documents:
            raise ValueError("No documents were loaded. Please check your DataFrame and content column.")

        document_chunks = text_splitter.split_documents(documents)
        logger.info(f"Number of document chunks: {len(document_chunks)}")

        if not document_chunks:
            raise ValueError("No document chunks were created. Please check your text splitter settings.")

        # Connect to hosted Milvus
        # connections.connect(
        #     alias="default", 
        #     uri=MILVUS_URI,
        #     token=MILVUS_API_KEY
        # )

        # Initialize Milvus with the first batch
        first_batch = document_chunks[:batch_size]
        vectorstore_db = Milvus.from_documents(
            first_batch,
            embedding_model,
            collection_name="resume_collection",
            connection_args={
                "uri": MILVUS_URI,
                "token": MILVUS_API_KEY
            }
        )

        # Add remaining documents in batches
        for i in tqdm(range(batch_size, len(document_chunks), batch_size)):
            batch = document_chunks[i:i+batch_size]
            try:
                vectorstore_db.add_documents(batch)
            except Exception as e:
                logger.error(f"Error adding batch {i//batch_size + 1}: {str(e)}")
                logger.error(f"Problematic batch: {batch}")
                raise

        logger.info("Ingestion completed successfully")
        return vectorstore_db

    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}")
        raise
    finally:
        pass
        # Disconnect from Milvus
        #connections.disconnect("default")
