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
```
---


### 🎯 4. 사용자 입력
```
media_type = input("검색할 분야 (drama, movie, artist): ").strip()
name = input("배우 또는 아티스트 이름 입력: ").strip()
region = input("지역 선택 (예: 경기): ").strip()
```

### 🔍 5. 필터링 및 예외 처리

```python
if media_type == 'drama':
    df = media_drama
elif media_type == 'movie':
    df = media_movie
elif media_type == 'artist':
    df = media_artist
else:
    raise ValueError("media_type은 drama, movie, artist 중 하나여야 합니다.")

# 이름, 지역 필터링
if media_type in ['drama', 'movie']:
    filtered = df[df['배우이름'].str.contains(name, na=False) & (df['주소_지역명'] == region)]
else:
    filtered = df[df['아티스트명'].str.contains(name, na=False) & (df['주소_지역명'] == region)]

# ❗ 빈 경우 처리
if filtered.empty:
    print("해당 배우/아티스트와 지역 조합으로 데이터가 없습니다.")
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=10)  # 서울
    display(m)
    exit()

```
### 🔢 6. 중심좌표 계산 및 거리 함수 정의

- **입력된 데이터를 기준으로 촬영지 데이터에서 추출**
    - drama/movie/artist 중 선택 1 → 아티스트명/배우명 입력 → 14개의 지역 중 선택 1
- 추출된 데이터를 보고 **사용자가 마음에 드는 장소 한 가지 선택**
- 선택된 데이터를 기준으로 맛집 3곳, 카페 3곳, 숙박 3곳을 추천
    - 각 촬영지 기준으로 거리 계산 → **geodesic  방식 사용 (두 점의 위도/경도 값으로 최단 거리 계산)**
- 장소별 중요 정보를 포함한 지도 시각화

```python

# ---------------------- [4. 촬영지 정제 및 중심좌표 계산] ----------------------
recommend_place = filtered.groupby('장소타입').apply(lambda x: x.head(3)).reset_index(drop=True)

# ---------------------- [★ 선택형 추천 기능 추가 위치] ----------------------
# unique 장소 목록 출력용
display_df = recommend_place[['제목', '장소명', '장소타입']].drop_duplicates().reset_index(drop=True)

# 출력
print("🎬 추천 촬영지 목록 (1개만 선택):")
for i, row in display_df.iterrows():
    print(f"{i+1}. 제목: {row['제목']}, 장소: {row['장소명']}, 타입: {row['장소타입']}")

# 선택
selected_index = input(f"\n추천받고 싶은 촬영지 번호를 입력하세요 (1 ~ {len(display_df)}): ").strip()

# 정수 변환 및 유효성 검사
if selected_index.isdigit():
    selected_index = int(selected_index) - 1
    if 0 <= selected_index < len(display_df):
        selected_row = display_df.loc[selected_index]
        # 선택된 장소 기준으로 recommend_place 필터링
        recommend_place = recommend_place[
            (recommend_place['제목'] == selected_row['제목']) &
            (recommend_place['장소명'] == selected_row['장소명']) &
            (recommend_place['장소타입'] == selected_row['장소타입'])
        ].reset_index(drop=True)
    else:
        print("❗입력한 번호가 유효하지 않습니다.")
        exit()
else:
    print("❗숫자로 입력해주세요.")
    exit()

results = []
for idx, row in recommend_place.iterrows():
    place_name = row['장소명']
    place_lat = row['위도']
    place_lng = row['경도']
    place_type = row['장소타입']
    place_title = row.get('제목', '제목 없음')

		**# 거리 계산 함수!!
		# # geodesic 방식 : 두 지리 좌표 간의 실제 지구 표면을 따라 측정한 최단 거리를 계산
		# # 입력 : 두 점의 (위도1, 경도1), (위도2, 경도2)
		# # 출력 : 두 점 사이의 거리 (단위 : m)**
    def calc_distance_to_place(r):
        try:
            return geodesic((place_lat, place_lng), (r['위도'], r['경도'])).meters
        except:
            return float('inf')

    kakao_food['거리'] = kakao_food.apply(calc_distance_to_place, axis=1)
    hotel_df['거리'] = hotel_df.apply(calc_distance_to_place, axis=1)

    closest_rests = kakao_food[(kakao_food['카테고리'] == 'restaurant') & (kakao_food['지역명'] == region)].sort_values('거리').head(3)
    closest_cafes = kakao_food[(kakao_food['카테고리'] == 'cafe') & (kakao_food['지역명'] == region)].sort_values('거리').head(3)
    closest_hotels = hotel_df[hotel_df['지역명'] == region].sort_values('거리').head(3)

    results.append({
        '촬영지 제목': place_title,
        '장소명': place_name,
        '장소타입': place_type,
        '맛집 목록': closest_rests['식당이름'].tolist() if not closest_rests.empty else ['-'],
        '맛집 거리(m)': [round(d, 2) for d in closest_rests['거리'].tolist()] if not closest_rests.empty else ['-'],
        '카페 목록': closest_cafes['식당이름'].tolist() if not closest_cafes.empty else ['-'],
        '카페 거리(m)': [round(d, 2) for d in closest_cafes['거리'].tolist()] if not closest_cafes.empty else ['-'],
        '숙소 목록': closest_hotels['숙박명'].tolist() if not closest_hotels.empty else ['-'],
        '숙소 거리(m)': [round(d, 2) for d in closest_hotels['거리'].tolist()] if not closest_hotels.empty else ['-'],
    })

recommend_detail = pd.DataFrame(results)
print("\n📍 각 촬영지별 주변 추천 (3개씩):")
display(recommend_detail)

```
![촬영지 데이터 기반 근처 맛집, 카페, 숙소 추천 리스트]("C:/Users/mcw08/Downloads/image (4).png")


