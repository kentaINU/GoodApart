# jobs/crawler/good_monthly.py
import os
import sys

# プロジェクトのルートディレクトリを検索パスに追加（モジュール読み込み用）
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from jobs.crawler.base_crawler import BaseCrawler


class GoodMonthlyCrawler(BaseCrawler):
    """グッドマンスリー専用のクローラー"""

    def __init__(self):
        # グッドマンスリー特有の設定
        site_name = "good_monthly"
        base_url = "https://www.good-monthly.com/fukuoka/search/list_add.html"
        default_params = {
            "jc[]": ["40133", "40132"],  # 中央区・博多区
            "pagesize": "30",
        }
        super().__init__(
            site_name=site_name,
            base_url=base_url,
            default_params=default_params,
            max_pages=12,
        )


if __name__ == "__main__":
    crawler = GoodMonthlyCrawler()
    crawler.fetch_all()
