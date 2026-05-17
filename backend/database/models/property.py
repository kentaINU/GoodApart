# database/models/property.py
from geoalchemy2 import Geometry
from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from database.connection import Base


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    site_name = Column(String, index=True, nullable=False, default="good_monthly")
    source_url = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, index=True)
    address = Column(String, index=True)
    price_text = Column(String)
    price_int = Column(Integer, index=True)
    geom = Column(Geometry(geometry_type="POINT", srid=4326))
    is_geocoded = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )
