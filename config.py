import os
from dotenv import load_dotenv

load_dotenv()  # 讀取同一層的 .env 檔案，把裡面的內容塞進系統環境變數

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "90409991")
    DB_NAME = os.getenv("DB_NAME", "schedule_ver1")
