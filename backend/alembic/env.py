import os
import sys
from logging.config import fileConfig

# プロジェクトルートをパスに通す
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# モデルを検知させるために、分割したモデルのルートをインポート
import database.models
from alembic import context
from database.connection import DATABASE_URL, Base
from sqlalchemy import engine_from_config, pool, text

# AlembicのConfigオブジェクト
config = context.config

# ログ設定の読み込み
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# SQLAlchemyのメタデータをターゲットに指定
target_metadata = Base.metadata

# 環境変数から取得したURLを強制適用
config.set_main_option("sqlalchemy.url", DATABASE_URL)


def include_object(object, name, type_, reflected, compare_to):
    """ホワイトリスト方式: 自分が管理するオブジェクト以外はすべて Alembic の対象外にする"""

    # 自分が作成・管理するテーブル名（今後テーブルが増えたらここに追加する）
    MY_MANAGED_TABLES = {"properties", "alembic_version"}

    if type_ == "table":
        # テーブル名が小文字でも大文字でも、ホワイトリストに含まれていなければ完全に無視
        if name.lower() not in MY_MANAGED_TABLES:
            return False

    elif type_ == "index":
        # インデックスも、自分の管理テーブル（properties）に関するもの以外は無視
        if not (
            name and ("properties" in name.lower() or "idx_properties" in name.lower())
        ):
            return False

    return True


def run_migrations_offline() -> None:
    """オフラインモードでの実行"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,  # オフラインでも一応適用
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """オンラインモードでの実行（通常はこちら）"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # マイグレーション前に PostGIS 拡張を確実に有効化
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,  # 👈 ここでフィルターを適用
        )

        with context.begin_transaction():
            context.run_migrations()


# 実行モードの判定
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
