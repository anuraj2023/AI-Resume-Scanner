from tika import parser
from config import get_env_vars

env_vars = get_env_vars()
TIKA_SERVER_URL = env_vars['TIKA_SERVER_URL']

def extract_text_from_file(file_content):
    try:
        parsed_file = parser.from_buffer(file_content, serverEndpoint=TIKA_SERVER_URL)
        if 'content' not in parsed_file or parsed_file['content'] is None:
            raise ValueError("Tika parser failed to extract content")
        return parsed_file["content"]
    except Exception as e:
        raise Exception(f"Error extracting text from file: {str(e)}")