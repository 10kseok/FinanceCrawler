# v1.3
from enum import Enum
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
from peewee import *


mysql_db = MySQLDatabase(
    host='203.255.57.227',
    user='amugae',
    password= 'AMUGAE!!!amg1234',
    database= 'AMUGAE'
)

class BaseModel(Model):
    class Meta:
        database = mysql_db

class Sector(BaseModel):
    sector_id = CharField(primary_key=True)
    sector_name = CharField()

class Stock(BaseModel):
    stock_code = CharField(primary_key=True)
    volume = IntegerField()
    marketsum = IntegerField()
    
class Company(BaseModel):
    stock_code = ForeignKeyField(Stock, on_delete="CASCADE")
    company_name = CharField()
    sector_id = ForeignKeyField(Sector, on_update="CASCADE")
    
class FinancialStatements(BaseModel):
    stock_code = ForeignKeyField(Stock, backref="FS3Years", on_delete="CASCADE")
    year = IntegerField()
    sales = IntegerField()
    operating_income = IntegerField()
    net_income = IntegerField()
    opm = DecimalField(decimal_places=2)
    npm = DecimalField(decimal_places=2)
    ROE = DecimalField(decimal_places=2)
    debt_ratio = DecimalField(decimal_places=2)
    quick_ratio = DecimalField(decimal_places=2)
    reserve_ratio = DecimalField(decimal_places=2)
    EPS = IntegerField()
    PER = DecimalField(decimal_places=2)
    BPS = IntegerField()
    PBR = DecimalField(decimal_places=2)
    dps = IntegerField()
    dividend_yield_ratio = DecimalField(decimal_places=2)
    divident_payout_ratio = DecimalField(decimal_places=2)
    
    class Meta:
        primary_key = CompositeKey('stock_code', 'year')

# Just for giving result hint.
class URL:
    pass
class HTML:
    pass
class StockCode:
    pass
#---------------------------------------

class Crawler:
    def __init__(self) -> None:
        self.__url = ""
        self.__html = None

    def parse(self, url) -> HTML:
        # header to certificate "Not bot"
        if self.__url == url: return self.__html
        html = bs(requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).text, 'html.parser')

        self.__url = url
        self.__html = html

        return self.__html 

class URLCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.__sector_to_url = {}
        self.__company_to_url = {}
    
    def get_sector_url(self) -> URL:
        url = "https://finance.naver.com/sise/sise_group.nhn?type=upjong"
        return url
    
    def get_sector_to_url(self) -> dict({Sector: URL}):
        return self.crawl_sector_to_urls()
    
    def get_sector_to_id(self) -> dict({Sector: id}):
        return self.make_sector_to_id()

    def get_company_url(self, stock_code) -> URL:
        url = f"https://finance.naver.com/item/main.naver?code={stock_code}"
        return url
    
    def get_company_to_url(self) -> dict({Company: URL}):
        return self.crawl_company_to_url()
    
    def crawl_sector_to_urls(self) -> list([URL]):
        # (업종마다 나눠진 회사들을 보기위해) 업종별 링크수집 {업종 : 업종Link}
        if len(self.__sector_to_url) != 0: return self.__sector_to_url

        sector_to_url = {}
        url = self.get_sector_url()
        html = super().parse(url)

        for url in html.find_all('a'):
            link = url['href']
            if self.is_sector_url(link):
                name = url.get_text()
                sector_to_url[name] = f"https://finance.naver.com{link}"

        # for caching
        self.__sector_to_url = sector_to_url

        return sector_to_url
    
    def crawl_company_to_url(self) -> dict({Company: URL}):
        # 각 회사별 (종목정보를 볼 수 있는)링크 수집 {회사명: 종목Link}
        if len(self.__company_to_url) != 0: return self.__company_to_url
        
        company_to_url = {}
        
        for sector_url in self.get_sector_to_url().values():
            html = super().parse(sector_url)

            for company_url in html.find_all('a'):
                link = company_url['href']
                if self.is_stock_url(link):
                    name = company_url.get_text()
                    company_to_url[name] = f"https://finance.naver.com{link}"
        
        # for caching
        self.__company_to_url = company_to_url   
        
        return company_to_url

    def make_sector_to_id(self):
        sector_to_id = {}
        sector_to_url = self.get_sector_to_url().items()

        for name, url in sector_to_url:
            sid = self.convert_url_to_id(url)
            sector_to_id[name] = sid

        return sector_to_id

    def convert_url_to_id(self, url):
        return url.split("=")[-1]

    def is_stock_url(self, url):
        return url.startswith('/item/main.naver?code=')

    def is_sector_url(self, url):
        return url.startswith('/sise/sise_group_detail.naver?type=upjong&no=')
    
class StockCrawler(Crawler):
    def __init__(self) -> None:
        super().__init__()

    def set_stock_code(self, stock_code):
        self.stock_code = stock_code
        self.url = f"https://finance.naver.com/item/main.naver?code={stock_code}" 

    def get_marketsum(self) -> int:
        return self.crawl_marketsum()

    def get_volume(self) -> int:
        return self.crawl_volume()
    
    def crawl_marketsum(self, stock_code) -> int:
        html = super().parse(self.url)
        # remove blank, linespace, tap, dot
        market_sum = int("".join(html.find(id="_market_sum").text.strip().split()).replace("조", "").replace(",", ""))
        return market_sum
    
    def crawl_volume(self, stock_code) -> int:
        html = super().parse(self.url)
        volume_tag = html.find_all("td")
        # remove blank, linespace, tap, dot
        volume = int(volume_tag[2].find(class_="blind").text.replace(",", ""))
        return volume
        
class CompanyCrawler(URLCrawler):
    def __init__(self):
        super().__init__()
        self.__sector_to_company = {}
        self.__company_to_stock_code = {}
        self.__financial_statements = {}   
    
    def get_sector_to_company(self) -> dict({Sector: Company}):
        return self.crawl_sector_to_company_all()
       
    def get_company_to_stock_code(self) -> dict({Company: StockCode}):
        return self.crawl_company_to_stock_code()

    def get_financial_statements(self, stock_code):
        return self.crawl_financial_statements_specific_company(stock_code)

    def crawl_company_in(self, sector) -> list([Company]):
        # 입력받은 업종에 포함되어 있는 회사들 수집
        company_list = []
        html = super().parse(self.__sector_to_url[sector])
        
        for url in html.find_all('a'):
            link = url['href']
            if link.startswith('/item/main.naver?code='):
                company_list.append(url.get_text())
        
        return company_list
    
    def crawl_company_to_stock_code(self) -> dict({Company: StockCode}):
        # 종목코드 수집
        if len(self.__company_to_stock_code) != 0: return self.__company_to_stock_code
        
        company_to_stock_code = {}
        company_to_url = super().get_company_to_url().items()
        
        for company, company_url in company_to_url:   
            stock_code = company_url.split('=')[-1]
            company_to_stock_code[company] = stock_code
            
        self.__company_to_stock_code = company_to_stock_code

        return company_to_stock_code
                    
    def crawl_sector_to_company_all(self) -> dict({Sector: [Company]}):
        # 각 업종별 회사들 수집
        if len(self.__sector_to_company) != 0: return self.__sector_to_company
        
        sector_to_company = {}
        sectors = super().crawl_sector_to_urls().keys()
        
        for sector in sectors:
            companies = self.crawl_company_in(sector)
            sector_to_company[sector] = companies
        
        # for caching
        self.__sector_to_company = sector_to_company
        
        return sector_to_company
        
    def crawl_financial_statements_specific_company(self, stock_code) -> FinancialStatements:
        table = pd.read_html(f'https://finance.naver.com/item/main.naver?code={stock_code}', encoding='euc-kr')
        # 기업실적분석 테이블만 가져옴
        try:
            financial_reports_df = table[3]
        
            recent_year_1st = financial_reports_df.columns[1]
            recent_year_2nd = financial_reports_df.columns[2]
            recent_year_3rd = financial_reports_df.columns[3]
            
        except:
            # 회사외의 종목들 (ETF, ETN, 원자재 등)
            print("Not Company (crawl_financial_report)")
            
        else:
            # 최근 3년치 연간실적 테이블값만 가져옴
            financial_reports_df_3years = [financial_reports_df[recent_year_1st],
                                          financial_reports_df[recent_year_2nd],
                                          financial_reports_df[recent_year_3rd]]

            return financial_reports_df_3years
    
    def crawl_financial_statements_all_company(self) -> dict({StockCode: FinancialStatements}):
        if len(self.__financial_statements) != 0: return self.__financial_statements
        
        financial_statements = {}
        stock_codes =  self.get_company_to_stock_code().values()
        
        for stock_code in stock_codes:
            financial_statements = self.crawl_financial_statements_specific_company(stock_code)
            financial_statements[stock_code] = financial_statements
        
        self.__financial_statements = financial_statements
        
        return financial_statements

    def find_sector(self, company_name):
        sector_to_company = self.get_sector_to_company().items()
        for sector, companies in sector_to_company:
            if company_name in companies:
                return sector


if __name__ == "__main__":
    pass
