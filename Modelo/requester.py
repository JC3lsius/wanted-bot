import requests
from requests.exceptions import HTTPError
from dataclasses import dataclass
from typing import Optional

class Requester:
    def __init__(self, locale="www.vinted.es", proxies: Optional[dict] = None):
        self.max_retries = 3
        #self.base_url = f"https://{locale}"
        self.base_url = f"{locale}"
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Referer": "https://www.vinted.es/",
            "Connection": "keep-alive",
            "Host": "www.vinted.es",
        }
        self.proxies = proxies
        self.session.headers.update(self.headers)
        self.session.cookies.set('cookie_name', 'cookie_value')

    def set_proxy(self, proxies):
        self.proxies = proxies

    def set_cookies(self):
        self.session.cookies.clear_session_cookies()
        try:
            self.session.head(self.base_url)
            # print("Cookies set!")

        except Exception as e:
            print(f"There was an error fetching cookies for vinted\n Error : {e}")

    def get(self, url, params=None):
        """
        Realiza una peticion http de tipo get.
        :param url: str
        :param params: dict, optional
        :return: dict
            Json format
        """
        # Asegúrate de que las cookies están configuradas al menos una vez
        if not self.session.cookies or not self.session.cookies.get_dict():
            self.set_cookies()
        if self.proxies:
            self.session.proxies.update(self.proxies)

        tried = 0
        while tried < self.max_retries:
            tried += 1

            response = self.session.get(url, params=params)

            if response.status_code == 401 and tried < self.max_retries:
                print(f"[SEARCH] Cookies invalid retrying {tried}/{self.max_retries}")
                self.set_cookies()

            elif response.status_code == 200 or tried == self.max_retries:
                return response

        return HTTPError