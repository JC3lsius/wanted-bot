from requests.exceptions import RequestException, ProxyError, ConnectionError
from requests.exceptions import HTTPError
from dataclasses import dataclass
from typing import Optional

import requests

class Requester:


    def __init__(self, locale="www.vinted.es", proxies: Optional[dict] = None):
        self.max_retries = 3
        #self.base_url = f"https://{locale}"
        self.base_url = f"{locale}"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Referer": "https://www.vinted.es/",
            "Connection": "keep-alive",
            "Host": "www.vinted.es",
        }
        self.proxies = proxies
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.cookies.set('cookie_name', 'cookie_value')


    def set_proxy(self, proxies):
        self.proxies = proxies


    def set_cookies(self):
        self.session.cookies.clear_session_cookies()
        try:
            self.session.head(self.base_url)
            print("Cookies set!")

        except Exception as e:
            print(f"There was an error fetching cookies for vinted\n Error : {e}")


    def get(self, url, params=None):
        """
        Realiza una petición HTTP GET con manejo de proxy, cookies y reintentos.
        :param url: str
        :param params: dict, optional
        :return: dict o None si falla
        """

        # Asegúrate de que las cookies están configuradas al menos una vez
        if not self.session.cookies or not self.session.cookies.get_dict():
            self.set_cookies()

        # Si hay proxy, configurarlo
        if self.proxies:
            print("[DEBUG] Usando proxy configurado:", self.proxies)
            self.session.proxies.update(self.proxies)

            # Testeo del proxy (opcional)
            try:
                response = self.session.get("https://httpbin.org/ip", timeout=10)
                print("[PROXY TEST] IP reportada por httpbin:", response.text)
            except Exception as e:
                print("[PROXY TEST] El proxy falló:", e)
                # Aquí puedes decidir si seguir o abortar
                return None

        # Petición con reintentos
        tried = 0

        while tried < self.max_retries:
            tried += 1
            try:
                response = self.session.get(url, params=params, timeout=10)

                if response.status_code == 401 and tried < self.max_retries:
                    print(f"[SEARCH] Cookies invalid. Retrying {tried}/{self.max_retries}")
                    self.set_cookies()

                elif response.status_code == 200 or tried == self.max_retries:
                    return response

                print(f"[SEARCH] RESPONSE: {response.status_code} - {response.reason}")

            except (ProxyError, ConnectionError) as e:
                print(f"[SEARCH] Proxy/Connection error: {e}. Retrying {tried}/{self.max_retries}")
            except RequestException as e:
                print(f"[SEARCH] Error en la petición: {e}. Retrying {tried}/{self.max_retries}")

        # Si todos los intentos fallan
        print("[SEARCH] Todos los intentos fallaron.")
        return None