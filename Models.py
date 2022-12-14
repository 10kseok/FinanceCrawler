from peewee import *

mysql_db = MySQLDatabase(
    host='203.255.57.227',
    user='amugae',
    password='AMUGAE!!!amg1234',
    database='AMUGAE'
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
