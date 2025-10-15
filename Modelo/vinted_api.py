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
    description: str
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

        self.options.add_argument("--log-level=3")
        #self.options.add_experimental_option('excludeSwitches', ['enable-logging'])

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


    # <-> Busca artículos scrapeando la página HTML de Vinted, Wallapop, Ebay o Milanuncios
    #     Devuelve una lista de objetos Item que contienen la información de los artículos.

    def search_items_html(self, search_url: str, page: int = 1, proxy: str = None, type: int = 3) -> List[Item]:

        start_time = time.time()

        # Inicializar el driver de Selenium
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        # Elemento de espera para que la página cargue completamente
        self.wait = WebDriverWait(self.driver, 20)

        try:

            print(f"[API] Cargando página: {search_url}")
            # Obtener la página de búsqueda
            self.driver.get(search_url)

            # Esperar que carguen los items
            # Vinted
            if type == 0:
                self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.feed-grid__item")))
            # Wallapop
            elif type == 1:
                self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[class*='item-card_ItemCard--vertical']")))
            # Ebay
            elif type == 2:
                self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.srp-results > li.s-card")))
            # Milanuncios
            else:
                #self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.ma-AdList > article.ma-AdCardV2")))
                #self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article")))
                

                #self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ma-AdList")))
                # Esperar hasta que los artículos individuales estén cargados
                #self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.ma-AdCardV2")))
                
                
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='AD_LIST']"))
)

            # Extrae el contenido de la página obtenida
            soup = BeautifulSoup(self.driver.page_source, "html.parser")

        except Exception as e:
            print(f"[API] Error al cargar la página: {type(e).__name__}: {e}")
            self.driver.quit()
            return []

        self.driver.quit()

        # Procesar los items de la página HTML, se puede limitar el número de items procesados
        if type == 0:
            items = self.parse_items_vinted_html(soup, items=[])
        elif type == 1:
            items = self.parse_items_wallapop_html(soup, items=[])
        elif type == 2:
            items = self.parse_items_ebay_html(soup, items=[])
        else:
            items = self.parse_items_milanuncios_html(soup, items=[])

        if len(items) > 0:
            self.search_number += 1

        duration = time.time() - start_time
        print(f"[API] search_items_api duró {duration:.2f} segundos")
        return items


    # <-> Devuelve los items procesados de la búsqueda HTML de Vinted
    #     Procesa el HTML de los items y devuelve una lista de objetos Item
    #     Utiliza selectores CSS para extraer la información de cada item.
    
    def parse_items_vinted_html(self, soup, items=[], num_items=50) -> List[Item]:
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

                # Añadir el item a la lista
                items.append(Item(
                    id=item_id,
                    title=title,
                    price=price,
                    description ="",
                    #description = self.fetch_item_description(url),
                    brand_title="",  # No disponible en el HTML proporcionado
                    photo=photo,
                    url=url,
                    raw_timestamp=int(time.time())
                ))

            except Exception as e:
                print(f"[API] Error procesando item: {e}")
                continue

        return items

    # <-> Obtiene la descripción de un item de Vinted de una url y lo añade a un item
    #     Reduce la velocidad del programa pero mejora la precisión en el filtrado de items      

    def fetch_item_description(self, url):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Referer": "https://www.vinted.es/",
                "Connection": "keep-alive",
                "Host": "www.vinted.es",
            }
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Selector CSS de la descripción
            desc_tag = soup.select_one("span.web_ui__Text__text.web_ui__Text__body.web_ui__Text__left.web_ui__Text__format")
            if desc_tag:
                # .get_text(strip=True) elimina espacios iniciales/finales
                return desc_tag.get_text(separator="\n", strip=True)
            return ""
        except Exception as e:
            print(f"Error obteniendo descripción de {url}: {e}")
            return ""
  
    # <-> Devuelve los items procesados de la búsqueda HTML de Wallapop
    #     Procesa el HTML de los items y devuelve una lista de objetos Item
    #     Utiliza selectores CSS para extraer la información de cada item.

    def parse_items_wallapop_html(self, soup, items = []) -> List[Item]:
        for item_div in soup.select("a[class*='item-card_ItemCard--vertical']"):
            # título
            title_tag = item_div.select_one("h3.item-card_ItemCard__title__5TocV")
            title = title_tag.get_text(strip=True) if title_tag else "Sin título"

            # precio
            price_tag = item_div.select_one("strong.item-card_ItemCard__price__pVpdc")
            price = price_tag.get_text(strip=True) if price_tag else "?"

            # imagen
            img_tag = item_div.select_one("img.item-card-images-slider_ItemCardImagesSlider__image__9JlAd")
            photo = img_tag["src"] if img_tag else ""

            # url
            url = item_div["href"]
            if not url.startswith("http"):
                url = "https://es.wallapop.com" + url
            
            # Añadir el item a la lista
            items.append(Item(
                id="item_id",
                title=title,
                price=price,
                description ="",
                brand_title="",
                photo=photo,
                url=url,
                raw_timestamp=int(time.time())
            ))
            
        return items
    
    # <-> Devuelve los items procesados de la búsqueda HTML de Ebay
    #     Procesa el HTML de los items y devuelve una lista de objetos Item
    #     Utiliza selectores CSS para extraer la información de cada item.
    
    def parse_items_ebay_html(self, soup, items=[]) -> list[Item]:
        # Buscar el contenedor padre
        items_ul = soup.select_one("ul.srp-results")
        if not items_ul:
            return items

        # Iterar sobre cada item <li> en eBay
        for li in items_ul.select("li.s-card"):
            # Título
            title_tag = li.select_one(".s-card__title span")
            title = title_tag.get_text(strip=True) if title_tag else "Sin título"

            # Precio
            price_tag = li.select_one(".s-card__price")
            price = price_tag.get_text(strip=True) if price_tag else "?"

            # URL del item
            link_tag = li.select_one("a.image-treatment, a.s-card__link")
            link = link_tag["href"] if link_tag else ""
            if link and not link.startswith("http"):
                link = "https://www.ebay.es" + link

            # Imagen
            img_tag = li.select_one("img.s-card__image")
            image = img_tag["src"] if img_tag else ""

            # Vendedor
            seller_tag = li.select_one(".su-card-container__attributes__secondary .s-card__attribute-row span.primary")
            seller = seller_tag.get_text(strip=True) if seller_tag else ""

            # Añadir el item a la lista
            items.append(Item(
                id="item_id",
                title=title,
                price=price,
                description ="",
                brand_title="",
                photo=image,
                url=link,
                raw_timestamp=int(time.time())
            ))

        return items

    # NO IMPLEMENTADO
    # <-> Devuelve los items procesados de la búsqueda HTML de Milanuncios
    #     Procesa el HTML de los items y devuelve una lista de objetos Item
    #     Utiliza selectores CSS para extraer la información de cada item.
    
    def parse_items_milanuncios_html(self, soup, items = []) -> List[Item]:
        # Contenedor padre
        ad_list = soup.select_one("div.ma-AdList")
        if not ad_list:
            return items

        # Iterar sobre cada artículo
        for article in ad_list.select("article.ma-AdCardV2"):
            # URL
            link_tag = article.select_one("a.ma-AdCardV2-link")
            url = link_tag["href"] if link_tag else ""

            # Imagen
            img_tag = article.select_one("img.ma-AdCardV2-photo")
            photo = img_tag["src"] if img_tag else ""

            # Título
            title = img_tag["title"] if img_tag and "title" in img_tag.attrs else "Sin título"

            # Precio
            price_tag = article.select_one(".ma-AdCardV2-headerListing")  # Ajustar según donde aparezca el precio
            price = price_tag.get_text(strip=True) if price_tag else "?"

            # Añadir el item a la lista
            items.append(Item(
                id="item_id",
                title=title,
                price=price,
                description ="",
                brand_title="",
                photo=photo,
                url=url,
                raw_timestamp=int(time.time())
            ))

        return items