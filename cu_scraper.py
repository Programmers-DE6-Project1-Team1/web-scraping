"""
CU 상품 크롤러 (macOS · Windows · Linux 공통)
- ChromeDriver 경로를 운영체제별로 직접 지정하지 않고,
  `webdriver‑manager`가 실행 시점에 알맞은 드라이버를 내려받아 사용합니다.
- Selenium ≥ 4.10, webdriver‑manager ≥ 4.0 권장
"""

import time
import os
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager   # NEW

def get_chrome_driver() -> webdriver.Chrome:
    """운영체제에 맞는 ChromeDriver를 자동 설치·재사용한다."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")          # 새 헤드리스 모드
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_experimental_option("detach", True) # 디버그용(선택)

    # Apple Silicon에서 드라이버가 x86으로 내려오는 경우:
    # os.environ["WDM_ARCH"] = "arm64"

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def crawl_cu_products() -> None:
    driver = get_chrome_driver()
    print("크롬 브라우저 실행 중...")

    base_url = (
        "https://cu.bgfretail.com/product/product.do?"
        "category=product&depth2=4&depth3={}"
    )
    detail_base_url = (
        "https://cu.bgfretail.com/product/view.do?category=product&gdIdx={}"
    )

    products = []

    for depth in range(1, 8):
        print(f"\n접속 중: depth3={depth}")
        driver.get(base_url.format(depth))

        # 더보기 버튼 반복 클릭
        try:
            while True:
                more_btn = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.prodListBtn-w > a")
                    )
                )
                print("더보기 클릭")
                driver.execute_script("arguments[0].click();", more_btn)
                time.sleep(1.2)
        except Exception:
            print("더보기 버튼 없음")

        soup = BeautifulSoup(driver.page_source, "html.parser")
        product_items = soup.select("li.prod_list")
        print(f"상품 수: {len(product_items)}")

        visited_ids: set[str] = set()

        for idx, item in enumerate(product_items):
            print(f"\n상품 {idx + 1} 처리 시작")

            onclick_elem = item.select_one(".prod_img")
            onclick_attr = onclick_elem.get("onclick", "") if onclick_elem else ""
            if "view(" not in onclick_attr:
                continue

            try:
                gdIdx = onclick_attr.split("view(")[1].split(")")[0].strip()
            except IndexError:
                continue

            if gdIdx in visited_ids:
                print(f"{gdIdx} 이미 처리됨 → 스킵")
                continue
            visited_ids.add(gdIdx)

            detail_url = detail_base_url.format(gdIdx)
            driver.get(detail_url)

            try:
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.prodDetail"))
                )

                detail_soup = BeautifulSoup(driver.page_source, "html.parser")
                product_name = detail_soup.select_one("div.prodDetail p.tit")

                promotion_tag_ul = detail_soup.select_one("ul.prodTag")
                promotion_tag_items = (
                    promotion_tag_ul.select("li")
                    if promotion_tag_ul and promotion_tag_ul.get("id") != "taglist"
                    else []
                )

                price = detail_soup.select_one("dd.prodPrice > p > span")
                product_description = detail_soup.select_one("ul.prodExplain > li")
                tag_list = detail_soup.select("ul#taglist > li")
                image = detail_soup.select_one("div.prodDetail img")
                label = detail_soup.select_one("span.tag img")

                promotion_tags, category_tags = [], []
                PROMOTION_KEYWORDS = ["1+1", "2+1"]

                for tag in promotion_tag_items:
                    text = tag.text.strip()
                    img = tag.find("img")
                    if img and img.get("alt"):
                        text = img["alt"].strip()
                    for t in text.split(","):
                        t = t.strip().replace("\u3000", "").replace("\xa0", "")
                        if t and any(k in t for k in PROMOTION_KEYWORDS):
                            if t not in promotion_tags:
                                promotion_tags.append(t)

                for t in tag_list:
                    cleaned = t.text.strip()
                    if cleaned:
                        category_tags.append(cleaned)

                name_text = product_name.text.strip() if product_name else None
                if not name_text:
                    continue

                promotion_text = ", ".join(promotion_tags) or None
                price_text = None
                if price and price.text:
                    price_clean = price.text.replace(",", "").strip()
                    price_text = int(price_clean) if price_clean.isdigit() else None

                description_text = (
                    product_description.text.strip() if product_description else None
                )
                tag_text = ", ".join(category_tags) or None

                image_url = None
                if image:
                    raw_src = image.get("src")
                    if raw_src:
                        image_url = raw_src if raw_src.startswith("http") else "https:" + raw_src

                label_text = label["alt"].strip() if label and label.get("alt") else None

                products.append(
                    [
                        name_text,
                        promotion_text,
                        price_text,
                        description_text,
                        tag_text,
                        image_url,
                        label_text,
                    ]
                )
                print("저장 완료:", name_text)

            except Exception as e:
                print("상세페이지 로딩 실패:", e)

    driver.quit()

    # CSV 저장
    with open("cu_products_standalone.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "product_name",
                "promotion_tag",
                "price",
                "product_description",
                "tag",
                "image_url",
                "label",
            ]
        )
        writer.writerows(products)

    print(f"\nCSV 저장 완료: {len(products)}개")


if __name__ == "__main__":
    crawl_cu_products()
