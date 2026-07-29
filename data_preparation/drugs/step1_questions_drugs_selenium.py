import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException


BASE_URL = "https://www.drugs.com"
START_URL = "https://www.drugs.com/medical-answers/"


def build_driver(headless=False):
    """
    Crea el navegador Chrome para Selenium.

    Parámetros:
    - headless=False:
      Si está a False, se verá la ventana del navegador.
      Si está a True, trabajará en segundo plano.

    Qué hace:
    - configura Chrome para parecer un navegador real
    - añade un User-Agent estándar
    - devuelve el driver listo para usar
    """
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


def is_real_medical_answer_url(href):
    """
    Comprueba si una URL corresponde de verdad a una pregunta de Drugs.com.

    Queremos enlaces como:
    https://www.drugs.com/medical-answers/tirzepatide-cause-cancer-3582083/

    Excluimos:
    - la portada principal
    - anchors tipo # o #content
    - paginación ?page=
    - cualquier cosa que no termine en slug-numero
    """
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


def accept_consent_if_present(driver, timeout=8):
    """
    Intenta aceptar automáticamente el popup de consentimiento.

    Por qué hace falta:
    Si no se acepta el popup, muchas veces la página no deja acceder bien
    al contenido principal y solo detectas 1 pregunta o muy pocas.

    Estrategia:
    - espera unos segundos a ver si aparece un botón con texto 'Consent'
    - si aparece, hace click
    - si no aparece, sigue sin romper
    """
    try:
        consent_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//button[normalize-space()='Consent']"
            ))
        )
        print("[STEP 1] Popup de consentimiento detectado. Haciendo click en 'Consent'...")
        consent_button.click()
        time.sleep(2)
    except TimeoutException:
        print("[STEP 1] No apareció popup de consentimiento o ya estaba aceptado.")
    except Exception as e:
        print(f"[STEP 1] No se pudo pulsar 'Consent': {e}")


def wait_for_question_links(driver, timeout=20):
    """
    Espera hasta que haya suficientes enlaces reales de preguntas.

    No usamos una lista fija de WebElements en la espera porque el DOM puede
    cambiar y provocar StaleElementReferenceException.

    En su lugar leemos los href actuales desde JavaScript.
    """
    def enough_real_links(d):
        hrefs = d.execute_script("""
            return Array.from(document.querySelectorAll('a'))
                .map(a => a.href)
                .filter(Boolean);
        """)

        real_links = [h for h in hrefs if is_real_medical_answer_url(h)]
        return len(real_links) >= 20

    WebDriverWait(driver, timeout).until(enough_real_links)


def get_question_links(driver, url, max_questions=20):
    """
    Abre la página principal de Medical Answers y extrae preguntas reales.

    Qué hace:
    - abre la URL
    - intenta aceptar el popup de consentimiento
    - espera a que haya preguntas reales disponibles
    - recorre los enlaces <a>
    - filtra solo URLs válidas de preguntas
    - elimina duplicados
    - se queda con las primeras max_questions

    Nota:
    Aquí nos quedamos con 20 preguntas normales para la prueba.
    Las 5 featured no nos interesan ahora.
    """
    print(f"\n[STEP 1] Abriendo: {url}\n")
    driver.get(url)

    print(f"[STEP 1] TITLE inicial: {driver.title}")
    print(f"[STEP 1] URL inicial: {driver.current_url}\n")

    # Intentamos cerrar/aceptar el popup si aparece
    accept_consent_if_present(driver)

    # Esperamos a que haya suficientes preguntas reales
    wait_for_question_links(driver)

    print(f"[STEP 1] TITLE final: {driver.title}")
    print(f"[STEP 1] URL final: {driver.current_url}\n")

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

    # Ordenamos por aparición natural en la página, sin ordenar alfabéticamente,
    # porque aquí nos interesa respetar el orden visible.
    questions = questions[:max_questions]

    print("[STEP 1] Preguntas detectadas:\n")
    for q in questions:
        print(f"[QUESTION] título='{q['title']}' -> url='{q['url']}'")

    print(f"\n[STEP 1] Total preguntas detectadas: {len(questions)}\n")

    return questions


def main():
    """
    Función principal del step 1.

    En este paso validamos que:
    - se puede abrir la página
    - se acepta el popup automáticamente
    - se detectan preguntas reales
    - se obtienen 20 preguntas normales
    """
    driver = build_driver(headless=False)

    try:
        questions = get_question_links(driver, START_URL, max_questions=25)

        print("[STEP 1] RESUMEN FINAL")
        print(f"[STEP 1] Número de preguntas extraídas: {len(questions)}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
