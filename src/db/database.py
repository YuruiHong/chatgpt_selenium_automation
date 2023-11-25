from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()


class Prompt(Base):
    __tablename__ = 'prompts'
    id = Column(Integer, primary_key=True)
    prompt = Column(String, nullable=False)
    response = Column(String)
    created_date = Column(DateTime, default=datetime.now)
    modified_date = Column(DateTime)


class Queue(Base):
    __tablename__ = 'queue'
    id = Column(Integer, primary_key=True)
    prompt_id = Column(Integer, ForeignKey('prompts.id'))
    enqueued_date = Column(DateTime, default=datetime.now)


class StructuredPrompt(Base):
    __tablename__ = 'structured_prompts'
    id = Column(Integer, primary_key=True)
    json_data = Column(JSON)
    template_name = Column(String)
    key = Column(String)


class DatabaseManager:
    def __init__(self, db_url='sqlite:///database.db'):
        self.engine = create_engine(db_url, echo=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def insert_prompt(self, prompt, response=None):
        session = self.Session()
        new_prompt = Prompt(prompt=prompt, response=response)
        session.add(new_prompt)
        session.commit()
        return new_prompt.id

    def enqueue_prompt(self, prompt_id):
        session = self.Session()
        new_queue_entry = Queue(prompt_id=prompt_id)
        session.add(new_queue_entry)
        session.commit()

    def insert_structured_prompt(self, json_data, template_name, key):
        session = self.Session()
        new_structured_prompt = StructuredPrompt(
            json_data=json_data, template_name=template_name, key=key
        )
        session.add(new_structured_prompt)
        session.commit()
        return new_structured_prompt.id


db_manager = DatabaseManager()
