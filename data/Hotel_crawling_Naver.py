from bs4 import BeautifulSoup
from selenium import webdriver
import time
import csv
import re
from datetime import datetime, timedelta

# 'YYYY-MM-DD'
def is_valid_date(date_str):
    try:
        time.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

date1 = ""
date2 = ""

while not is_valid_date(date1):
    date1 = input("체크인 날짜를 입력하세요 (YYYY-MM-DD) : ")

while not is_valid_date(date2):
    date2 = input("체크아웃 날짜를 입력하세요 (YYYY-MM-DD) : ")

date_obj = datetime.strptime(date1, '%Y-%m-%d')
week = date_obj.strftime('%A')

start_date = date1
limit_date = input("크롤링을 종료할 날짜를 입력하세요 (YYYY-MM-DD) : ")

limit_day_obj = datetime.strptime(limit_date, '%Y-%m-%d')

lastPage = int(input('몇 페이지를 크롤링 할까요? : '))

driver = webdriver.Chrome()


place = "Louvre"

# 구역별로 place 변수에 넣어서 사용
# 샤를드 골 공항 : Paris_Charles_de_Gaulle_Airport
# 1구역 : Louvre
# 2구역 : Bourse
# 3구역 : Temple_Paris_Department_France
# 4구역 : Hotel_de_Ville
# 5구역 : 5th_Arrondissement_Pantheon
# 6구역 : Luxembourg_lle_de_France_France
# 7구역 : 7th_Arrondissement_of_Paris
# 8구역 : Elysee
# 9구역 : Opera_Paris_Department_France

data_list = []  # 데이터를 저장할 리스트 생성

while date_obj <= limit_day_obj:
    week = date_obj.strftime('%A')  
    for pageNum in range(lastPage):
        search_url = f'https://hotels.naver.com/list?placeFileName=place%3A{place}&adultCnt=1&checkIn={date1}&checkOut={date2}&includeTax=false&sortField=popularityKR&sortDirection=descending&pageIndex={pageNum}'

        driver.get(search_url)

        time.sleep(3)

        for i in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

        html = driver.page_source

        soup = BeautifulSoup(html, "html.parser")

        # 호텔 정보 가져오기
        items = soup.select(".SearchList_HotelItem__aj2GM")

        for rank_num, item in enumerate(items, 1):
            # 포스트 정렬 순서 표시
            print(f"<<{rank_num}>>")

            # 호텔이름 표시
            hotel_name_element = item.select_one(".Detail_title__40_dz")
            hotel_name = hotel_name_element.text if hotel_name_element else None
            print(f"{hotel_name}")

            # 지역이름 표시
            location_element = item.select_one(".Detail_location__u3_N6")
            location = location_element.text if location_element else None
            print(f"{location}")

            # 평점 표시
            rating_element = item.select_one(".Detail_score__UxnqZ")
            rating = rating_element.text if rating_element else None
            print(f"{rating}")

            # 성급 표시
            star_rating_element = item.select_one(".Detail_grade__y5BmJ")
            star_rating = star_rating_element.text if star_rating_element else None
            print(f"{star_rating}")

            # 호텔특징 표시
            feature_element = item.select_one(".Detail_feature__HC8K_")
            feature = feature_element.text if feature_element else None
            print(f"{feature}")

            # 가격 표시
            price_element = item.select_one(".Price_show_price__iQpms")
            price_text = price_element.text.strip() if price_element else None

            # Extract the numeric part of the price using regular expressions
            price_number = re.findall(r'\d{1,3}(?:,\d{3})*', price_text)[0] if price_text else None
            print(f"가격: {price_number}")

            # 추가가격 표시 (없을 경우 'None'으로 표기)
            price_extra = item.select_one(".RateList_Item__iFuN6 .RateList_price__x2QuB")
            extra = price_extra.text if price_extra else "None"
            print(f"{extra}")

            # 데이터를 리스트에 추가합니다.
            data_list.append([week, date1, date2, place, hotel_name, location, rating, star_rating, feature, price_number, extra])

            # 빈 줄 출력
            print()

        if date_obj == limit_day_obj:
            break

    date_obj += timedelta(days=1)
    date1 = date_obj.strftime('%Y-%m-%d')
    date2 = (date_obj + timedelta(days=1)).strftime('%Y-%m-%d')

# CSV 파일로 데이터 저장
with open(f"hotel_{place}_{start_date}_{limit_date}.csv", 'w', encoding='CP949', newline='') as f:
    fieldnames = ['요일', '체크인date', '체크아웃date', '구역', '호텔이름', '지역이름', '평점', '성급', '특징', '가격', '기타 가격']
    csvWriter = csv.writer(f)

    # 첫 번째 줄에 column명 입력
    csvWriter.writerow(fieldnames)

    # 데이터를 CSV 파일에 저장
    for data in data_list:
        csvWriter.writerow(data)

# 브라우저 닫기
driver.quit()

print('모든 스크래핑이 완료되었습니다.')
