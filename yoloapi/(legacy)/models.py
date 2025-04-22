from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
from sentence_transformers import SentenceTransformer
from transformers import CLIPProcessor, CLIPModel
import torch

Base = declarative_base()

class ImageEmbedding(Base):
    __tablename__ = 'image_embeddings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    image_id = Column(Integer, unique=True, nullable=False)
    embedding = Column(Vector(512), nullable=False)  # Adjust the vector size as per CLIP embedding
    document = Column(Text, nullable=False) #Here the document refers to context text associated with the embedding
    meta = Column(JSONB)
    def __repr__(self):
        return f"<ImageEmbedding(image_id={self.image_id}, embedding={self.embedding[:10]}...)>"

class TextEmbedding(Base):
    __tablename__ = 'text_embeddings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    text_id = Column(Integer, unique=True, nullable=False)
    document = Column(Text, nullable=False) #Here the document refers to context text associated with the embedding
    embedding = Column(Vector(512), nullable=False)  # Adjust the vector size as per model embedding
    meta = Column(JSONB)
    def __repr__(self):
        return f"<TextEmbedding(text_id={self.text_id}, text={self.text[:10]}..., embedding={self.embedding[:10]}...)>"



