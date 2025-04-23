import os
import pytest
import csv
from cu_scraper import crawl_cu_products, save_to_csv

@pytest.fixture(scope="module")
def products():
    return crawl_cu_products(test_mode=False)

def test_crawled_product_count(products):
    assert len(products) >= 100, "수집된 상품 수가 너무 적습니다"

def test_required_fields(products):
    for p in products:
        assert p[0] is not None and isinstance(p[1], str), "상품명이 없음"
        assert p[2] is None or isinstance(p[3], int), "가격이 숫자가 아님"

def test_no_duplicate_products(products):
    gdidx_list = [p[0] for p in products]  # p[0]은 gdIdx
    assert len(gdidx_list) == len(set(gdidx_list)), "gdIdx 기준 중복된 상품이 존재합니다"


def test_image_url_format(products):
    for p in products:
        url = p[6]
        if url:
            assert url.startswith("http://"), "이미지 URL 형식 오류"
def test_csv_creation(products):
    test_filename = "test_output.csv"
    save_to_csv(products, filename=test_filename)
    assert os.path.exists(test_filename), "CSV 파일 생성 실패"

    with open(test_filename, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        headers = next(reader)
        assert headers == [
            'gdIdx', 'product_name', 'promotion_tag', 'price',
            'product_description', 'tag', 'image_url', 'label'
        ]
