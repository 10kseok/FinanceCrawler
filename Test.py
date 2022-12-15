import unittest
from FinanceCrawler import *

class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.crawler = Crawler()
        self.stock_crawler = StockCrawler()

    def test_parse특정URL(self):
        test_url = "https://docs.python.org/ko/3/library/unittest.html"
        test_html = bs(requests.get(test_url, headers={'User-agent': 'Mozilla/5.0'}).text, 'html.parser')
        self.assertEqual(self.crawler.parse(test_url), test_html)  # add assertion here

    def test_parse네이버증권(self):
        test_url = "https://finance.naver.com/"
        test_html = bs(requests.get(test_url, headers={'User-agent': 'Mozilla/5.0'}).text, 'html.parser')
        self.assertEqual(self.crawler.parse(test_url), test_html)  # add assertion here

    def test_parse네이버증권_업종별시세(self):
        test_url = "https://finance.naver.com/sise/sise_group.naver?type=upjong"
        test_html = bs(requests.get(test_url, headers={'User-agent': 'Mozilla/5.0'}).text, 'html.parser')
        self.assertEqual(self.crawler.parse(test_url), test_html)  # add assertion here

    def test_scrap_marketsum(self):
        # 장 중에 테스트하면 계속 변동되기에 장마감시간 이후에 테스트
        self.assertEqual(self.stock_crawler.scrap_marketsum("226360"), 679)

    def test_scrap_volume(self):
        # 장 중에 테스트하면 계속 변동되기에 장마감시간 이후에 테스트
        self.assertEqual(self.stock_crawler.scrap_volume("226360"), 24395515)



if __name__ == '__main__':
    unittest.main()
