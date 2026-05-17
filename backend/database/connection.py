# database/connection.py
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 環境変数からURLを取得（デフォルトはローカルDocker環境）
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@db:5432/fukuoka_monthly"
)

# Supabase（ポスター等）や特定の環境で古いプレフィックスを置換する処理
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# コネクションプールの設定を追加（本番環境のSupabase対策）
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # 接続が切れていないか毎回チェックする（超重要）
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPIやバッチ処理でセッションを安全に使い回すための依存関数"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
