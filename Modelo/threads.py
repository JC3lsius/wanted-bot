from datetime import datetime
import random
from time import sleep
import threading
import concurrent
import requests
import telegram
from Modelo.vinted_api import VintedAPI

# Credenciales del BOT de Telegram
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""


#------------------------#
# METODOS DEL HILO PROXY #
#------------------------#


# <-> Obtiene un proxy funcional revisado de una lista de proxies
#     Si no hay proxies en la lista, busca proxies gratuitos y los prueba.

def get_working_proxy(proxies= [], blackList_proxies= [], test_url="https://www.vinted.es", stop_event=None, proxy_lock=None):

    good_proxies_finded = 0

    while not stop_event.is_set():
        total_Proxies = get_free_proxies(stop_event)
        random.shuffle(total_Proxies)

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(test_proxy, proxy, test_url, stop_event): proxy for proxy in total_Proxies if proxy not in blackList_proxies}
            for future in concurrent.futures.as_completed(futures):
                proxy_result = future.result()
                if proxy_result and proxy_result not in proxies and proxy_result not in blackList_proxies:
                    good_proxies_finded+= 1
                    proxies.append(proxy_result)
                    print(f"\n[PROXY] Proxy funcional encontrado: {proxy_result}")
                    print("[PROXY] Tamaño de lista de proxies funcionales: ", len(proxies))
                    print("[PROXY] Tamaño de blacklist: ", len(blackList_proxies))

        print("[PROXY] Ha finalizado la busqueda de proxies.")


# <-> Obtiene proxies de varios sitios web sin comprobar su funcionalidad

def get_free_proxies(stop_event):
    url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=elite"
    response = requests.get(url)
    raw_proxies = response.text.strip().split("\n")
    proxies = [f"http://{proxy.strip()}" for proxy in raw_proxies if proxy.strip()]
    print(f"\n[PROXY] Proxies Proxyscrape obtenidos: {len(proxies)}")
    return proxies


# <-> Prueba un proxy para ver si es funcional
#     Si el proxy es funcional, lo devuelve, si no, devuelve False

def test_proxy(proxy, test_url="https://www.vinted.es", stop_event=None):

    thread_name = threading.current_thread().name
    # print(f"[PROXY] [{thread_name}] Probando proxy: {proxy}")
    if stop_event.is_set():
        return None
    try:
        if not proxy.startswith("http://") and not proxy.startswith("https://"):
            proxy = "http://" + proxy

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Connection": "keep-alive"
        }

        test_url = "https://www.vinted.es"

        response = requests.get(
            test_url,
            proxies={"http": proxy, "https": proxy},
            headers=headers,
            timeout=15,
        )

        #print(f"[{thread_name}] Probando proxy: {proxy} - Status: {response.status_code}")

        if response.status_code == 200:
            return proxy
        else:
            return False

    except requests.exceptions.ProxyError:
        return False
    except requests.exceptions.ConnectTimeout:
        return False
    except requests.exceptions.ReadTimeout:
        return False
    except requests.exceptions.RequestException:
        return False


# <-> Envia una notificación a Telegram con los datos del item encontrado
#     Se debe tener configurado el bot de Telegram y el chat ID

async def send_notification(item):

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f'Hora_envio_{timestamp}'

    # Enviar la notificación a Telegram
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=img_file, caption="Persona detectada.")
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text= item.title + "\n\n" + item.url)
    print("Notificación enviada a través de Telegram.")


#-------------------------#
# METODOS DEL HILO FINDER #
#-------------------------#


# <-> Comprueba si un item cumple con los criterios establecidos
#     y envía una notificación si es así.

def comprobarItem(itemcheck, timeWait, timeLimit, urls, noTags, tags):

    name = str(itemcheck.title).lower()
    resultado = (datetime.now().replace(microsecond=0) - datetime.fromtimestamp(itemcheck.raw_timestamp)).total_seconds()

    # Parametros para tener en cuenta el articulo
    if (resultado < timeLimit
    and itemcheck.url not in urls
    and any(word in name for word in tags)
    and not any(worde in name for worde in noTags)
    ):
        send_notification(itemcheck)
        urls.append(itemcheck.url)

    #sleep(timeWait)


# <-> Inicia la búsqueda de artículos en Vinted
#     Se encarga de buscar artículos y comprobar si cumplen con los criterios establecidos.

def startBusqueda(linkName, timeLimit=15, timeWait=10, urls=[], noTags=[], tags=[], proxyType=None, proxies=None, blacklist_proxies=None, stop_event=None, type="API"):

    vinted = VintedAPI(linkName)
    print(f"TIPO DE PROXY: {proxyType}")
    proxy_golden_list = []
    proxy = None

    while not stop_event.is_set():

        # Asignar un proxy si es necesario
        if(proxyType == "AUTOMATIC"):
            while True:
                print(f"\n[SEARCH] Buscando proxy...")
                if proxies:
                    proxy = proxies.pop(0)
                    print(f"\n[SEARCH] Proxy Obtenido de la lista: {proxy}")
                    break
                if not proxy:
                    sleep(1)
        elif proxyType:
            proxy = proxyType
        
        # Busqueda de artículos y comprobación de items
        errors = 0
        for i in range(50):

            if  type == "API":
                items = vinted.search_items_vinted_api(linkName, page=1, proxy=proxy)
            else:
                items = vinted.search_items_vinted_html(linkName, page=1, proxy=proxy)

            if len(items) == 0:
                errors += 1
                if errors >= 6:
                    blacklist_proxies.append(proxy)
                    print("[THREAD] No se encontraron artículos, cambiando de proxy...")
                    break
            else:
                errors = 0
                print(f"[SEARCH] Artículos encontrados: {len(items)}")

                # for itemcheck in items:
                #     comprobarItem(itemcheck, timeWait, timeLimit, urls, noTags, tags)

                sleep(timeWait/4)


#----------------------#
# INICIADORES DE HILOS #
#----------------------#


# ---> Hilo de búsqueda de artículos
#       Este hilo se encarga de buscar artículos en Vinted y comprobar si cumplen con los criterios establecidos.

def searchThread(params, tags, notTags, proxy, hilos_activos, proxies=None, blacklist_proxies=None, proxy_lock=None, thread_limit=3):

    if hilos_activos >= thread_limit:
        print("\nLimite de hilos alcanzado, volviendo...\n")
        sleep(1)
        return None

    stop_event = threading.Event()
    hilo = threading.Thread(
        name="hilo_search",
        target=startBusqueda,
        args=(params[2], params[0], params[1], [], notTags, tags, proxy, proxies, blacklist_proxies, stop_event)
    )
    hilo.start()

    return hilo


# ---> Hilo de búsqueda de proxies
#       Este hilo se encarga de buscar proxies funcionales y añadirlos a la lista de proxies.

def proxyfinder(proxies=[], blacklist_proxies=[], linkName="https://www.vinted.es", proxy_lock=None):

    stop_event = threading.Event()
    hilo = threading.Thread(
        name="hilo_proxy",
        target=get_working_proxy,
        args=(proxies, blacklist_proxies, linkName, stop_event, proxy_lock)
    )
    hilo.start()

    return hilo


# ---> Monitor de hilos activos
#       Este hilo se encarga de monitorizar los hilos activos y eliminar los que ya no están vivos.

def monitor(hilos_activos, check_interval=1):

    while True:
        for hilo in hilos_activos:
            if not hilo.is_alive():         
                print(f"⚠️ ALERTA: {hilo} ha dejado de funcionar.")
                hilos_activos.remove(hilo)
        sleep(check_interval)