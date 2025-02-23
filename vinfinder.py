from datetime import datetime, timezone
from pip._internal.utils import urls
from pyVinted import Vinted
from time import sleep
import threading
import requests
import platform
import warnings
import telegram
import requests
import asyncio
import random
import psutil
import time
import sys
import os


# Credenciales del BOT de Telegram
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""

# Envía una notificación de un producto a un canal de Telegram
async def send_notification(item):
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f'Hora_envio_{timestamp}.jpg'

    # Enviar la notificación a Telegram
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=img_file, caption="Persona detectada.")
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text= item.title + "\n\n" + item.url)
    print("Notificación enviada a través de Telegram.")

##############################################################################################
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

#########################
def imprimirDatos(item1):
    print(
        f"Nombre: {item1.title}\n"
        f"id: {item1.id}\n"
        f"Hora Item: {datetime.fromtimestamp(item1.raw_timestamp, tz=timezone.utc).strftime('%Y-%m-%d_%H-%M-%S')}\n"
        f"Precio: {item1.price}\n"
        f"Marca: {item1.brand_title}\n"
        f"Foto: {item1.photo}\n"
        f"Link: {item1.url}\n"
        '''f"Datos: {item1.raw_data}\n"'''
    )


def startBusqueda(itemcheck, timeWait = 5, timeLimit = 15, urls = [], noTags = [], tags = []):

    vinted = Vinted()
    items = vinted.items.search(
        "https://www.vinted.es/catalog?search_text=3ds%20xl&price_from=30.0&price_to=75.0&currency=EUR&search_id=14107566922&order=newest_first",
        20, 5)
    '''
    for item1 in items:
        comprobarItem(item, tags, noTags, urls)         
    '''
    sleep(5)

#####################
def borrarPantalla():
    if platform.system() == "Windows":
        os.system('cls')
    elif platform.system() == "Linux":
        os.system('clear')
    else:
        print("\nSistema no reconocido, comando no ejecutado...\n")

###########################
def checkParams(idle=True):

    if platform.system() not in ["Windows", "Linux"]:
        print(f"Sistema {platform.system()} no compatible, puede que el programa no funcione correctamente...\n")

    if(idle): print("\n")

    print(f"Sistema operativo: {platform.system()}"
          f"\nVersión: {platform.version()}"
          f"\nDetalles del sistema: {platform.platform()}"
          f"\nVersion de Python: {sys.version}"
          f"\n\nUsuario actual: {os.getlogin()}"
          f"\nID del proceso actual: {os.getpid()}"
          f"\nID del proceso padre: {os.getppid()}"
          f"\nUso de memoria: {psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024):.2f} MB"
          f"\n\nDirectorio actual: {os.getcwd()}"
          f"\nIPv6 Pública: {requests.get("https://api64.ipify.org?format=text").text}"
          f"\nIPv4 Pública: {requests.get("https://api4.ipify.org?format=text").text}\n\n"
    )

    if(idle):
        print(
            f" ______________________________________________\n"
            f"|                                              |\n"
            f"|          Pulse INTRO para iniciar...         |\n"
            f"|______________________________________________|\n"
        )
        input()
    else:
        print(f"Pulse INTRO para salir...\n")
        input()

    borrarPantalla()


def mostrar_menu(hilos_activos=[]):

    print("""\n 
       ..-+**************************+-..                                          
     .+**********************************+.                                         
    :+*************************************:                                        
    =**************++*********+::**********=.                                       
    +***********.     -*****+.  +**********+.                                       
    +***********      :*****:  :***********+.                                       
    +***********.     :****=   -***********+.                                       
    +***********.     .****   .+***********+.                                       
    +***********-     .+**:   -************+.                                       
    +***********=      +*+.   *************+.                                       
    +***********+.     =*-   -*************+.                                       
    +************:     -+.  .+*************+.                                       
    +************+     ..  .=***************.                                       
    +*************:        =****************.                                       
    +**************:    :+*****************+.                                       
    :**************************************:                                        
     .+**********************************+.                                         
       .:=****************************=:.     
    """)

    if(len(hilos_activos) > 0):
            imprimirHilos(hilos_activos)

    print(
        f"\n--- Menú de opciones ---\n"
        f"1. Ver información del Programa y del Sistema\n"
        f"2. Guardar configuración actual\n"
        f"3. Cargar configuración\n"
        f"4. Modificar filtros\n"
        f"5. Iniciar\n"
        f"6. Salir\n"
    )
    return input("Seleccione una opción: ")


def imprimirHilos(hilos_activos):

    return


def saveConf():
    return


def loadconf():
    return


def modifyFilters():
    return


def endProgram(hilosActivos):
    print("\nSaliendo del programa... \n")
    sleep(2)
    borrarPantalla()


def launchThread(params, tags, notTags, hilos_activos):
    if(hilos_activos.length == 4):
        print("\nLimite de hilos alcanzado, volviendo...\n")
        sleep(1)
    else:
        if(params[2] == ""):
            print(f"\nEJEMPLOS:"
                    f"https://www.vinted.es/catalog?search_text=camisa"
                    f"https://www.vinted.es/catalog?search_text=pelota&status_ids[]=2&page=1&price_from=10&currency=EUR&price_to=30"
                    f"\n")
            params[0] = input("Pega el link de busqueda del producto: ")
        # Crear el hilo
        hilo = threading.Thread(target=startBusqueda())
        hilo.start()
        hilos_activos.append(hilo.getName)
        params[2] = ""


def main():

    timeUrlParams = [15,5,""]
    tags = ["nintendo", "3ds", "hs", "broke", "rot"]
    notTags = ["gameboy", "gba", "gamecube", "cd", "n64", "nintendo64"]
    urls = []
    hilos_activos = []

    checkParams()

    while (True):

        option = mostrar_menu(hilos_activos)

        if option == "1":
            borrarPantalla()
            checkParams(False)
        elif option == "2":
            saveConf(timeUrlParams, tags, notTags)
        elif option == "3":
            loadconf(timeUrlParams, tags, notTags)
        elif option == "4":
            modifyFilters(timeUrlParams, tags, notTags)
        elif option == "5":
            launchThread(timeUrlParams, tags, notTags, hilos_activos)
        elif option == "6":
            endProgram(hilos_activos) 
            return
        else:
            print("Opción no válida. Por favor, intente de nuevo.")
            sleep(1)
        borrarPantalla()


if __name__ == "__main__":
    main()

#   consideraciones
# -------------------
#     Si la lista de articulos encontrados llega a 100, se borran las primeras 50 urls de referencia del listado
# SI  Hacer menu y interfaz al iniciar la busqueda que se interrumpa al introducir comando
#     Deteccion de errores y contador de fallos
#     Cambio de los parametros de busqueda
#     Compatibilidad con terminal de windows y Linux
#     Si hay un hilo corriendo (el programa) pedir que se cierre, y opciones de segundo plano

#   recomendaciones
# --------------------
# Utilizar proxy/VPN para que no te baneen la IP