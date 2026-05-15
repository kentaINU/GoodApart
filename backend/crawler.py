import os
import random
import time

import requests

# 設定
BASE_URL = "https://www.good-monthly.com/fukuoka/search/list_add.html"

# 検索条件（博多区・中央区など）
PARAMS = {
    "jc[]": ["40133", "40132"],
    "pagesize": "30",
    "page": 1,
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
SAVE_DIR = "html_data"


def fetch_pages(max_pages=5):
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    for p in range(1, max_pages + 1):
        print(f"--- {p}ページ目を取得中 ---")
        PARAMS["page"] = p

        try:
            response = requests.get(BASE_URL, params=PARAMS, headers=HEADERS)
            response.raise_for_status()

            # ファイル名を page_1.html のようにして保存
            file_path = os.path.join(SAVE_DIR, f"page_{p}.html")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)

            print(f"保存完了: {file_path}")

            # 相手サーバ負荷軽減
            time.sleep(5 + random.uniform(0, 3))

        except Exception as e:
            print(f"取得失敗: {e}")
            break


if __name__ == "__main__":
    fetch_pages(max_pages=12)
