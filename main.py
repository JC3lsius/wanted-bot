from Controlador.vinfinder import Vinfinder

if __name__ == "__main__":
    app = Vinfinder()
    app.run()

#   consideraciones
# -------------------
#     Si la lista de articulos encontrados llega a 100, se borran las primeras 50 urls de referencia del listado
# SI  Hacer menu y interfaz al iniciar la busqueda que se interrumpa al introducir comando
#     Deteccion de errores y contador de fallos
#     Cambio de los parametros de busqueda
#     Compatibilidad con terminal de windows y Linux
# SI  Si hay un hilo corriendo (el programa) pedir que se cierre, y opciones de segundo plano
# SI  Control de errores de hilo
# SI  Modelo Vista Controlador

#   recomendaciones
# --------------------
# IMPLEMENTADO Utilizar proxy/VPN para que no te baneen la IP