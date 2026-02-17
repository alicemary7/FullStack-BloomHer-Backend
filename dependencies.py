from db.database import SessionLocal

def connect_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()