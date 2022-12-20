# v1.3
import pandas as pd
from Models import *
from utility import *
from URLCrawler import *
from typing import *

class StockCrawler(Crawler):
    '''
    각 기업정보사이트에서 차트 옆에 '투자정보'란에 있는 종목 정보들(시가총액, 주식수...etc)을 가져옴.
    '''
    def __init__(self) -> None:
        super().__init__()
        self.__stock_code_to_url = {}

    def set_stock_code(self, stock_code: str):
        self.__stock_code_to_url[stock_code] = f"https://finance.naver.com/item/main.naver?code={stock_code}"

    def get_url_of(self, stock_code: str) -> str:
        if self.__stock_code_to_url.get(stock_code):
            return self.__stock_code_to_url[stock_code]

        self.set_stock_code(stock_code)

        return self.get_url_of(stock_code)

    def get_marketsum(self) -> int:
        return self.scrap_marketsum()

    def get_volume(self) -> int:
        return self.scrap_volume()
    
    def scrap_marketsum(self, stock_code: str) -> int:
        '''
        :param stock_code: 종목코드
        :return: 입력받은 종목의 시가총액
        '''
        html = super().parse(self.get_url_of(stock_code))
        # remove blank, linespace, tap, dot
        market_sum = int(only_num("".join(html.find(id="_market_sum").text.strip().split())))
        return market_sum
    
    def scrap_volume(self, stock_code: str) -> int:
        '''
        :param stock_code: 종목코드
        :return: 입력받은 종목의 거래량
        '''
        html = super().parse(self.get_url_of(stock_code))
        volume_tag = html.find_all("td")
        # remove blank, linespace, tap, dot
        volume = int(only_num(volume_tag[2].find(class_="blind").text))
        return volume
        
class CompanyCrawler(URLCrawler):
    __STOCK_DETAIL_URL = "https://finance.naver.com/item/main.naver?code="

    def __init__(self):
        super().__init__()
        self.__sector_to_company = {}
        self.__company_to_stock_code = {}
        self.__financial_statements = {}   

    def get_sector_to_company(self) -> Dict[str, str]:
        return self.crawl_sector_to_company_all()
       
    def get_company_to_stock_code(self) -> Dict[str, str]:
        return self.crawl_company_to_stock_code()

    def get_financial_statements(self, stock_code) -> List[FinancialStatements]:
        return self.scrap_financial_statements_about(stock_code)

    def crawl_company_in(self, sector) -> List[Company]:
        '''
        :param sector: 업종명
        :return: 입력받은 업종에 해당하는 기업들
        '''
        company_list = []
        html = super().parse(self.get_sector_to_url()[sector])

        for url in html.find_all('a'):
            link = url['href']
            if link.startswith('/item/main.naver?code='):
                company_list.append(url.get_text())
        
        return company_list
    
    def crawl_company_to_stock_code(self) -> Dict[str, str]:
        '''
        :return: { 기업명: 종목코드 } ex) {'케이엠제약': '225430', '프로스테믹스': '203690', ...}

        업종별로 나눠진 기업들에서 얻어온 url로 종목코드를 추출해낸다.
        '''
        if len(self.__company_to_stock_code) != 0:
            return self.__company_to_stock_code
        
        company_to_stock_code = {}
        company_to_url = super().get_company_to_url().items()
        
        for company, company_url in company_to_url:   
            stock_code = company_url.split('=')[-1]
            company_to_stock_code[company] = stock_code
            
        self.__company_to_stock_code = company_to_stock_code

        return company_to_stock_code
                    
    def crawl_sector_to_company_all(self) -> Dict[str, List[str]]:
        # TODO: crawl_sector_to_company 메서드를 만들어 단일 섹터:기업들을 반환, 이것을 여러번 호출하여 all 메서드를 만드는 방식으로 변환필요.
        '''
        :return: { 업종 : 업종에 속하는 기업들 }

        ex) {'가정용품': ['케이엠제약', '모자리자', ...], '출판': ['디앤씨미디어', '아시아경제',...], ...}
        '''
        if len(self.__sector_to_company) != 0:
            return self.__sector_to_company
        
        sector_to_company = {}
        sectors = super().crawl_sector_to_urls().keys()
        
        for sector in sectors:
            companies = self.crawl_company_in(sector)
            sector_to_company[sector] = companies
        
        # for caching
        self.__sector_to_company = sector_to_company
        
        return sector_to_company
        
    def scrap_financial_statements_about(self, stock_code: str) -> List[FinancialStatements]:
        '''
        :param stock_code: 종목코드
        :return: 주요재무재표 3년치(2020~2022) 내용

        특정종목 상세정보가 나타나는 사이트에서 '기업분석실적'란에서 주요재무정보를 가져온다.
        '''
        table = pd.read_html(f'{self.__STOCK_DETAIL_URL}{stock_code}', encoding='euc-kr')
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
    
    def scrap_financial_statements_all_company(self) -> Dict[str, FinancialStatements]:
        '''
        :return: 모든 기업의 재무재표 정보

        ex) {'종목코드1' : [2020년 재무재표, 2021년 재무재표, 2022년 재무재표], '종목코드2' : [2020년 재무재표, 2021년 재무재표, 2022년 재무재표], ... }

        재무재표가 있는 모든 기업들의 주요재무정보를 가져온다.
        '''
        if len(self.__financial_statements) != 0:
            return self.__financial_statements
        
        financial_statements = {}
        stock_codes = self.get_company_to_stock_code().values()
        
        for stock_code in stock_codes:
            financial_statements = self.scrap_financial_statements_about(stock_code)
            financial_statements[stock_code] = financial_statements
        
        self.__financial_statements = financial_statements
        
        return financial_statements

    def find_sector_of(self, company: str) -> str:
        sector_to_company = self.get_sector_to_company().items()
        for sector, companies in sector_to_company:
            if company in companies:
                return sector


if __name__ == "__main__":
    # cc = CompanyCrawler()
    # print(cc.crawl_sector_to_company_all())

    pass
