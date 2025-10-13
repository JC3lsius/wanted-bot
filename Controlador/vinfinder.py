from time import sleep

import Modelo.threads as threads
import Vista.UIface as UIface
import threading
import os
import re

class Vinfinder:

    def __init__(self):
        self.url = None
        self.tags = []
        self.notTags = []
        self.timeUrlParams = [15, 10]
        self.hilos_activos = []
        self.proxy = None
        self.proxies = []
        self.blacklist_proxies = []
        self.proxy_lock = threading.Lock() 
        self.thread_limit = 30
        self.search = "API"

    
    # <-> Carga la configuración del archivo conf.txt que tiene que estar en la misma carpeta que el script
    #     Si no existe, se crea un archivo conf.txt con una configuración por defecto

    def loadConf(self):

        if not os.path.exists("conf"):
            print("\nNo se encontró el archivo de configuración conf.\n\nSino existe, cree un archivo conf.txt en la misma carpeta donde ejecutaste el script.\n")
            sleep(1)
            return

        section = None
        self.tags = []
        self.notTags = []

        try:
            with open("conf", "r", encoding="utf-8") as archivo:
                for linea in archivo:
                    linea = linea.strip()

                    # Detectar secciones
                    if linea.startswith("http"):
                        self.url = linea
                        continue
                    elif linea.startswith("Tags:"):
                        section = "tags"
                        continue
                    elif linea.startswith("No Tags:"):
                        section = "not_tags"
                        continue
                    elif linea.startswith("Time Params:"):
                        section = "time_params"
                        continue
                    elif linea.startswith("Proxy:"):
                        section = "proxy"
                        continue
                    elif linea.startswith("Search:"):
                        section = "search"
                        continue

                    # Ignorar líneas vacías que no aportan contenido
                    if not linea:
                        continue

                    # Cargar contenido según la sección actual
                    if section == "tags":
                        self.tags.append(linea)
                    elif section == "not_tags":
                        self.notTags.append(linea)
                    elif section == "time_params":
                        numeros = re.findall(r'\d+', linea)
                        self.timeUrlParams.extend([int(n) for n in numeros])
                        if len(self.timeUrlParams) > 2:
                            self.timeUrlParams = self.timeUrlParams[:2]
                    elif section == "proxy":
                        self.proxy = linea.strip()
                    elif section == "search":
                        self.search = linea.strip()
                        
        except PermissionError:
            print("Error: No tienes permisos para leer el archivo.")
        except UnicodeDecodeError:
            print("Error: El archivo contiene caracteres no reconocidos.")
        except OSError as e:
            print(f"Error inesperado al leer el archivo: {e}")

        print("\nConfiguración cargada con éxito:")
        print(f"URL: {self.url if self.url else 'No definida'}")
        print(f"Tags: {self.tags}")
        print(f"Tags a ignorar: {self.notTags}")
        print(f"Time Params: {self.timeUrlParams}")
        print(f"Proxy: {self.proxy}")
        print(f"Search: {self.search}")
        print("\n\nEspere 1 segundo...")
        sleep(1)


    # <-> Inicia la búsqueda de artículos en Vinted
    #     Se encarga de iniciar el hilo de búsqueda y el hilo de búsqueda de proxies
    #     Si se ha definido un proxy, lo utiliza para la búsqueda de artículos.

    def run(self):

        monitor_thread = threading.Thread(target=threads.monitor, daemon=True, args=(self.hilos_activos,))
        monitor_thread.start()

        UIface.checkParams()

        while True:
            #UIface.borrarPantalla()
            option = UIface.mostrar_menu(self.hilos_activos)

            if option == "1":
                UIface.borrarPantalla()
                UIface.checkParams(False)
            elif option == "2":
                config_result = self.loadConf()
                if config_result is False:
                    UIface.mostrar_error("No se pudo cargar la configuración.")
            elif option == "3":
                if not self.url:
                    url_input = input("Introduce la URL de búsqueda (debe contener '?'): ").strip()
                    if "?" not in url_input:
                        sleep(1)
                        UIface.mostrar_error("La URL de búsqueda no contiene parámetros. Revisa la URL introducida.")
                        continue
                    else:
                        self.url = url_input
                # Hilo de búsqueda
                hilo = threads.searchThread(
                    [self.timeUrlParams[0], self.timeUrlParams[1], self.url],
                    self.tags,
                    self.notTags,
                    self.proxy,
                    len(self.hilos_activos),
                    self.proxies, 
                    self.blacklist_proxies,
                    self.proxy_lock,
                    self.thread_limit,
                    self.search
                )
                self.hilos_activos.append(hilo)
                if(self.proxy == "AUTOMATIC"):
                    # Hilo de búsqueda de proxies
                    hilo_proxy = threads.proxyfinder(self.proxies, 
                    self.blacklist_proxies,
                    self.proxy_lock)
                    self.hilos_activos.append(hilo_proxy)

            elif option == "4":
                UIface.endProgram()
                return
            
            elif option == "kill":
                    pid_input = input("Introduce la URL de búsqueda (debe contener '?'): ").strip()
                    if "?" not in url_input:
                        sleep(1)
                        UIface.mostrar_error("La URL de búsqueda no contiene parámetros. Revisa la URL introducida.")
                        continue
            else:
                UIface.mostrar_error("Opción no válida. Por favor, intente de nuevo.")
                sleep(1)
            #UIface.borrarPantalla()
            