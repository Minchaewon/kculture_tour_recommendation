'''
kakao_crawler.py
- 카카오맵에서 음식점 정보를 크롤링하는 코드
- 검색어를 입력하면 해당 검색어에 대한 음식점 정보를 csv 파일로 저장
- 음식점 이름, 평점, 리뷰 개수, 링크, 주소를 저장
- 크롤링한 정보를 csv 파일로 저장
'''
import re
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import requests
import csv
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import googlemaps
import pandas as pd

# ✅ 자동 크롬드라이버 설치용 import
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ✅ 옵션 설정 및 드라이버 실행
options = webdriver.ChromeOptions()
options.add_argument('lang=ko_KR')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ✅ 그 아래 코드들은 그대로 유지
headers = {'User-Agent': 'Mozilla/5.0(Windows NT 10.0; Win64; x64)AppleWebKit/537.36(KHTML, like Gecko)Chrome/73.0.3683.86 Safari/537.36'}
list = []

url = "https://map.kakao.com/"

# 1. 카카오 지도 접속하기
driver.get(url)

print("\n검색할 장소를 입력하세요 : ", end="", flush=True)
searchloc = input()
print("저장할 파일 이름을 입력하세요 : ", end="", flush=True)
filename = input()

# 2. 검색창에 입력받은 장소명 입력 후 찾기 버튼 누르기
search_box = driver.find_element(By.XPATH, '//*[@id="search.keyword.query"]')
search_box.send_keys(searchloc) # 검색어 입력
driver.find_element(By.XPATH,'//*[@id="search.keyword.submit"]' ).send_keys(Keys.ENTER)
time.sleep(2)
# 3. 장소 버튼 클릭
driver.find_element(By.XPATH,'//*[@id="info.main.options"]/li[2]/a').send_keys(Keys.ENTER)


# 음식점 이름, 평점, 리뷰, 링크, 주소 저장
def storeNamePrint():
    time.sleep(0.2)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    cafe_lists = soup.select('.placelist > .PlaceItem')
    count = 1
    for cafe in cafe_lists:
        temp = []
        cafe_name = cafe.select('.head_item > .tit_name > .link_name')[0].text
        category = cafe.select('.head_item.clickArea > .subcategory')[0].text
        food_score = cafe.select('.rating > .score > .num')[0].text
        review = cafe.select('.rating > .review')[0].text
        link = cafe.select('.contact > .moreview')[0]['href']
        addr = cafe.select('.addr')[0].text

        # 리뷰 : 문제열 제거 후 숫자만 반환
        review = review[3:len(review)]

        # 숫자만 반환된 문자를 쉼표 제거
        review = int(re.sub(',','',review))

        temp.append(cafe_name)
        temp.append(category)
        temp.append(food_score)
        temp.append(review)
        temp.append(link)
        temp.append(addr)

        list.append(temp)

    # 원하는 저장 경로 지정
    
    save_dir = "C:/Users/mcw08/OneDrive/바탕 화면/동덕여대/2025 문화 디지털혁신 및 데이터 활용 공모전/새로운 데이터/카카오맵 크롤링 데이터(맛집)"  # ← 여기를 원하는 경로로 수정
    file_path = os.path.join(save_dir, filename + '.csv')

    f = open(file_path, 'w', encoding='utf-8-sig', newline='')
    writercsv = csv.writer(f)
    header = ['Name', 'Category','Score', 'Review_Num', 'Link', 'Addr']
    writercsv.writerow(header)

    for i in list:
        writercsv.writerow(i)
    f.close()

# 페이지수 넘기면서 크롤링
page = 1
page2 = 0
for i in range(0,34):

    try:
        page2+=1
        print(page,"크롤링 완료")
        time.sleep(2)
        driver.find_element(By.XPATH, f"//*[@id = 'info.search.page.no{page2}']").send_keys(Keys.ENTER)
        storeNamePrint()

        if (page2) % 5 == 0:
            driver.find_element(By.XPATH, f"//*[@id = 'info.search.page.next']").send_keys(Keys.ENTER)
            page2 = 0
            
        page += 1
    except:
        break
print("크롤링 끝!!")