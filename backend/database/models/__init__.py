# database/models/__init__.py
from sqlalchemy import text  # 💡 text をインポートに追加

from database.connection import Base, engine

# 分割したモデルをここに集約
from database.models.property import Property


def create_tables():
    """すべてのテーブルを一括作成・更新する"""
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()  # 拡張機能の有効化を確定（コミット）させる

    # すべてのモデルをDBに反映
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
    print("すべてのテーブルの作成・更新が完了しました！")
