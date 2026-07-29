import re
import json
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


TEST_URL = "https://www.who.int/news-room/fact-sheets/detail/healthy-diet"
OUTPUT_FILE = "./files/who_step1_single_test.json"


def build_driver(headless=True):
    options = Options()

    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(45)
    return driver


def clean_text(text):
    if not text:
        return ""
    text = text.replace("\u200b", " ").replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def wait_for_page(driver, timeout=20):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )


def extract_title_and_first_paragraph(driver, url):
    print(f"[STEP 1] Abriendo: {url}")
    driver.get(url)
    wait_for_page(driver)
    time.sleep(2)

    title = ""
    first_paragraph = ""

    try:
        h1 = driver.find_element(By.TAG_NAME, "h1")
        title = clean_text(h1.text)
    except Exception:
        pass

    # Buscamos párrafos visibles con texto suficiente
    paragraphs = driver.find_elements(By.TAG_NAME, "p")
    for p in paragraphs:
        text = clean_text(p.text)
        if len(text.split()) >= 8:
            first_paragraph = text
            break

    return {
        "url": url,
        "title": title,
        "first_paragraph": first_paragraph
    }


def main():
    driver = build_driver(headless=True)

    try:
        data = extract_title_and_first_paragraph(driver, TEST_URL)
        save_json(data, OUTPUT_FILE)

        print("\n[STEP 1] Resultado:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        print(f"\n[STEP 1] Guardado en: {OUTPUT_FILE}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
