import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

MAINCATEGORY = {
    '10': '간편식사',
    '20': '즉석조리',
    '30': '과자류',
    '40': '아이스크림',
    '50': '식품',
    '60': '음료',
}

headers = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/123.0.0.0 Safari/537.36'
    )
}


def fetch_products(cate_cd, category_name):
    """특정 카테고리의 상품들을 크롤링"""
    products = []

    for page in range(1, 15):
        url = "https://cu.bgfretail.com/product/productAjax.do"

        data = {
            "pageIndex": str(page),
            "listType": "prod",
            "cateCd": cate_cd,
            "category": "1",
            "depth1": "1",
            "depth2": "4",
            "pageSize": "20"
        }

        res = requests.post(url, data=data, headers=headers)

        if res.status_code != 200:
            logging.warning(f"[{category_name}] 페이지 {page}: 요청 실패 (status {res.status_code})")
            break

        soup = BeautifulSoup(res.text, "html.parser")
        product_tags = soup.select("li.prod_list")

        if not product_tags:
            logging.info(f"[{category_name}] 페이지 {page}: 상품 없음 (종료)")
            break

        for tag in product_tags:
            name_tag = tag.select_one(".name p")
            price_tag = tag.select_one(".price strong")
            img_tag = tag.select_one(".prod_img img")

            if not (name_tag and price_tag and img_tag):
                continue

            # 🏷️ 뱃지 분류 (중복 허용)
            badge_imgs = tag.select("img")
            is_new = False
            is_best = False
            event_types = []

            for b in badge_imgs:
                src = b.get("src", "").lower()
                if "new" in src:
                    is_new = True
                elif "best" in src:
                    is_best = True
                if "1plus1" in src or "1+1" in src:
                    event_types.append("1+1")
                elif "2plus1" in src or "2+1" in src:
                    event_types.append("2+1")

            products.append({
                "category": category_name,
                "name": name_tag.get_text(strip=True),
                "price": price_tag.get_text(strip=True),
                "image_url": urljoin("https://cu.bgfretail.com", img_tag["src"]),
                "is_new": is_new,
                "is_best": is_best,
                "event_types": event_types
            })

    return products


def main():
    all_products = []

    for cate_cd, category_name in MAINCATEGORY.items():
        logging.info(f"📂 [{category_name}] 크롤링 시작")
        category_products = fetch_products(cate_cd, category_name)
        all_products.extend(category_products)

    logging.info(f"\n✅ 크롤링 완료! 총 {len(all_products)}개 상품 수집됨\n")
    return all_products


if __name__ == "__main__":
    products = main()

    # 👀 신제품만 예시 출력
    for p in products:
        if p["is_new"]:
            print(p)

    # 💾 JSON 저장
    with open("cu_products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    print("✔ cu_products.json 파일로 저장 완료!")
