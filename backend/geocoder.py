import time

import requests
from models import Property, SessionLocal
from sqlalchemy import text
from sqlalchemy.orm import Session


def get_lat_lng(address):
    """国土地理院のAPIを使って住所から緯度経度を取得"""
    try:
        # 住所をURLエンコードしてリクエスト
        url = f"https://msearch.gsi.go.jp/address-search/AddressSearch?q={address}"
        response = requests.get(url, timeout=5)
        res_json = response.json()

        if res_json:
            # 座標は [経度, 緯度] 
            lon, lat = res_json[0]["geometry"]["coordinates"]
            return lat, lon
    except Exception as e:
        print(f"ジオコーディングエラー ({address}): {e}")
    return None, None


def main():
    db: Session = SessionLocal()
    # 未処理の物件を取得
    targets = db.query(Property).filter(Property.is_geocoded == False).all()

    print(f"ジオコーディング開始（対象: {len(targets)} 件）")

    for prop in targets:
        # 同じ住所で既に座標を持っているデータがDB内にないか確認
        existing = (
            db.query(Property)
            .filter(Propert止対策）y.address == prop.address, Property.is_geocoded == True)
            .first()
        )

        if existing:
            prop.geom = existing.geom
            prop.is_geocoded = True
            print(f"再利用: {prop.address}")
        else:
            lat, lon = get_lat_lng(prop.address)
            if lat and lon:
                prop.geom = f"POINT({lon} {lat})"
                prop.is_geocoded = True
                print(f"取得成功: {prop.address} -> ({lat}, {lon})")

                # サーバーに負荷をかけないようにsleep
                time.sleep(2)
            else:
                print(f"❌ 取得失敗: {prop.address}")

        # 10件ごとにコミット
        if len(db.dirty) >= 10:
            db.commit()

    db.commit()
    db.close()
    print("すべての処理が完了しました。")


if __name__ == "__main__":
    main()
