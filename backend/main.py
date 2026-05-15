from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from geoalchemy2.shape import to_shape
from models import Property, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

# 起動コマンド memo
# python -m uvicorn main:app --host 0.0.0.0 --reload

# フロントエンドからアクセスを許可するための設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開発時はすべて許可
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/properties")
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
                "lat": point.y if point else None,
                "lng": point.x if point else None,
            }
        )

    return results
