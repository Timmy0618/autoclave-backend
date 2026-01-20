from urllib.parse import quote_plus
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    basedir = os.path.abspath(os.path.dirname(__file__))
    PORT = int(os.getenv('PORT', 5002))
    BASE_DIR = basedir
    DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
    
    # Database Configuration
    DB_USERNAME = os.getenv('DB_USERNAME', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '1qaz@WSX3edc')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'autoclave')
    
    # RS485 轉以太網設備設定
    FESTO_HOST = os.getenv('FESTO_HOST', '192.168.1.100')
    FESTO_PORT = int(os.getenv('FESTO_PORT', 502))
    FESTO_DEVIATION = int(os.getenv('FESTO_DEVIATION', 3))
    
    # 对密码进行百分号编码
    encoded_password = quote_plus(DB_PASSWORD)

    # 构建数据库URI
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USERNAME}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'autoclave-super-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
