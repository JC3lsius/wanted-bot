from datetime import datetime, timezone
from pyVinted import Vinted
from time import sleep
import threading
import telegram


# Credenciales del BOT de Telegram
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""


def launchThread(params, tags, notTags, hilos_activos):
    if(hilos_activos == 2):
        print("\nLimite de hilos alcanzado, volviendo...\n")
        sleep(1)
    else:
        if(len(params) == 2):
            print(f"\nEJEMPLOS:"
                    f"\nhttps://www.vinted.es/catalog?search_text=camisa"
                    f"\nhttps://www.vinted.es/catalog?search_text=pelota&status_ids[]=2&page=1&price_from=10&currency=EUR&price_to=30"
                    f"\n")
            params.append(input("Pega el link de busqueda del producto: "))
        # Crear el hilo
        hilo = threading.Thread(name= "hilo_search", target=startBusqueda, args=(params[2], params[0], params[1], [], notTags, tags))
        hilo.start()
        params.pop()
        return hilo



# Envía una notificación de un producto a un canal de Telegram
async def send_notification(item):
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f'Hora_envio_{timestamp}.jpg'

    # Enviar la notificación a Telegram
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=img_file, caption="Persona detectada.")
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text= item.title + "\n\n" + item.url)
    print("Notificación enviada a través de Telegram.")


def comprobarItem(itemcheck, timeWait = 5, timeLimit = 15, urls = [], noTags = [], tags = []):
    """
    Comprueba si un producto cumple los requisitos específicos antes de enviar la notificación.

    Parámetros:
        itemcheck (objeto): Objeto que representa un artículo.
        timeWait (int, opcional): Tiempo de espera.
        timeLimit (int, opcional): Tiempo máximo en segundos para considerar el artículo como reciente.
        urls (list, opcional): Lista de URLs ya notificadas para evitar duplicados.
        noTags (list, opcional): Lista de palabras clave que descartan el artículo.
        tags (list, opcional): Lista de palabras clave que consideran el artículo.

    Retorno:
        None
    """
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

    sleep(timeWait)


def startBusqueda(linkName, timeLimit = 15, timeWait = 10, urls = [], noTags = [], tags = []):

    while(True):
        vinted = Vinted()
        items = vinted.items.search(linkName,20, 5)
        
        for item1 in items:
            item1.photo
            comprobarItem(item, tags, noTags, urls)         
        
        sleep(timeWait)


def monitor(hilos_activos):
    while True:
        for hilo in hilos_activos:
            if not hilo.is_alive():         
                print(f"⚠️ ALERTA: {hilo} ha dejado de funcionar.")
                hilos_activos.pop(hilo)
        sleep(1)