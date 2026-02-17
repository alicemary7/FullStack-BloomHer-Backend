from dotenv import load_dotenv
import os 
load_dotenv()

DB_USERNAME=os.getenv("DB_USERNAME")
DB_PASSWORD=os.getenv("DB_PASSWORD")
DB_HOSTNAME=os.getenv("DB_HOSTNAME")
DB_PORT=os.getenv("DB_PORT")
DATABASE=os.getenv("DB_DATABASE")

# Auth Settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-it-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))