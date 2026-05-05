"""
Quản lý cấu hình ứng dụng từ file .env.
Sử dụng dotenv để load biến môi trường.

Tham chiếu: docs/DOCS-main/skill_env_configuration.md
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Tìm file .env từ thư mục gốc dự án
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(_env_path)


class Settings:
    """
    Cấu hình chung cho toàn bộ ứng dụng.
    DIR_ROOT được xác định từ vị trí file .env để tránh lỗi đường dẫn tương đối.
    """

    # Thư mục gốc của dự án (dựa trên vị trí file .env)
    DIR_ROOT: str = str(Path(__file__).parent.parent)

    # Môi trường: development hoặc production
    ENV: str = os.getenv("ENV", "production")

    # AI Engine
    DEFAULT_LLM: str = os.getenv("DEFAULT_LLM", "openai")
    KEY_API_OPENAI: str = os.getenv("KEY_API_OPENAI", "")
    OPENAI_LLM_MODEL_NAME: str = os.getenv("OPENAI_LLM_MODEL_NAME", "gpt-4o-mini")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_LLM_MODEL_NAME: str = os.getenv("GOOGLE_LLM_MODEL_NAME", "gemini-2.5-flash")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-this-in-production")

    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    OAUTH_REDIRECT_URI: str = os.getenv("OAUTH_REDIRECT_URI", "")

    # CORS
    ALLOW_ORIGINS: list = ["http://localhost:5173", "http://localhost:8001"]


settings = Settings()
