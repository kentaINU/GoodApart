# jobs/crawler/base_crawler.py
import os
import random
import time
from datetime import datetime

import requests


class BaseCrawler:
    """すべてのクローラーの基盤となる共通クラス"""

    def __init__(self, site_name, base_url, default_params, max_pages=5):
        self.site_name = site_name  # 保存先フォルダ名 (例: "good_monthly")
        self.base_url = base_url
        self.params = default_params
        self.max_pages = max_pages
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

    def _get_save_dir(self):
        """実行日の日付（JST想定）に合わせた保存先ディレクトリパスを生成"""
        # html_data はプロジェクトルートからの相対パス
        current_month = datetime.now().strftime("%Y-%m")
        current_date = datetime.now().strftime("%Y-%m-%d")
        return os.path.join("html_data", self.site_name, current_month, current_date)

    def set_page_param(self, page_num):
        """💡 サイトごとにページ番号のパラメータ名（page, p, num等）が異なる場合、子クラスでオーバーライドする"""
        self.params["page"] = page_num

    def fetch_all(self):
        """全ページを一括取得して保存するメイン処理"""
        save_dir = self._get_save_dir()
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        print(f"==========================================")
        print(
            f"🚀 【{self.site_name}】のクロールを開始します（最大 {self.max_pages} ページ）"
        )
        print(f"==========================================")

        for p in range(1, self.max_pages + 1):
            print(f"--- {p}ページ目を取得中 ---")
            self.set_page_param(p)

            try:
                response = requests.get(
                    self.base_url, params=self.params, headers=self.headers
                )
                response.raise_for_status()

                file_path = os.path.join(save_dir, f"page_{p}.html")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(response.text)

                print(f"✅ 保存完了: {file_path}")

                # 相手サーバー負荷軽減（5〜8秒のランダムスリープ）
                time.sleep(5 + random.uniform(0, 3))

            except Exception as e:
                print(f"❌ {p}ページ目の取得に失敗しました: {e}")
                break
