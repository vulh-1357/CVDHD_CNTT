from parser import ParserService
from graph_db import GraphDBService
from extractor import ExtractorService 
from google import genai
from dotenv import load_dotenv
import os 
import logging

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Hiển thị trên console
        logging.FileHandler('app.log')  # Lưu vào file
    ]
)

logger = logging.getLogger(__name__)

load_dotenv()

def main():
    file_name = "LeHoangVu_CV_v4.pdf"
    api_key = os.getenv("GOOGLE_API_KEY")
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    
    client = genai.Client(api_key=api_key)
    parser_service = ParserService(client)
    extractor_service = ExtractorService(client)
    graph_db_service = GraphDBService(uri=uri, user=user, password=password)

    markdown_content = parser_service.parse_cv_to_markdown(file_name)
    logger.info(f"Parsed CV to markdown successfully. Markdown content: {markdown_content}")

    raw_results = extractor_service.extract_raw(markdown_content)
    logger.info(f"Extracted raw results from markdown. Results: {raw_results}")
    
    entities = extractor_service.extract_entities(raw_results)
    logger.info(f"Extracted {len(entities)} entities")
    
    relationships = extractor_service.extract_relationships(raw_results)
    logger.info(f"Extracted {len(relationships)} relationships")

    graph_db_service.import_data(file_name, markdown_content, entities, relationships)
    
main()