import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

# --- User Schemas ---
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    skill: str = Field(..., min_length=2)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    skill: str
    subscription: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Chat Schemas ---
class ChatRequest(BaseModel):
    message: str
    topic: Optional[str] = None

class ChatOut(BaseModel):
    id: int
    message: str
    response: str
    timestamp: datetime.datetime

    class Config:
        from_attributes = True

# --- Course Schemas ---
class CourseSearch(BaseModel):
    skill: str
    topic: str

class CourseSave(BaseModel):
    title: str
    url: str
    description: Optional[str] = None
class CourseOut(BaseModel):
    id: Optional[int] = None
    title: str
    url: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class SavedCourseOut(BaseModel):
    id: int
    course: CourseOut

    class Config:
        from_attributes = True

# --- Progress Schemas ---
class ProgressOut(BaseModel):
    topic: str
    chat_count: int
    last_accessed: datetime.datetime

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    name: str
    skill: str
    saved_courses_count: int
    chat_sessions_count: int
    topics_practiced_count: int
    progress: List[ProgressOut]
