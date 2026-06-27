from dotenv import load_dotenv
import os

load_dotenv()

# Fallback to parent directory if running from backend folder
if not os.getenv("GEMINI_API_KEY"):
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import database
import models
import schemas
import auth
import ai
import course
import progress

from fastapi.staticfiles import StaticFiles

# Initialize database tables on startup
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="PrepBuddy API",
    description="Backend services powering the PrepBuddy study buddy and course explorer.",
    version="1.0.0"
)

# Enable CORS for local-first execution (crucial for file:// protocol browser connections)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files to serve the landing page and frontend over HTTP
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/landing_page", StaticFiles(directory=os.path.join(BASE_DIR, "landing_page"), html=True), name="landing_page")
app.mount("/frontend", StaticFiles(directory=os.path.join(BASE_DIR, "frontend"), html=True), name="frontend")


# --- Root Check Endpoint ---
@app.get("/")
def read_root():
    return {"message": "PrepBuddy Backend Running"}


# --- Authentication Endpoints ---

@app.post("/register", response_model=schemas.UserOut)
def register(user_data: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )
    
    # Hash password and store record
    hashed_pwd = auth.get_password_hash(user_data.password)
    new_user = models.User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_pwd,
        skill=user_data.skill
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login", response_model=schemas.Token)
def login(login_data: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    if not user or not auth.verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )
    
    # Generate access token
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


@app.post("/logout")
def logout():
    """Signout is managed by deleting headers client-side; returns a confirm status."""
    return {"message": "Logged out successfully"}


# --- AI Chat Endpoints ---

@app.post("/chat", response_model=schemas.ChatOut)
def send_chat_message(
    chat_req: schemas.ChatRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if not chat_req.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be blank."
        )
        
    # Get conversational history for user to feed context
    history = db.query(models.Chat).filter(
        models.Chat.user_id == current_user.id
    ).order_by(models.Chat.timestamp.asc()).all()
    
    # Retrieve AI guide reply
    ai_reply = ai.get_ai_response(chat_req.message, history)
    
    # Save the conversation in database
    chat_entry = models.Chat(
        user_id=current_user.id,
        message=chat_req.message,
        response=ai_reply
    )
    db.add(chat_entry)
    db.commit()
    db.refresh(chat_entry)
    
    # Update Practice Progress Stats
    practice_topic = chat_req.topic or current_user.skill
    progress.update_user_progress(db, current_user.id, practice_topic)
    
    return chat_entry


@app.get("/chat/history", response_model=List[schemas.ChatOut])
def get_chat_history(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    chats = db.query(models.Chat).filter(
        models.Chat.user_id == current_user.id
    ).order_by(models.Chat.timestamp.asc()).all()
    return chats


@app.delete("/chat/history")
def clear_chat_history(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    db.query(models.Chat).filter(models.Chat.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Conversation history cleared successfully."}


# --- Course Search & Saving Endpoints ---

@app.post("/courses/search", response_model=List[schemas.CourseOut])
def search_courses(
    search_data: schemas.CourseSearch,
    current_user: models.User = Depends(auth.get_current_user)
):
    # Perform external lookup or mock response lookup
    return course.get_courses(search_data.skill, search_data.topic)


@app.get("/courses/saved", response_model=List[schemas.SavedCourseOut])
def get_saved_courses(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    saved_items = db.query(models.SavedCourse).filter(
        models.SavedCourse.user_id == current_user.id
    ).all()
    return saved_items


@app.post("/courses/save")
def save_course(
    course_data: schemas.CourseSave,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    # 1. Lookup Course URL globally
    course_item = db.query(models.Course).filter(models.Course.url == course_data.url).first()
    if not course_item:
        course_item = models.Course(
            title=course_data.title,
            url=course_data.url,
            description=course_data.description or "No description provided."
        )
        db.add(course_item)
        db.commit()
        db.refresh(course_item)
        
    # 2. Check if user already saved this course
    existing_save = db.query(models.SavedCourse).filter(
        models.SavedCourse.user_id == current_user.id,
        models.SavedCourse.course_id == course_item.id
    ).first()
    
    if existing_save:
        return {"message": "Course is already saved.", "id": existing_save.id}
        
    # 3. Create saved mapping
    new_save = models.SavedCourse(
        user_id=current_user.id,
        course_id=course_item.id
    )
    db.add(new_save)
    db.commit()
    db.refresh(new_save)
    return {"message": "Course saved successfully.", "id": new_save.id}


@app.delete("/courses/remove/{id}")
def remove_saved_course(
    id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    save_item = db.query(models.SavedCourse).filter(
        models.SavedCourse.id == id,
        models.SavedCourse.user_id == current_user.id
    ).first()
    
    if not save_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved course record not found."
        )
        
    db.delete(save_item)
    db.commit()
    return {"message": "Course removed from saved list."}


# --- Progress Reporting Endpoints ---

@app.get("/progress")
def get_user_progress(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    # Fetch all progress rows
    progress_rows = db.query(models.Progress).filter(
        models.Progress.user_id == current_user.id
    ).order_by(models.Progress.last_accessed.desc()).all()
    
    # Calculate counters
    saved_count = db.query(models.SavedCourse).filter(models.SavedCourse.user_id == current_user.id).count()
    chats_count = db.query(models.Chat).filter(models.Chat.user_id == current_user.id).count()
    topics_count = len(progress_rows)
    
    return {
        "name": current_user.name,
        "skill": current_user.skill,
        "saved_courses_count": saved_count,
        "chat_sessions_count": chats_count,
        "topics_practiced_count": topics_count,
        "progress": [
            {
                "topic": row.topic,
                "chat_count": row.chat_count,
                "last_accessed": row.last_accessed
            } for row in progress_rows
        ]
    }
