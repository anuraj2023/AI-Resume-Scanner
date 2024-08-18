from dotenv import load_dotenv
import os

load_dotenv()

OPEN_AI_KEY = os.getenv('OPEN_AI_API_KEY')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
AWS_REGION = os.getenv('AWS_REGION')
TIKA_SERVER_URL = os.getenv('TIKA_SERVER_URL')
MILVUS_URI = os.getenv('MILVUS_URI')
MILVUS_API_KEY = os.getenv('MILVUS_API_KEY')


def get_env_vars():
    return {
        'OPEN_AI_KEY': OPEN_AI_KEY,
        'AWS_ACCESS_KEY': AWS_ACCESS_KEY,
        'AWS_SECRET_KEY': AWS_SECRET_KEY,
        'S3_BUCKET_NAME': S3_BUCKET_NAME,
        'AWS_REGION' : AWS_REGION,
        'TIKA_SERVER_URL': TIKA_SERVER_URL,
        'MILVUS_URI': MILVUS_URI,
        'MILVUS_API_KEY': MILVUS_API_KEY
    }