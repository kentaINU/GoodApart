import glob
import logging
import os
import re
import sys
from datetime import datetime

from bs4 import BeautifulSoup
from sqlalchemy.dialects.postgresql import insert

# プロジェクトのルートディレクトリ（/workspace/backend）を検索パスに確実に追加
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from database.connection import SessionLocal
from database.models.property import Property

# ログの設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

SITE_NAME = "good_monthly"
SITE_DOMAIN = "https://www.good-monthly.com"


def clean_price(price_str: str) -> int:
    """「102,000円/月」のような文字列から数値（102000）だけを抽出する"""
    if not price_str:
        return 0
    nums = re.sub(r"[^\d]", "", price_str)
    return int(nums) if nums else 0


def parse_html_file(file_path: str) -> list[dict]:
    """1つのHTMLファイルを解析して、物件データの辞書リストを返す"""
    properties = []

    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    sections = soup.find_all("section", class_="default")
    for section in sections:
        h3_tag = section.find("h3")
        a_tag = h3_tag.find("a") if h3_tag else None
        if not a_tag or not a_tag.get("href"):
            continue

        name = a_tag.get_text(strip=True)
        source_url = f"{SITE_DOMAIN}{a_tag['href']}"

        # 住所の取得
        address_dt = section.find("dt", string="所在地")
        address = (
            address_dt.find_next("dd").get_text(strip=True)
            if address_dt
            else "住所不明"
        )

        # 賃料の取得
        price_text = "料金情報なし"
        price_int = 0

        price_table = section.find("div", class_="priceArea")
        if price_table:
            all_ths = price_table.find_all("th")
            target_th = None

            # 1. まず優先度の高いキーワード（ショート・1ヶ月以上）を探す
            for th in all_ths:
                th_text = th.get_text()
                if "ショート" in th_text or "1ヶ月以上" in th_text:
                    target_th = th
                    break

            # 2. 見つからなければ「料金」というキーワードを探す
            if not target_th:
                for th in all_ths:
                    if "料金" in th.get_text():
                        target_th = th
                        break

            # 💡 3. それでもダメなら、テーブル内のヘッダー行(最上段)を除いた最初の td を持ってくる（最終防衛ライン）
            price_td = None
            if target_th:
                price_td = target_th.find_next("td")
            else:
                # 見出し行以外の tr から最初の td を取得
                all_trs = price_table.find_all("tr")
                for tr in all_trs:
                    tds = tr.find_all("td")
                    if tds:  # tdが存在する＝データ行
                        price_td = tds[0]
                        break

            if price_td:
                # stripped_strings でタグに挟まれたテキストを綺麗に分解して抽出
                lines = [s for s in price_td.stripped_strings if "月" in s]
                if lines:
                    price_text = lines[0]
                else:
                    price_text = price_td.get_text(strip=True)

                price_int = clean_price(price_text)

        properties.append(
            {
                "site_name": SITE_NAME,
                "source_url": source_url,
                "name": name,
                "address": address,
                "price_text": price_text,
                "price_int": price_int,
                "is_geocoded": False,
            }
        )

    return properties


def parse_and_save_to_db(target_date: str = None):
    """指定された日付のHTMLデータをパースしてDBに一括Upsertする"""
    if target_date is None:
        target_date = datetime.now().strftime("%Y-%m-%d")

    target_month = target_date[:7]
    html_dir = os.path.join("html_data", SITE_NAME, target_month, target_date)
    html_files = glob.glob(os.path.join(html_dir, "*.html"))

    if not html_files:
        logger.warning(f"対象ディレクトリにHTMLファイルがありません: {html_dir}")
        return

    # 全ファイルから登録対象のデータをメモリ上に集約
    all_properties = []
    for file_path in sorted(html_files):
        logger.info(f"📖 解析中: {file_path}")
        try:
            file_data = parse_html_file(file_path)
            all_properties.extend(file_data)
        except Exception as e:
            logger.error(f"❌ ファイルパース失敗 ({file_path}): {e}")

    if not all_properties:
        logger.info("登録対象の物件データがありませんでした。")
        return

    # Python側で source_url の一意性を保証
    unique_properties = {}
    for prop in all_properties:
        unique_properties[prop["source_url"]] = prop

    final_properties = list(unique_properties.values())

    logger.info(
        f"🧹 重複排除完了: 総数 {len(all_properties)} 件 -> 固有数 {len(final_properties)} 件"
    )

    # データの登録・更新処理（バルクUpsert）
    db = SessionLocal()
    try:
        stmt = insert(Property).values(final_properties)

        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=[Property.source_url],
            set_={
                "name": stmt.excluded.name,
                "address": stmt.excluded.address,
                "price_text": stmt.excluded.price_text,
                "price_int": stmt.excluded.price_int,
                "is_geocoded": False,
            },
        )

        db.execute(upsert_stmt)
        db.commit()
        logger.info(
            f"🎉 【{SITE_NAME}】{target_date}分 の全 {len(final_properties)} 件をDBに一括Upsertしました。"
        )

    except Exception as e:
        db.rollback()
        logger.error(f"❌ DB更新中にエラーが発生しました: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parse_and_save_to_db()
