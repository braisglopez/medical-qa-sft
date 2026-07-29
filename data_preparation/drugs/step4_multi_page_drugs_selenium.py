import re
import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException


BASE_URL = "https://www.drugs.com"
START_URL = "https://www.drugs.com/medical-answers/"
OUTPUT_FILE = "./files/drugs_answers_all_pages.json"

START_PAGE = 1
MAX_PAGES = None  # None = recorrer hasta que no haya más páginas
MAX_QUESTIONS_DETECTED_PER_PAGE = 50


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


def unique_keep_order(items):
    seen = set()
    result = []

    for item in items:
        item = clean_text(item)
        if item and item not in seen:
            seen.add(item)
            result.append(item)

    return result


def is_real_medical_answer_url(href):
    if not href:
        return False

    if "/medical-answers/" not in href:
        return False

    if href.rstrip("/") == START_URL.rstrip("/"):
        return False

    if "#content" in href or href.endswith("/#") or href.endswith("#"):
        return False

    if "?page=" in href:
        return False

    pattern = r"^https://www\.drugs\.com/medical-answers/.+-\d+/?$"
    return re.match(pattern, href) is not None


def get_page_url(page_number):
    if page_number == 1:
        return START_URL
    return f"{START_URL}?page={page_number}"


def accept_consent_if_present(driver, timeout=8):
    try:
        consent_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//button[normalize-space()='Consent']"
            ))
        )
        print("[STEP 4] Popup detectado. Pulsando 'Consent'...")
        consent_button.click()
        time.sleep(2)
    except TimeoutException:
        print("[STEP 4] No apareció popup de consentimiento o ya estaba aceptado.")
    except Exception as e:
        print(f"[STEP 4] No se pudo pulsar 'Consent': {e}")


def wait_for_question_links(driver, timeout=20):
    def enough_real_links(d):
        hrefs = d.execute_script("""
            return Array.from(document.querySelectorAll('a'))
                .map(a => a.href)
                .filter(Boolean);
        """)
        real_links = [h for h in hrefs if is_real_medical_answer_url(h)]
        return len(real_links) >= 5

    WebDriverWait(driver, timeout).until(enough_real_links)


def get_question_links(driver, url, max_questions=50):
    print(f"\n[STEP 4] Abriendo listado: {url}\n")
    driver.get(url)

    print(f"[STEP 4] TITLE inicial: {driver.title}")
    print(f"[STEP 4] URL inicial: {driver.current_url}\n")

    accept_consent_if_present(driver)

    try:
        wait_for_question_links(driver)
    except Exception:
        print("[STEP 4] No se detectaron suficientes preguntas en esta página.")
        return []

    print(f"[STEP 4] TITLE final: {driver.title}")
    print(f"[STEP 4] URL final: {driver.current_url}\n")

    anchors = driver.find_elements(By.TAG_NAME, "a")

    seen = set()
    questions = []

    for a in anchors:
        try:
            href = a.get_attribute("href")
            text = a.text.strip()
        except StaleElementReferenceException:
            continue
        except Exception:
            continue

        if not is_real_medical_answer_url(href):
            continue

        if not text:
            continue

        if href not in seen:
            seen.add(href)
            questions.append({
                "title": text,
                "url": href
            })

    questions = questions[:max_questions]

    print("[STEP 4] Preguntas detectadas en la página:\n")
    for q in questions:
        print(f"[QUESTION] título='{q['title']}' -> url='{q['url']}'")

    print(f"\n[STEP 4] Total preguntas detectadas: {len(questions)}\n")

    return questions


def wait_for_question_page(driver, timeout=15):
    WebDriverWait(driver, timeout).until(
        lambda d: len(d.find_elements(By.TAG_NAME, "h1")) > 0
    )


def should_skip_line(line, title):
    low = line.lower()

    if not line:
        return True

    if line == title:
        return True

    if low.startswith("medically reviewed by"):
        return True
    if low.startswith("by "):
        return True
    if low.startswith("updated "):
        return True
    if low == "official answer by drugs.com":
        return True

    noise_exact = {
        "select the section you want to search in",
        "skip to main content",
        "contents",
        "advertisement",
        "medical answers",
        "drugs.com mobile apps",
        "support group",
        "more about",
        "related treatment guides",
        "terms of use",
        "privacy policy",
        "about us",
        "contact us",
    }

    if low in noise_exact:
        return True

    if len(line.split()) < 2:
        return True

    return False

def is_stop_line(line):
    """
    Decide si una línea marca el final del contenido útil del artículo.

    Queremos parar cuando empiecen secciones que ya no forman parte de
    la respuesta principal.
    """
    low = line.lower().strip()

    stop_lines = {
        "references",
        "read next",
        "see also:",
    }

    return low in stop_lines


def extract_full_answer_until_references(driver, question, source_page):
    question_url = question["url"]
    question_title_hint = question["title"]

    print("-" * 100)
    print(f"[STEP 4] Abriendo pregunta: {question_title_hint}")
    print(f"[STEP 4] URL: {question_url}")
    print(f"[STEP 4] Página origen del listado: {source_page}")
    print("-" * 100)

    driver.get(question_url)
    wait_for_question_page(driver)

    try:
        h1 = driver.find_element(By.TAG_NAME, "h1")
        title = clean_text(h1.text)
    except Exception:
        title = clean_text(question_title_hint)

    body_text = driver.find_element(By.TAG_NAME, "body").text
    lines = [clean_text(x) for x in body_text.splitlines() if clean_text(x)]
    lines = unique_keep_order(lines)

    capturing = False
    answer_blocks = []

    for line in lines:
        if line == title:
            capturing = True
            continue

        if not capturing:
            continue

        if is_stop_line(line):
            print(f"[STEP 4] Se encontró marca de parada: '{line}'")
            break

        if should_skip_line(line, title):
            continue

        answer_blocks.append(line)

    answer_blocks = unique_keep_order(answer_blocks)
    answer_text = " ".join(answer_blocks)

    return {
        "question": title,
        "url": question_url,
        "source_page": source_page,
        "answer_text": answer_text
    }


def save_results_to_json(results, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"[STEP 4] Resultados guardados en: {output_file}")


def main():
    driver = build_driver(headless=True)

    try:
        all_results = []
        seen_question_urls = set()
        page_number = START_PAGE

        while True:
            if MAX_PAGES is not None and page_number > MAX_PAGES:
                print(f"[STEP 4] Se alcanzó el límite manual de páginas: {MAX_PAGES}")
                break

            page_url = get_page_url(page_number)

            print("\n" + "=" * 110)
            print(f"[STEP 4] PROCESANDO PÁGINA {page_number}")
            print(f"[STEP 4] URL DEL LISTADO: {page_url}")
            print("=" * 110 + "\n")

            questions = get_question_links(
                driver,
                page_url,
                max_questions=MAX_QUESTIONS_DETECTED_PER_PAGE
            )

            if not questions:
                print(f"[STEP 4] Página {page_number} sin preguntas válidas. Fin del recorrido.")
                break

            selected_questions = []
            for q in questions:
                if q["url"] in seen_question_urls:
                    continue

                selected_questions.append(q)
                seen_question_urls.add(q["url"])

            if not selected_questions:
                print(f"[STEP 4] Página {page_number} no aportó preguntas nuevas. Fin del recorrido.")
                break

            print(f"[STEP 4] Preguntas nuevas seleccionadas en la página {page_number}: {len(selected_questions)}\n")

            for question in selected_questions:
                extracted = extract_full_answer_until_references(
                    driver,
                    question,
                    source_page=page_number
                )
                all_results.append(extracted)

            save_results_to_json(all_results, OUTPUT_FILE)

            page_number += 1

        print("\n" + "#" * 110)
        print("[STEP 4] RESUMEN FINAL")
        print(f"[STEP 4] Total páginas recorridas: {page_number - 1}")
        print(f"[STEP 4] Preguntas guardadas: {len(all_results)}")
        print(f"[STEP 4] Fichero generado: {OUTPUT_FILE}")
        print("#" * 110 + "\n")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
