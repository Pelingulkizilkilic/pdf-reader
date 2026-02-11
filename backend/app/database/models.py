# app/database/models.py
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.database import Base
import datetime


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    pdf_documents = relationship("PDFDocument", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")


class PDFDocument(Base):
    __tablename__ = "pdf_documents"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    page_count = Column(Integer, nullable=True)
    chunk_count = Column(Integer, nullable=True)
    vector_store_path = Column(String, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    processing_error = Column(Text, nullable=True)
    pdf_metadata = Column(JSON, default={})  # metadata → pdf_metadata DEĞİŞTİR
    
    # Relationships
    user = relationship("User", back_populates="pdf_documents")
    conversations = relationship("Conversation", back_populates="pdf_document")


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    pdf_id = Column(String, ForeignKey("pdf_documents.id"), nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    pdf_document = relationship("PDFDocument", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_user = Column(Boolean, default=True)  # True: user message, False: AI response
    message_metadata = Column(JSON, default={})  # metadata → message_metadata DEĞİŞTİR
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    api_key = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")