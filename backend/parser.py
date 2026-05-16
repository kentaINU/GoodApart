import glob
import json
import os

from bs4 import BeautifulSoup

HTML_DIR = "html_data"
OUTPUT_FILE = "properties.json"


def parse_all_html():
    html_files = glob.glob(os.path.join(HTML_DIR, "*.html"))
    if not html_files:
        print(
            "解析対象のHTMLファイルが見つかりません。先に crawler.py を実行してください。"
        )
        return

    all_results = []

    for file_path in sorted(html_files):  # ページ順に並べる
        print(f"解析中: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        sections = soup.find_all("section", class_="default")
        for section in sections:
            name_tag = section.find("h3").find("a") if section.find("h3") else None
            name = name_tag.get_text(strip=True) if name_tag else "名称不明"

            address_dt = section.find("dt", string="所在地")
            address = (
                address_dt.find_next("dd").get_text(strip=True)
                if address_dt
                else "住所不明"
            )

            price_td = section.select_one(".priceArea td")
            price = price_td.get_text(strip=True) if price_td else "価格情報なし"

            all_results.append(
                {
                    "name": name,
                    "address": address,
                    "price": price,
                    "source_file": os.path.basename(file_path),
                }
            )

    # JSON保存
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=4)

    print(
        f"\n 解析完了！ 合計 {len(all_results)} 件のデータを {OUTPUT_FILE} に保存しました。"
    )


if __name__ == "__main__":
    parse_all_html()
