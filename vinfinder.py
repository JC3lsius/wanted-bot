from datetime import datetime, timezone
from pip._internal.utils import urls
from time import sleep
import threading
import logging
import requests
import platform
import warnings
import requests
import asyncio
import random
import psutil
import time
import sys
import os

import UIface
import threads


def loadConf(url_list, tags, no_tags):
    if not os.path.exists("conf"):
        print("No se encontró el archivo de configuración conf")
        sleep(2)
        return

    section = None

    try:
        with open("conf", "r") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if not linea:
                    continue

                if linea.startswith("URL:"):
                    url_list[0] = linea.split("URL:")[1].strip()
                elif linea.startswith("Tags:"):
                    section = "tags"
                    tags.clear()
                elif linea.startswith("No Tags:"):
                    section = "no_tags"
                    no_tags.clear()
                else:
                    if section == "tags":
                        tags.append(linea)
                    elif section == "no_tags":
                        no_tags.append(linea)
    except PermissionError:
        print("Error: No tienes permisos para leer el archivo.")
    except UnicodeDecodeError:
        print("Error: El archivo contiene caracteres no reconocidos.")
    except OSError as e:
        print(f"Error inesperado al leer el archivo: {e}")
    
    print("Configuración cargada con éxito:")
    print(f"URL: {url_list[0]}")
    print(f"Tags: {tags}")
    print(f"Tags a ignorar: {no_tags}")

    sleep(2)


def modifyFilters(timeUrlParams, tags, notTags):
    return


def main():

    timeUrlParams = [15,10]
    tags = ["nintendo", "3ds", "hs", "broke", "rot"]
    notTags = ["gameboy", "gba", "gamecube", "cd", "n64", "nintendo64"]
    urls = [""]
    hilos_activos = []

    monitor_thread = threading.Thread(target=threads.monitor, daemon=True, args=(hilos_activos,))
    monitor_thread.start()

    UIface.checkParams()

    while (True):
        UIface.borrarPantalla()
        option = UIface.mostrar_menu(hilos_activos)

        if option == "1":
            UIface.borrarPantalla()
            UIface.checkParams(False)
        elif option == "2":
            loadConf(timeUrlParams, tags, notTags)
        elif option == "3":
            hilos_activos.add(threads.launchThread(timeUrlParams, tags, notTags, len(hilos_activos)))
        elif option == "4":
            UIface.endProgram(hilos_activos) 
            return
        else:
            print("Opción no válida. Por favor, intente de nuevo.")
            sleep(1)
        UIface.borrarPantalla()


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
#     Control de errores de hilo

#   recomendaciones
# --------------------
# Utilizar proxy/VPN para que no te baneen la IP