import glob
import os

from bs4 import BeautifulSoup
from models import Property, SessionLocal, engine
from sqlalchemy.orm import Session

HTML_DIR = "html_data"


def parse_and_save_to_db():
    html_files = glob.glob(os.path.join(HTML_DIR, "*.html"))
    db: Session = SessionLocal()

    try:
        total_added = 0
        for file_path in sorted(html_files):
            with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")

            sections = soup.find_all("section", class_="default")
            for section in sections:
                # 解析処理
                name = (
                    section.find("h3").get_text(strip=True)
                    if section.find("h3")
                    else "名称不明"
                )
                address_dt = section.find("dt", string="所在地")
                address = (
                    address_dt.find_next("dd").get_text(strip=True)
                    if address_dt
                    else "住所不明"
                )

                # DBへ追加（チェックなし！）
                new_prop = Property(name=name, address=address, is_geocoded=False)
                db.add(new_prop)
                total_added += 1

        db.commit()
        print(f" 全 {total_added} 件をDBに保存しました。")
    finally:
        db.close()


if __name__ == "__main__":
    parse_and_save_to_db()
