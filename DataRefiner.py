from FinanceCrawler import *

class DataRefiner:
    def __init__(self) -> None:
        self.stock_crawler = StockCrawler()
        self.company_crawler = CompanyCrawler()
        self.url_crawler = URLCrawler()

    def get_Sectors(self) -> list([Sector]):
        sectors = []
        sector_to_url = self.url_crawler.get_sector_to_url().items()

        for sector_name, sector_url in sector_to_url:
            sid = sector_url.split("=")[-1]
            sector = Sector(sector_id= sid, sector_name= sector_name)
            sectors.append(sector)

        return sectors 

    def get_Stocks(self) -> list([Stock]):
        stocks = []
        stock_codes = self.company_crawler.get_company_to_stock_code().values()

        for stock_code in stock_codes:
            self.stock_crawler.set_stock_code(stock_code)
            volume = self.stock_crawler.get_volume()
            marketsum = self.stock_crawler.get_marketsum()
            stock = Stock(stock_code= stock_code, volume= volume, marketsum= marketsum)
            stocks.append(stock)

        return stocks

    def get_Companies(self) -> list([Company]):
        companies = []
        company_to_stock_code = self.company_crawler.get_company_to_stock_code().items()
        sector_to_id = self.url_crawler.get_sector_to_id()

        for company_name, stock_code in company_to_stock_code:
            sector = self.company_crawler.find_sector_of(company_name)
            if self.is_valid(sector):
                company = Company(stock_code= stock_code, company_name= company_name, sector_id= sector_to_id[sector])
                companies.append(company)

        return companies

    def get_Financial_statements(self) -> FinancialStatements:
        stock_codes = self.company_crawler.get_company_to_stock_code().values()
        FSs = []

        for stock_code in stock_codes:
            fs = self.company_crawler.get_financial_statements(stock_code)
            if self.is_valid(fs):
                for f in fs:
                    try:
                        # 최근 3년치가 있어야함 
                        year = int(f.name[1][:4])
                    except:
                        # If Not Company ETF, ETN etc .. 
                        print("You should get away. get ")
                    else:
                        # Nan값처리(ex_ 배당 안하는 기업들)
                        for i in range(len(f)):
                            if pd.isna(f[i]):
                                f[i] = 0
                                
                        financial_statements = FinancialStatements(stock_code= stock_code,
                                                                year= year,
                                                                sales= f[0],
                                                                operating_income= f[1],
                                                                net_income= f[2],
                                                                opm= f[3],
                                                                npm= f[4],
                                                                ROE= f[5],
                                                                debt_ratio= f[6],
                                                                quick_ratio= f[7],
                                                                reserve_ratio= f[8],
                                                                EPS= f[9],
                                                                PER= f[10],
                                                                BPS= f[11],
                                                                PBR= f[12],
                                                                dps= f[13],
                                                                dividend_yield_ratio= f[14],
                                                                divident_payout_ratio= f[15]
                                                                )

                        FSs.append(financial_statements)
        return FSs

    def is_valid(self, sector):
        return sector == True

if __name__ == "__main__":
    dr = DataRefiner()
    sectors = dr.get_Sectors()
    stocks = dr.get_Stocks()
    companies = dr.get_Companies()
    financial_statements = dr.get_Financial_statements()

    # MARK: DB에 데이터 저장과정
    # mysql_db.connect()
    # # Create Tables
    # mysql_db.create_tables([Stock, Sector, Company, FinancialStatements])
    #
    # # For the first time insert, force_insert=True
    # for sector in sectors:
    #     sector.save(force_insert=True)
    #
    # for stock in stocks:
    #     stock.save(force_insert=True)
    #
    # for company in companies:
    #     company.save(force_insert=True)
    #
    # for fs in financial_statements:
    #     fs.save(force_insert=True)
    #
    # mysql_db.close()

