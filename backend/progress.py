from sqlalchemy.orm import Session
from datetime import datetime
import models

def update_user_progress(db: Session, user_id: int, topic: str) -> models.Progress:
    """
    Increments the chat session count and updates access timestamps for a specific topic.
    Creates a new progress record if the topic hasn't been practiced yet.
    """
    if not topic:
        return None
        
    # Standardize topic names to title case
    topic_normalized = topic.strip().title()
    
    # Query for existing record
    progress = db.query(models.Progress).filter(
        models.Progress.user_id == user_id,
        models.Progress.topic == topic_normalized
    ).first()
    
    if progress:
        progress.chat_count += 1
        progress.last_accessed = datetime.utcnow()
    else:
        progress = models.Progress(
            user_id=user_id,
            topic=topic_normalized,
            chat_count=1,
            last_accessed=datetime.utcnow()
        )
        db.add(progress)
        
    db.commit()
    db.refresh(progress)
    return progress
