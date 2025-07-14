from google import genai
from google.genai import types
from prompts import parser_prompt
import pathlib


class ParserService:
    
    def __init__(self, client: genai.Client) -> None:
        self.client = client

    def parse_cv_to_markdown(self, filepath: str) -> str:
        file_path = pathlib.Path(filepath)
        
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(
                    data=file_path.read_bytes(),
                    mime_type='application/pdf',
                ),
                parser_prompt
            ],
        )
        
        return response.text