from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os 

load_dotenv()

Base = declarative_base()

class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(String, nullable=False)
    rephrased_question = Column(String, nullable=True)
    sub_questions = Column(JSONB, nullable=True)  # Dùng JSONB cho PostgreSQL
    answer = Column(String, nullable=True)
    

user = os.getenv('POSTGRES_USER', 'postgres')
password = os.getenv('POSTGRES_PASSWORD', 'postgres')
database = os.getenv('POSTGRES_DB', 'chatbot')
host = os.getenv('POSTGRES_HOST', 'localhost')
port = os.getenv('POSTGRES_PORT', '15432')
DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    """
    Initializes the database and creates tables if they don't exist.
    """
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
    print("Database initialized and 'message' table created if it didn't exist.")

