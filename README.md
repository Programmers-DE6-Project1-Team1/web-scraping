# web-scraping

# 🛒 CU 편의점 상품 크롤러

CU 편의점 웹사이트에서 상품 정보를 카테고리별로 크롤링하는 Python 스크립트입니다.  
상품명, 가격, 이미지, 신상품 여부, 행사 정보(1+1, 2+1) 등을 수집하며  
**신상품/베스트 여부와 행사 정보는 상품에 표시된 뱃지로 판별**합니다.  


## 📁 수집 데이터 예시

```json
{
  "category": "간편식사",
  "name": "햄치즈샌드위치",
  "price": "3,200",
  "image_url": "https://cu.bgfretail.com/images/product/sample.jpg",
  "is_new": true,
  "is_best": false,
  "event_types": ["1+1"]
}
```

---

## 🚀 사용법

### 🔹 1. 크롤러 실행

```bash
python cu_scraper.py
```

> 콘솔에 신상품만 출력됩니다.


## 🧩 필요 라이브러리

- `requests`
- `beautifulsoup4`

### 설치 방법

```bash
pip install -r requirements.txt
```

또는 수동 설치:

```bash
pip install requests beautifulsoup4
```

---

## 📂 파일 구조

```
.
├── cu_scraper.py       # 크롤링 스크립트
├── README.md           # 설명 파일
└── requirements.txt    # 필요한 라이브러리 목록
```

---
