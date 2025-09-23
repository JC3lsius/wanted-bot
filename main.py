from Controlador.vinfinder import Vinfinder

if __name__ == "__main__":
    app = Vinfinder()
    app.run()


#   FUNCIONAL
# -------------------   
#   SI 

#   consideraciones extra
# -------------------
#     Si la lista de articulos encontrados llega a 100, se borran las primeras 20 urls de referencia del listado
# SI  Hacer menu y interfaz al iniciar la busqueda que se interrumpa al introducir comando
#     Deteccion de errores y contador de fallos
#     Cambio de los parametros de busqueda
#     Compatibilidad con terminal de windows y Linux
#     Si hay un hilo corriendo (el programa) pedir que se cierre, y opciones de segundo plano
# SI  Control de errores de hilo
# SI  Modelo Vista Controlador

#   recomendaciones
# --------------------
# IMPLEMENTADO  Sistema que permita utilizar y buscar proxy para que no baneen por IP
#               Crear una lista dorada de proxies entre las que rote si se sabe que funcionan, y gestionar su validez

# FALTA, SI RECIBO UNA URL, EXTRAER PARAMETROS Y CREAR UNA REQUEST EN CONDICIONES, AÑADIR PARAMETROS SEGUN LA URL A LOS PARAMS
# SE PUEDEN CREAR VARIOS HILOS DE CADA TIPO, PERO LOS HILOS DE PROXY NO SE PUEDEN SOLAPAR AL BUSCAR, QUE TENGAN ACCESOS CONTROLADOS A RECURSOS, IGUAL QUE LOS DE BUSQUEDA