from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver

from Modelo.requester import Requester
from dataclasses import dataclass
from httpcore import ProxyError
from asyncio import subprocess
from httpx import ReadTimeout
from bs4 import BeautifulSoup
from typing import List

import subprocess
import requests
import time
import re



@dataclass
class Item:
    id: str
    title: str
    price: str
    brand_title: str
    photo: str
    url: str
    raw_timestamp: float

class VintedAPI:


    def __init__(self, locale: str = "www.vinted.es", type_search: str = "API", proxy: str = None):
        self.api_endpoint = f"http://www.vinted.es/api/v2/catalog/items" 
        self.base_url = f"{locale}" #self.base_url = f"https://{locale}"
        self.locale = locale
        self.search_number = 0
        self.proxy = proxy

        if type_search == "API":
            self.client = Requester(self.locale)
        else:
            self.chromedriver_path = ChromeDriverManager().install()
            self.service = Service(executable_path=self.chromedriver_path, log_path="nul")
            self.service.creationflags = subprocess.CREATE_NO_WINDOW
            self.configure_selenium(proxy)



    # <-> Configuracion de parametros para la busqueda de Selenium, mejora de rendimiento y errores
    #

    def configure_selenium(self, proxy: str = None):

        self.options = Options()
        self.options.add_argument("--headless=new")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        #self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        #self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument("--use-gl=swiftshader")
        self.options.add_argument("--enable-unsafe-swiftshader")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-infobars")

        print(f"[API] Proxy: {proxy}")
        if proxy:
            self.options.add_argument(f'--proxy-server={proxy}')


    # <-> Busca artículos usando la API de Vinted
    #     Devuelve una lista de objetos Item que contienen la información de los artículos.

    def search_items_vinted_api(self, search_text: str, page: int = 1, per_page: int = 20, proxy: str = None) -> List[Item]:

        #start_time = time.time()

        # FALTA, SI RECIBO UNA URL, EXTRAER PARAMETROS Y CREAR UNA REQUEST EN CONDICIONES, AÑADIR PARAMETROS SEGUN LA URL A LOS PARAMS
        params = {
            "search_text": "poster",
            "page": page,
            "per_page": per_page,
            "order": "newest_first",
        }

        try:
            # Actualizamos el proxy del cliente si se proporciona
            if self.proxy:
                proxies = {
                    "http": self.proxy,
                    "https": self.proxy
                }
                self.client.set_proxy(proxies=proxies)
            elif proxy:
                print("[API] El proxy elegido es:", proxy)
                proxies = {
                    "http": proxy,
                    "https": proxy
                }
                self.client.set_proxy(proxies=proxies)
            # Realizamos la solicitud a la API
            response = self.client.get(self.api_endpoint, params=params)

            #print(f"[API] Request URL: {response.url}")
            #print(f"[API] Response text: {response.text[:50000]}")

            if not response:
                print("[ERROR] No response received.")
                return []

            if "Enable JavaScript and cookies" in response.text:
                print("[ERROR] Cloudflare block detected.")
                return []
            
            if response.status_code != 200:
                print(f"[API] Error en la API: {response.status_code if response else 'No response'}")
                return []

            try:
                data = response.json()
                # Procesar data["items"] y convertir a objetos Item
            except Exception as e:
                print(f"[ERROR] Could not parse response as JSON: {e}")
                return []

        except ReadTimeout:
            print(f"[API] Timeout al acceder a {self.api_endpoint} con proxy: {proxy}")
            return []
        except ProxyError:
            print(f"[API] Error con el proxy: {proxy}")
            return []
        except requests.RequestException as e:
            print(f"[API] Error inesperado: {e}")
            return []
        except Exception as e:
            print(f"[API] Error desconocido: {e}")
            return []
    
        # Procesamos los items de la respuesta
        items = self.format_items_api(data, items=[])

        if len(items) > 0:
            self.search_number += 1

        #duration = time.time() - start_time
        #print(f"[API] search_items_vinted_api duró {duration:.2f} segundos")

        return items


    # <-> Devuelve los items procesados de la búsqueda HTML

    def format_items_api(self, data, items= []) -> List[Item]:
        for entry in data.get("items", []):
            items.append(Item(
                id=str(entry.get("id")),
                title=entry.get("title", ""),
                price=str(entry.get("price", {}).get("amount", "")),
                brand_title=entry.get("brand", {}).get("title", ""),
                photo=entry.get("photo", {}).get("url", ""),
                url=f"https://www.vinted.es/items/{entry.get('id')}",
                raw_timestamp=entry.get("created_at_ts", 0)
            ))
        return items


    # <-> FALTA COMPLETAR Obtiene los parámetros de la URL y los devuelve en un diccionario

    def url_to_params(self, url: str) -> dict:
        params = {}
        return params


    # <-> Busca artículos scrapeando la página HTML de Vinted
    #     Devuelve una lista de objetos Item que contienen la información de los artículos.

    def search_items_vinted_html(self, search_url: str, page: int = 1, proxy: str = None) -> List[Item]:

        start_time = time.time()

        # Inicializar el driver de Selenium
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        # Elemento de espera para que la página cargue completamente
        self.wait = WebDriverWait(self.driver, 10)

        try:

            print(f"[API] Cargando página: {search_url}")
            # Obtener la página de búsqueda
            self.driver.get(search_url)
            # Esperar que carguen los items
            self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.feed-grid__item")))
            # Extrae el contenido de la página obtenida
            soup = BeautifulSoup(self.driver.page_source, "html.parser")

        except Exception as e:
            print(f"[API] Error al cargar la página: {type(e).__name__}: {e}")
            self.driver.quit()
            return []

        self.driver.quit()

        # Procesar los items de la página HTML, se puede limitar el número de items procesados
        items = self.parse_items_html(soup, items=[])

        if len(items) > 0:
            self.search_number += 1

        duration = time.time() - start_time
        print(f"[API] search_items_vinted_api duró {duration:.2f} segundos")
        return items


    # <-> Devuelve los items procesados de la búsqueda HTML
    #     Procesa el HTML de los items y devuelve una lista de objetos Item
    #     Utiliza selectores CSS para extraer la información de cada item.
    
    def parse_items_html(self, soup, items= [], num_items=50) -> List[Item]:
        # Selector para cada elemento del grid
        for item_div in soup.select("div.feed-grid__item"):

            if len(items) >= num_items:
                break
    
            try:
                # URL del producto
                link_tag = item_div.select_one("a.new-item-box__overlay")
                url = link_tag["href"] if link_tag else ""
                if url and not url.startswith("http"):
                    url = "https://www.vinted.es" + url

                # ID extraído del data-testid o de la url
                data_testid = item_div.select_one("[data-testid^='product-item-id-']")
                item_id = None
                if data_testid:
                    m = re.search(r'product-item-id-(\d+)', data_testid.get("data-testid", ""))
                    if m:
                        item_id = m.group(1)
                if not item_id and url:
                    item_id = url.split("/")[-1].split("-")[0]

                # Título
                title_tag = item_div.select_one("[data-testid$='--description-title']")
                title = title_tag.get_text(strip=True) if title_tag else "Sin título"

                # Estado (opcional, si quieres)
                # condition_tag = item_div.select_one("[data-testid$='--description-subtitle']")
                # condition = condition_tag.get_text(strip=True) if condition_tag else ""

                # Precio principal
                price_tag = item_div.select_one("[data-testid$='--price-text']")
                price = price_tag.get_text(strip=True) if price_tag else "?"

                # Precio con protección
                price_prot_tag = item_div.select_one("button[aria-label*='Protección al comprador incluida']")
                price_with_prot = None
                if price_prot_tag:
                    price_with_prot_span = price_prot_tag.select_one("span.web_ui__Text__subtitle")
                    if price_with_prot_span:
                        price_with_prot = price_with_prot_span.get_text(strip=True)

                # Imagen
                img_tag = item_div.select_one("img.web_ui__Image__content")
                photo = img_tag["src"] if img_tag and "src" in img_tag.attrs else ""

                items.append(Item(
                    id=item_id,
                    title=title,
                    price=price,
                    brand_title="",  # No disponible en el HTML proporcionado
                    photo=photo,
                    url=url,
                    raw_timestamp=int(time.time())
                ))

            except Exception as e:
                print(f"[API] Error procesando item: {e}")
                continue

        return items