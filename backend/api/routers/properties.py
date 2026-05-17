from api.deps import get_db
from database.models.property import Property
from fastapi import APIRouter, Depends
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/properties")
def get_properties(db: Session = Depends(get_db)):
    properties = db.query(Property).all()

    results = []
    for p in properties:
        # GeoAlchemy2のgeomから緯度経度を取り出す
        point = to_shape(p.geom) if p.geom else None

        results.append(
            {
                "id": p.id,
                "name": p.name,
                "address": p.address,
                "price": p.price_int,
                "price_text": p.price_text,
                "site_name": p.site_name,
                "source_url": p.source_url,
                "lat": point.y if point else None,
                "lng": point.x if point else None,
            }
        )

    return results
