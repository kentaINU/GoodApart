import os

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# DATABASE_URL を取得
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@db:5432/fukuoka_monthly"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String, index=True)
    price_text = Column(String)
    price_int = Column(Integer)
    geom = Column(Geometry(geometry_type="POINT", srid=4326))
    is_geocoded = Column(Boolean, default=False)


# テーブルを一括作成
def create_tables():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
    print("propertiesテーブルを作成しました")
