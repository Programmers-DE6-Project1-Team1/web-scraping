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

def crawl_cu_products(test_mode=False):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")

    service = Service(executable_path=os.path.join(os.getcwd(), "chromedriver.exe"))
    driver = webdriver.Chrome(service=service, options=chrome_options)

    print("크롬 브라우저 실행 중...")

    base_url = "https://cu.bgfretail.com/product/product.do?category=product&depth2=4&depth3={}"
    detail_base_url = "https://cu.bgfretail.com/product/view.do?category=product&gdIdx={}"

    products = []

    depth_range = range(1, 8)
    
    for depth in depth_range:
        print(f"\n접속 중: depth3={depth}")
        driver.get(base_url.format(depth))

        try:
            while True:
                more_btn = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.prodListBtn-w > a"))
                )
                print("더보기 클릭")
                driver.execute_script("arguments[0].click();", more_btn)
                time.sleep(1.2)
        except:
            print("더보기 버튼 없음")

        soup = BeautifulSoup(driver.page_source, "html.parser")
        product_items = soup.select("li.prod_list")
        print(f"상품 수: {len(product_items)}")

        visited_ids = set()

        for idx, item in enumerate(product_items):
            if test_mode and idx >= 10:  # 테스트 모드일 경우 최대 10개만
                break

            print(f"\n상품 {idx + 1} 처리 시작")

            onclick = item.select_one(".prod_img")
            if not onclick or "view(" not in onclick.get("onclick", ""):
                continue

            try:
                gdIdx = onclick["onclick"].split("view(")[1].split(")")[0].strip()
            except:
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
                promotion_tag_items = []
                if promotion_tag_ul and promotion_tag_ul.get("id") != "taglist":
                    promotion_tag_items = promotion_tag_ul.select("li")

                price = detail_soup.select_one("dd.prodPrice > p > span")
                product_description = detail_soup.select_one("ul.prodExplain > li")
                tag_list = detail_soup.select("ul#taglist > li")
                image = detail_soup.select_one("div.prodDetail img")
                label = detail_soup.select_one("span.tag img")

                promotion_tags = []
                category_tags = []

                PROMOTION_KEYWORDS = ['1+1', '2+1']
                for tag in promotion_tag_items:
                    text = tag.text.strip()
                    img = tag.find("img")
                    if img and img.get("alt"):
                        text = img.get("alt").strip()
                    for t in text.split(','):
                        t = t.strip().replace('\u3000', '').replace('\xa0', '')
                        if not t:
                            continue
                        if any(keyword in t for keyword in PROMOTION_KEYWORDS):
                            if t not in promotion_tags:
                                promotion_tags.append(t)

                for t in tag_list:
                    cleaned = t.text.strip()
                    if cleaned:
                        category_tags.append(cleaned)

                name_text = product_name.text.strip() if product_name else None
                promotion_text = ", ".join(promotion_tags) if promotion_tags else None
                price_text = None
                if price and price.text:
                    price_clean = price.text.replace(",", "").strip()
                    price_text = int(price_clean) if price_clean.isdigit() else None
                description_text = product_description.text.strip() if product_description else None
                tag_text = ", ".join(category_tags) if category_tags else None

                image_url = None
                if image:
                    raw_src = image.get("src")
                    if raw_src:
                        # 중복 접두사 방지: 예를 들어 "https:http://..." 같은 경우
                        if raw_src.count("http") > 1:
                            print(f"잘못된 이미지 URL 감지됨: {raw_src}")
                        elif raw_src.startswith("http://") or raw_src.startswith("https://"):
                            image_url = raw_src
                        elif raw_src.startswith("//"):
                            image_url = "https:" + raw_src

                label_text = label["alt"].strip() if label and label.get("alt") else None

                if not name_text:
                    continue

                products.append([
                    gdIdx,
                    name_text, promotion_text, price_text, description_text,
                    tag_text, image_url, label_text
                ])
                print("저장 완료:", name_text)

            except Exception as e:
                print("상세페이지 로딩 실패:", e)

    driver.quit()
    return products

def save_to_csv(products, filename="cu_products_standalone.csv"):
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(['gdIdx', 'product_name', 'promotion_tag', 'price', 'product_description', 'tag', 'image_url', 'label'])
        writer.writerows(products)
    print(f"\nCSV 저장 완료: {len(products)}개")

if __name__ == "__main__":
    data = crawl_cu_products(test_mode=False)  # 테스트할 땐 True로 바꾸면 빨라짐
    save_to_csv(data)