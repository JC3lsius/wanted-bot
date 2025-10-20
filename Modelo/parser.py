from bs4 import BeautifulSoup
from Modelo.item import Item
from typing import List

import time, re
import requests


class Parser:

    # <-> Devuelve los items procesados de la búsqueda HTML de Vinted
    #     Procesa el HTML de los items y devuelve una lista de objetos Item
    #     Utiliza selectores CSS para extraer la información de cada item.
    @staticmethod
    def parse_items_vinted_html(soup, items=[], num_items=50) -> List[Item]:
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
                    brand_title="",
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
    @staticmethod
    def fetch_item_description(url):
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
    @staticmethod
    def parse_items_wallapop_html(soup, items = []) -> List[Item]:
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
    @staticmethod
    def parse_items_ebay_html(soup, items=[]) -> list[Item]:
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
    @staticmethod
    def parse_items_milanuncios_html(soup, items=[]) -> List[Item]:
        # Contenedor padre
        ad_list = soup.select_one("div.ma-AdList")
        if not ad_list:
            return items

        for article in ad_list.select("article.ma-AdCardV2"):
            # --- URL del anuncio ---
            link_tag = article.select_one("a.ma-AdCardListingV2-TitleLink")
            url = ""
            if link_tag:
                # Algunos enlaces no tienen href directamente
                url = link_tag.get("href", "")
                # A veces vienen sin dominio
                if url and url.startswith("/"):
                    url = "https://www.milanuncios.com" + url

            # --- Imagen ---
            img_tag = article.select_one("img.ma-AdCardV2-photo")
            photo = img_tag.get("src", "") if img_tag else ""

            # --- Título ---
            title = "Sin título"
            if link_tag:
                title = link_tag.get("title") or link_tag.get_text(strip=True)
            elif img_tag:
                title = img_tag.get("title", "Sin título")

            # --- Precio ---
            price_tag = article.select_one("span.ma-AdPrice-value")
            price = price_tag.get_text(strip=True) if price_tag else "?"

            # --- Ubicación ---
            location_tag = article.select_one("address.ma-AdLocation")
            location = location_tag.get_text(strip=True) if location_tag else ""

            # --- Descripción ---
            desc_tag = article.select_one("p.ma-AdCardV2-description")
            description = desc_tag.get_text(strip=True) if desc_tag else ""

            # --- Marca o categoría (si aplica) ---
            brand_tag = article.select_one("span.ma-AdTagList-item")
            brand = brand_tag.get_text(strip=True) if brand_tag else ""

            # --- Crear objeto Item ---
            items.append(Item(
                id=str(hash(title + url + price)),  # genera ID único reproducible
                title=title,
                price=price,
                description=description,
                brand_title=brand,
                photo=photo,
                url=url,
                raw_timestamp=int(time.time()),
                location=location if hasattr(Item, "location") else ""  # opcional
            ))

        return items