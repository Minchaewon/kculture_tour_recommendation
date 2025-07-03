> 📁  
>
> ## 활용한 데이터
>
> ```markdown
> * **카카오맵 맛집 크롤링 데이터** : kakao_food_deduplicated.csv  
> 
> * **촬영지 데이터(미디어타입 별 분할)** :  
>     * drama : media_drama.csv  
>     * movie : media_movie.csv  
>     * artist : media_artist.csv  
> 
> * **숙박 데이터** :  
>     * hotel_pre.csv  
> ```
>
> ---
>
> 📃  
>
### 🧩 1. 사용 데이터
>
> | 데이터명       | 데이터 건수 | 데이터 주요 컬럼                                    |
> | -------------- | ----------- | ------------------------------------------------- |
> | kakao_food     | 5441        | 식당이름, 카테고리, 별점, 리뷰 수, 웹사이트, 주소    |
> | media_drama    | 7339        | 제목, 장소명, 장소타입, 장소설명, 주소, 배우이름     |
> | media_movie    | 273         | 제목, 장소명, 장소타입, 장소설명, 주소, 배우이름     |
> | media_artist   | 1962        | 제목, 장소명, 장소타입, 장소설명, 주소, 아티스트명    |
> | hotel_pre      | 130         | 숙박명, 도로명주소, 성급, 최소가격, 최대가격, 평균평점 |
>
> 📍 배우이름, 아티스트명 : 새로 추출한 컬럼

---

### 🔧 2. 주요 기능

- 사용자 입력 (배우/아티스트명, 지역, 콘텐츠 유형)
- 해당 인물의 **촬영지 추천** (장소타입별 최대 3곳)
- 촬영지 기준 **거리 기반 맛집·카페·숙박 추천** (각 3곳)
- 지도 시각화 및 팝업 기능
- 결과 지도 HTML로 저장

### 📦 3. 필요 라이브러리 및 전처리

```python
import pandas as pd
import folium
from geopy.distance import geodesic
from IPython.display import display

media_drama = pd.read_csv(".../media_drama_pre.csv", encoding='utf-8-sig')
media_movie = pd.read_csv(".../media_movie_pre.csv", encoding='utf-8-sig')
media_artist = pd.read_csv(".../media_artist_pre.csv", encoding='utf-8-sig')
kakao_food = pd.read_csv(".../kakao_food_geocode.csv", encoding="utf-8-sig")
hotel_df = pd.read_csv(".../hotel_pre.csv", encoding='utf-8-sig')

hotel_df.columns = hotel_df.columns.str.strip()
hotel_df.rename(columns={
    'Unnamed: 0': '번호',
    'LDGS_NM': '숙박명',
    'LDGS_ADDR': '지역명',
    'LDGS_ROAD_NM_ADDR': '도로명주소',
    'GSRM_SCALE_CN': '규모',
    'LDGS_GRAD_VALUE': '성급',
    'LDGMNT_TY_NM': '숙박유형',
    'LDGS_AVRG_PRC': '평균가격',
    'LDGS_MIN_PRC': '최소가격',
    'LDGS_MXMM_PRC': '최대가격',
    'LDGS_AVRG_SCORE_CO': '평균평점',
}, inplace=True)

---


🎯 4. 사용자 입력
python
복사
편집
media_type = input("검색할 분야 (drama, movie, artist): ").strip()
name = input("배우 또는 아티스트 이름 입력: ").strip()
region = input("지역 선택 (예: 경기): ").strip()
