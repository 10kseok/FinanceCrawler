from bs4 import BeautifulSoup as bs
import requests


class Crawler:
    def __init__(self) -> None:
        self.__cache = {}

    def parse(self, url) -> bs:
        '''
        url 파싱 및 결과값 caching
        :param url: 파싱하려는 string url
        :return: BeautifulSoup 객체
        '''
        # header to certificate "Not bot"
        if self.__cache.get(url):
            return self.__cache[url]

        html = bs(requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).text, 'html.parser')
        self.__cache[url] = html

        return self.__cache[url]


class URLCrawler(Crawler):
    __SECTOR_BASEURL = "https://finance.naver.com/sise/sise_group.nhn?type=upjong"
    __COMPANY_URL = "https://finance.naver.com/item/main.naver?code="
    __MAIN_URL = "https://finance.naver.com"

    def __init__(self):
        super().__init__()
        self.__sector_to_url = {}  # 업종별 링크
        self.__company_to_url = {}  # 기업(종목)별 링크

    def get_sector_baseurl(self) -> str:
        return self.__SECTOR_BASEURL

    def get_sector_to_url(self) -> dict({str: str}):
        return self.crawl_sector_to_urls()

    def get_sector_to_id(self) -> dict({str: id}):
        return self.make_sector_to_id()

    def get_company_url(self, stock_code) -> str:
        return f"{self.__COMPANY_URL}{stock_code}"

    def get_company_to_url(self) -> dict({str: str}):
        return self.crawl_company_to_url()

    def crawl_sector_to_urls(self) -> list[str]:
        '''
         :return: {업종 : 업종Link}
         업종마다 나눠진 기업들을 보기위해 업종별 링크수집
        '''
        if len(self.__sector_to_url) != 0:
            return self.__sector_to_url

        sector_to_url = {}
        url = self.get_sector_baseurl()
        html = self.parse(url)

        for url in html.find_all('a'):
            link = url['href']
            if self.is_sector_url(link):
                name = url.get_text()
                sector_to_url[name] = f"{self.__MAIN_URL}{link}"

        # for caching
        self.__sector_to_url = sector_to_url

        return sector_to_url

    def crawl_company_to_url(self) -> dict({str: str}):
        '''
        :return: {회사명: 종목Link}
        업종명을 query에 들어갈 업종id과 맵핑
        '''
        if len(self.__company_to_url) != 0:
            return self.__company_to_url

        company_to_url = {}

        for sector_url in self.get_sector_to_url().values():
            html = self.parse(sector_url)

            for company_url in html.find_all('a'):
                link = company_url['href']
                if self.is_stock_url(link):
                    name = company_url.get_text()
                    company_to_url[name] = f"https://finance.naver.com{link}"

        # for caching
        self.__company_to_url = company_to_url

        return company_to_url

    def make_sector_to_id(self) -> dict[str, str]:
        '''
        :return: { sector : sid } (ex_ {'출판': '314', '가정용품': '297', ...})
        업종명을 query에 들어갈 업종id과 맵핑
        '''
        sector_to_id = {}
        sector_to_url = self.get_sector_to_url().items()

        for name, url in sector_to_url:
            sid = self.convert_url_to_id(url)
            sector_to_id[name] = sid

        return sector_to_id

    def convert_url_to_id(self, url) -> str:
        '''
        :param url: 특정 업종 url
        :return: 업종id(query parameter)
        '''
        return url.split("=")[-1]

    def is_stock_url(self, url) -> str:
        '''
        :return: 기업정보사이트가 맞는지
        '''
        return url.startswith('/item/main.naver?code=')

    def is_sector_url(self, url):
        '''
        :return: 업종들이 나열된 사이트가 맞는지
        '''
        return url.startswith('/sise/sise_group_detail.naver?type=upjong&no=')
