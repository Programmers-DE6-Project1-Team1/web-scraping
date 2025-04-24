# 🛒 CU 편의점 상품 크롤러

CU 편의점 웹사이트에서 상품 정보를 크롤링하여 CSV 파일로 저장하는 Python 스크립트입니다.  
Django나 기타 웹서버 없이 **단독 실행만으로 작동**합니다.

---

## 📋 수집 정보 항목

| 항목 | 설명 |
|------|------|
| 상품명 | 제품 이름 |
| 행사 정보 | 1+1, 2+1 등 |
| 가격 | 숫자형 가격 (쉼표 제거) |
| 설명 | 상세 설명 |
| 태그 | 제품 태그 목록 |
| 이미지 URL | 제품 이미지 주소 |
| 라벨 | 대표 뱃지 텍스트 (ex. 신상품 등) |

---

## 📁 결과 파일 예시

스크립트를 실행하면 같은 디렉토리에 `cu_products_standalone.csv` 파일이 생성됩니다.

```csv
product_name,promotion_tag,price,product_description,tag,image_url,label
"삼각김밥","1+1",1200,"든든한 한끼","간편식사","https://...","신상품"
...
```

---

## 🚀 실행 방법

### 1. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

> 💡 `chromedriver`는 현재 디렉토리에 `chromedriver.exe`로 위치해야 합니다.  
> 버전이 설치된 Chrome과 호환되어야 정상 동작합니다.

---

### 2. 스크립트 실행

```bash
python cu_scraper.py
```

---

## 📦 주요 기술 스택

- **Selenium**: 동적 페이지 제어 및 버튼 클릭
- **BeautifulSoup**: HTML 파싱
- **CSV**: 파일 저장 포맷

---

## 🚀 함수 설명

| 함수                              | 주요 기능 및 설명                                                                                                                         |
|-----------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| `get_chrome_driver()`             | - `webdriver-manager` 이용해 운영체제별 ChromeDriver 자동 설치·관리<br>- 헤드리스 모드, 윈도우 크기(1920×1080), sandbox 비활성화 등 옵션 설정<br>- `webdriver.Chrome` 인스턴스 반환 |
| `crawl_cu_products(test_mode=False)` | - `depth3` 카테고리(1~7) 순회<br>- “더보기” 버튼 반복 클릭으로 전체 상품 로드<br>- `gdIdx` 기반 중복 검사 및 `test_mode`(최대 10개) 지원<br>- 상세 페이지 접속 후 **상품명·행사·가격·설명·태그·이미지·라벨** 파싱<br>- `[상품명, 행사, 가격, 설명, 태그, 이미지 URL, 라벨]` 리스트 반환 |
| `save_to_csv(products, filename)` | - 수집된 `products` 리스트를 **UTF-8 BOM(utf-8-sig)** 형식의 CSV로 저장<br>- 헤더 행 자동 작성 후 모든 데이터 기록                                        |


## 💡 기타 정보

- 크롤링 범위: `depth3` 1~7까지 전체 카테고리
- 중복 방지를 위해 `gdIdx` 기준으로 중복 처리
- CSV는 UTF-8 BOM(`utf-8-sig`)으로 저장되어 Excel에서 바로 열림

---

## 📂 파일 구조

```
.
├── cu_scraper.py            # 크롤링 스크립트 (단독 실행)
├── cu_products_standalone.csv  # 크롤링 결과 (실행 후 생성됨)
└── README.md                # 설명 파일
```

---

## 🧑‍💻 작성자

- CU 웹 구조 기준으로 수작업 파싱
- 해당 코드 및 문서 작성: 범준 & 민주
