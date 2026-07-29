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


def build_driver(headless=True):
    """
    Crea el navegador Chrome para Selenium.

    Parámetros:
    - headless=False:
      Si está a False, verás la ventana del navegador.
      Si está a True, trabajará en segundo plano.

    Qué hace:
    - configura Chrome con opciones razonables
    - añade un User-Agent realista
    - devuelve el driver listo para navegar
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


def clean_text(text):
    """
    Limpia un texto para hacerlo más manejable.

    Qué hace:
    - elimina espacios raros
    - compacta espacios repetidos
    - recorta espacios sobrantes
    """
    if not text:
        return ""

    text = text.replace("\u200b", " ").replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def unique_keep_order(items):
    """
    Elimina duplicados manteniendo el orden original.

    Esto es útil porque al leer texto visible del DOM pueden aparecer
    líneas repetidas varias veces.
    """
    seen = set()
    result = []

    for item in items:
        item = clean_text(item)
        if item and item not in seen:
            seen.add(item)
            result.append(item)

    return result


def is_real_medical_answer_url(href):
    """
    Comprueba si una URL corresponde a una pregunta real de Drugs.com.

    Queremos URLs como:
    https://www.drugs.com/medical-answers/tirzepatide-cause-cancer-3582083/

    Excluimos:
    - la portada principal
    - anchors
    - paginación
    - cualquier URL que no termine en slug-numero
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
    Intenta aceptar el popup de consentimiento si aparece.

    Esto hace más estable la carga de la página y evita que el contenido
    principal quede tapado o incompleto.
    """
    try:
        consent_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//button[normalize-space()='Consent']"
            ))
        )
        print("[STEP 2] Popup detectado. Pulsando 'Consent'...")
        consent_button.click()
        time.sleep(2)
    except TimeoutException:
        print("[STEP 2] No apareció popup de consentimiento o ya estaba aceptado.")
    except Exception as e:
        print(f"[STEP 2] No se pudo pulsar 'Consent': {e}")


def wait_for_question_links(driver, timeout=20):
    """
    Espera hasta que haya suficientes preguntas reales en el listado.

    No usamos una lista fija de WebElements en la espera porque el DOM
    puede cambiar y provocar StaleElementReferenceException.
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


def get_question_links(driver, url, max_questions=25):
    """
    Abre una página de Medical Answers y extrae hasta max_questions preguntas.

    En este step no distinguimos featured de normales porque ya has dicho
    que no te importa mezclarlas.

    Flujo:
    - abre el listado
    - acepta el popup si aparece
    - espera a que haya suficientes enlaces válidos
    - recorre los <a>
    - se queda con URLs reales de preguntas
    - elimina duplicados
    """
    print(f"\n[STEP 2] Abriendo listado: {url}\n")
    driver.get(url)

    print(f"[STEP 2] TITLE inicial: {driver.title}")
    print(f"[STEP 2] URL inicial: {driver.current_url}\n")

    accept_consent_if_present(driver)
    wait_for_question_links(driver)

    print(f"[STEP 2] TITLE final: {driver.title}")
    print(f"[STEP 2] URL final: {driver.current_url}\n")

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

    print("[STEP 2] Preguntas detectadas en la página:\n")
    for q in questions:
        print(f"[QUESTION] título='{q['title']}' -> url='{q['url']}'")

    print(f"\n[STEP 2] Total preguntas detectadas: {len(questions)}\n")

    return questions


def wait_for_question_page(driver, timeout=15):
    """
    Espera a que una página de pregunta tenga suficiente contenido.

    Usamos como señal mínima la presencia de un h1.
    """
    WebDriverWait(driver, timeout).until(
        lambda d: len(d.find_elements(By.TAG_NAME, "h1")) > 0
    )


def should_skip_line(line, title):
    """
    Decide si una línea debe excluirse del contenido útil del artículo.

    Aquí filtramos ruido típico:
    - metadatos
    - navegación
    - avisos
    - bloques que no forman parte de la respuesta

    Esta función es importante porque el texto visible del body mezcla
    contenido real del artículo con otros elementos de la página.
    """
    low = line.lower()

    if not line:
        return True

    if line == title:
        return True

    # Metadatos del artículo
    if low.startswith("medically reviewed by"):
        return True
    if low.startswith("by "):
        return True
    if low.startswith("updated "):
        return True
    if low == "official answer by drugs.com":
        return True

    # Ruido de navegación / interfaz
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

    # Líneas demasiado cortas suelen ser ruido, salvo que luego quieras
    # recuperar bullets cortos. Por ahora dejamos un filtro básico.
    if len(line.split()) < 2:
        return True

    return False


def extract_full_answer_until_references(driver, question):
    """
    Entra en una pregunta concreta y extrae TODO el contenido útil del artículo
    hasta llegar a 'References'.

    Estrategia:
    1. abre la página
    2. obtiene el título desde el h1
    3. lee todo el body visible
    4. elimina duplicados
    5. empieza a capturar después del título
    6. ignora líneas de metadatos y ruido
    7. deja de capturar cuando aparece 'References'
    8. construye:
       - answer_blocks: lista ordenada de bloques útiles
       - answer_text: respuesta unificada en un solo string

    Esta estrategia encaja mucho mejor con tu formato final pregunta-respuesta
    que una simple selección de “pasajes largos”.
    """
    question_url = question["url"]
    question_title_hint = question["title"]

    print("-" * 100)
    print(f"[STEP 2] Abriendo pregunta: {question_title_hint}")
    print(f"[STEP 2] URL: {question_url}")
    print("-" * 100)

    driver.get(question_url)
    wait_for_question_page(driver)

    # Intentamos sacar el título real desde el h1
    try:
        h1 = driver.find_element(By.TAG_NAME, "h1")
        title = clean_text(h1.text)
    except Exception:
        title = clean_text(question_title_hint)

    # Leemos todo el body visible
    body_text = driver.find_element(By.TAG_NAME, "body").text
    lines = [clean_text(x) for x in body_text.splitlines() if clean_text(x)]
    lines = unique_keep_order(lines)

    print(f"[STEP 2] TITLE FINAL: {title}")
    print(f"[STEP 2] Líneas útiles detectadas antes de recortar: {len(lines)}")

    capturing = False
    answer_blocks = []

    for line in lines:
        # Empezamos a capturar justo después del título
        if line == title:
            capturing = True
            continue

        if not capturing:
            continue

        # Cortamos al llegar a References
        if line.lower().strip() == "references":
            print("[STEP 2] Se encontró 'References'. Fin del contenido útil.")
            break

        if should_skip_line(line, title):
            continue

        answer_blocks.append(line)

    answer_blocks = unique_keep_order(answer_blocks)

    # Unimos los bloques en una única respuesta
    answer_text = " ".join(answer_blocks)

    print(f"[STEP 2] BLOQUES DE RESPUESTA DETECTADOS: {len(answer_blocks)}")
    for i, block in enumerate(answer_blocks[:35], start=1):
        print(f"  [BLOCK {i}] {block}")

    print("\n[STEP 2] RESPUESTA UNIFICADA (primeros 1000 caracteres):")
    print(answer_text[:1000] + ("..." if len(answer_text) > 1000 else ""))
    print()

    return {
        "question": title,
        "url": question_url,
        "answer_blocks": answer_blocks,
        "answer_text": answer_text
    }


def main():
    """
    Función principal del step 2.

    Flujo:
    1. abre el listado principal
    2. saca hasta 25 preguntas
    3. elige unas pocas para prueba
    4. entra en cada una
    5. extrae TODO el contenido útil hasta 'References'
    6. construye una respuesta unificada

    En este punto ya estamos muy cerca del formato final:
    - question
    - answer_text
    """
    driver = build_driver(headless=True)

    try:
        questions = get_question_links(driver, START_URL, max_questions=25)

        # Para la prueba, procesamos solo 5 preguntas
        questions_to_process = questions[:1]

        print("[STEP 2] Preguntas elegidas para prueba de extracción:\n")
        for q in questions_to_process:
            print(f"[TO PROCESS] título='{q['title']}' -> url='{q['url']}'")
        print()

        extracted_items = []

        for question in questions_to_process:
            extracted = extract_full_answer_until_references(driver, question)
            extracted_items.append(extracted)

        print("\n" + "#" * 100)
        print("[STEP 2] RESUMEN FINAL")
        print(f"[STEP 2] Total preguntas detectadas en listado: {len(questions)}")
        print(f"[STEP 2] Total preguntas procesadas en detalle: {len(extracted_items)}")
        print("#" * 100 + "\n")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
