import re
import json
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


INPUT_FILE = "./files/who_step2_all_topics.json"
OUTPUT_DIR = "./files/who_topics"

MAX_TOPICS_TO_PROCESS = None   # None = procesar todos


def build_driver(headless=False):
    options = Options()

    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.page_load_strategy = "eager"

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


def unique_keep_order(items):
    seen = set()
    result = []

    for item in items:
        item = clean_text(item)
        if item and item not in seen:
            seen.add(item)
            result.append(item)

    return result


def slugify(text):
    text = clean_text(text).lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[-\s]+", "_", text)
    return text.strip("_")


def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_topics(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def wait_for_detail_page(driver, timeout=20):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )


def get_main_container(driver):
    selectors = [
        "main",
        "[role='main']",
        ".sf-content-block",
        ".article-content",
        ".content"
    ]

    for selector in selectors:
        try:
            return driver.find_element(By.CSS_SELECTOR, selector)
        except Exception:
            continue

    return driver.find_element(By.TAG_NAME, "body")


def should_keep_paragraph(text, title):
    text_low = text.lower()

    if not text:
        return False

    if text == title:
        return False

    if len(text.split()) < 8:
        return False

    noise_starts = [
        "related",
        "more information",
        "news",
        "copyright"
    ]

    if any(text_low.startswith(x) for x in noise_starts):
        return False

    return True


def extract_topic_content(driver, topic, index_num, total):
    url = topic["url"]
    title_hint = topic.get("title", "")

    print("-" * 110)
    print(f"[STEP 3] [{index_num}/{total}] Abriendo tema: {title_hint}")
    print(f"[STEP 3] URL: {url}")
    print("-" * 110)

    driver.get(url)
    wait_for_detail_page(driver)
    time.sleep(2)

    try:
        title = clean_text(driver.find_element(By.TAG_NAME, "h1").text)
    except Exception:
        title = clean_text(title_hint)

    container = get_main_container(driver)

    try:
        p_elements = container.find_elements(By.TAG_NAME, "p")
    except Exception:
        p_elements = driver.find_elements(By.TAG_NAME, "p")

    paragraphs = []

    for p in p_elements:
        try:
            text = clean_text(p.text)
        except Exception:
            continue

        if should_keep_paragraph(text, title):
            paragraphs.append(text)

    paragraphs = unique_keep_order(paragraphs)
    first_paragraph = paragraphs[0] if paragraphs else ""
    full_text = " ".join(paragraphs)

    print(f"[STEP 3] Título extraído: {title}")
    print(f"[STEP 3] Nº párrafos útiles: {len(paragraphs)}")

    return {
        "title": title,
        "url": url,
        "first_paragraph": first_paragraph,
        "all_paragraphs": paragraphs,
        "full_text": full_text
    }


def main():
    topics = load_topics(INPUT_FILE)

    if MAX_TOPICS_TO_PROCESS is not None:
        topics = topics[:MAX_TOPICS_TO_PROCESS]

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    driver = build_driver(headless=False)

    try:
        total = len(topics)

        for i, topic in enumerate(topics, start=1):
            data = extract_topic_content(driver, topic, i, total)

            safe_name = slugify(data["title"]) or f"topic_{i}"
            output_path = os.path.join(OUTPUT_DIR, f"{safe_name}.json")

            save_json(data, output_path)
            print(f"[STEP 3] Guardado: {output_path}\n")

        print("\n" + "#" * 110)
        print("[STEP 3] RESUMEN FINAL")
        print(f"[STEP 3] Total temas procesados: {total}")
        print(f"[STEP 3] Carpeta generada: {OUTPUT_DIR}")
        print("#" * 110 + "\n")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
