import os
import sys
import time

import requests
from sqlalchemy import text
from sqlalchemy.orm import Session

# プロジェクトのルートディレクトリ（/workspace/backend）を検索パスに確実に追加
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from database.connection import SessionLocal
from database.models.property import Property


def get_lat_lng(address: str):
    """国土地理院のAPIを使って住所から緯度経度を取得"""
    if not address or address == "住所不明":
        return None, None

    try:
        # 住所をURLエンコードしてリクエスト
        url = f"https://msearch.gsi.go.jp/address-search/AddressSearch?q={address}"
        response = requests.get(url, timeout=5)
        res_json = response.json()

        if res_json and len(res_json) > 0:
            # 座標は [経度, 緯度]
            geometry = res_json[0].get("geometry", {})
            coordinates = geometry.get("coordinates", [])
            if len(coordinates) == 2:
                lon, lat = coordinates
                return lat, lon
    except Exception as e:
        print(f"❌ ジオコーディングエラー ({address}): {e}")
    return None, None


def main():
    db: Session = SessionLocal()

    # 未処理の物件を取得
    targets = db.query(Property).filter(Property.is_geocoded == False).all()

    print(f"🚀 ジオコーディング開始（対象: {len(targets)} 件）")

    processed_count = 0

    for prop in targets:
        # 💡 タイポ修正：同じ住所で既に座標を持っているデータがDB内にないか確認
        existing = (
            db.query(Property)
            .filter(Property.address == prop.address, Property.is_geocoded == True)
            .first()
        )

        if existing and existing.geom is not None:
            prop.geom = existing.geom
            prop.is_geocoded = True
            print(f"♻️ 再利用: {prop.address}")
            processed_count += 1
        else:
            lat, lon = get_lat_lng(prop.address)
            if lat and lon:
                # 💡 PostGISのGeometry型（SRID 4326等）に安全に変換して代入
                # DB側の型定義に合わせて、文字列ではなく WKT (Well-Known Text) を関数でパース
                prop.geom = text(f"ST_GeomFromText('POINT({lon} {lat})', 4326)")
                prop.is_geocoded = True
                print(f"📍 取得成功: {prop.address} -> ({lat}, {lon})")
                processed_count += 1

                # サーバーに負荷をかけないようにsleep（国土地理院へのマナー）
                time.sleep(2)
            else:
                # 住所に問題がある、あるいはAPIで見つからない場合はスキップ（次回以降に繰り越し、またはフラグ調整）
                print(f"⚠️ 取得失敗（スキップ）: {prop.address}")

        # 💡 確実な件数ベースでの10件ごと一括コミット
        if processed_count > 0 and processed_count % 10 == 0:
            try:
                db.commit()
                print(f"💾 10件の中間コミット完了（累計: {processed_count} 件）")
            except Exception as e:
                db.rollback()
                print(f"❌ 中間コミット失敗によりロールバックしました: {e}")

    try:
        db.commit()
        print(f"🎉 すべての処理が完了しました。総処理件数: {processed_count} 件")
    except Exception as e:
        db.rollback()
        print(f"❌ 最終コミット失敗: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
