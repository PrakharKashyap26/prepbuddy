import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    skill = Column(String, default="Python")
    subscription = Column(String, default="free")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    saved_courses = relationship("SavedCourse", back_populates="user", cascade="all, delete-orphan")
    progress_entries = relationship("Progress", back_populates="user", cascade="all, delete-orphan")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship back to User
    user = relationship("User", back_populates="chats")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    url = Column(String, unique=True, index=True)
    description = Column(Text)

    # Relationship to SavedCourse
    saves = relationship("SavedCourse", back_populates="course", cascade="all, delete-orphan")


class SavedCourse(Base):
    __tablename__ = "saved_courses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))

    # Relationships
    user = relationship("User", back_populates="saved_courses")
    course = relationship("Course", back_populates="saves")


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic = Column(String, index=True)
    chat_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationship back to User
    user = relationship("User", back_populates="progress_entries")
