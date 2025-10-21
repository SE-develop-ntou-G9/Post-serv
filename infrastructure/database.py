from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from databases import Database
from dotenv import load_dotenv
import os

load_dotenv()

URL_DATABASE = os.getenv("DB_URL")

engine = create_engine(URL_DATABASE)

database = Database(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
