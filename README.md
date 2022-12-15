# FinanceScrapper

## 목표
#### 국내 주식정보를 긁어와 기업실적을 바탕으로 _**업종별 투자할 기업 선정**_
    
## 기능
    1. 네이버증권사이트에서 업종들을 긁어온다.
    2. 각 회사별 종목링크를 긁어온다.
    3. 종목별 '기업실적분석'을 긁어와 모든 재무정보를 저장한다.
    4. 긁어온 데이터를 원격DB에 저장시킨다.

## 규칙
    1. 리팩토링은 테스트코드 작성 후에 진행한다.
    2. getter, setter를 제외한 함수(메소드)에는 기능을 설명하는 주석 달기.