import re
import json
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException


START_URL = "https://www.who.int/news-room/fact-sheets"
OUTPUT_FILE = "./files/who_step2_all_topics.json"

MAX_TOPICS = None   # None = coger todos


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
    driver.set_page_load_timeout(15)
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

    print(f"[STEP 2] Resultados guardados en: {path}")


def is_real_fact_sheet_url(href):
    if not href:
        return False

    href = href.strip()

    if not href.startswith("https://www.who.int/news-room/fact-sheets/detail/"):
        return False

    if "#" in href:
        return False

    if href.rstrip("/") == "https://www.who.int/news-room/fact-sheets/detail":
        return False

    return True


def wait_for_index_page(driver, timeout=5):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    WebDriverWait(driver, timeout).until(
        lambda d: len(d.find_elements(By.TAG_NAME, "a")) > 20
    )


def get_all_fact_sheet_links(driver, url, max_topics=None):
    print(f"\n[STEP 2] Abriendo índice: {url}\n")
    driver.get(url)

    wait_for_index_page(driver)
    time.sleep(3)

    print(f"[STEP 2] TITLE: {driver.title}")
    print(f"[STEP 2] URL: {driver.current_url}\n")

    anchors = driver.find_elements(By.TAG_NAME, "a")

    topics = []
    seen_urls = set()

    for a in anchors:
        try:
            href = a.get_attribute("href")
            text = clean_text(a.text)
        except StaleElementReferenceException:
            continue
        except Exception:
            continue

        if not is_real_fact_sheet_url(href):
            continue

        if not text:
            continue

        if href in seen_urls:
            continue

        seen_urls.add(href)

        topics.append({
            "title": text,
            "url": href
        })

        if max_topics is not None and len(topics) >= max_topics:
            break

    topics.sort(key=lambda x: x["title"].lower())

    print("[STEP 2] Temas detectados:\n")
    for topic in topics:
        print(f"[TOPIC] '{topic['title']}' -> {topic['url']}")

    print(f"\n[STEP 2] Total temas detectados: {len(topics)}\n")

    return topics


def main():
    driver = build_driver(headless=True)

    try:
        topics = get_all_fact_sheet_links(
            driver,
            START_URL,
            max_topics=MAX_TOPICS
        )

        save_json(topics, OUTPUT_FILE)

        print("\n" + "#" * 110)
        print("[STEP 2] RESUMEN FINAL")
        print(f"[STEP 2] Temas guardados: {len(topics)}")
        print(f"[STEP 2] Fichero generado: {OUTPUT_FILE}")
        print("#" * 110 + "\n")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()