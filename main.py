from Controlador.wanted import Wanted

if __name__ == "__main__":
    app = Wanted()
    app.run()


#   FUNCIONAL
# -------------------   
#   SI 

#   funcionalidades extra
# -------------------
# SI  Imprimir un listado con los archivos .conf existentes y permitir cargar uno
# SI  Hacer menu y interfaz al iniciar la busqueda que se interrumpa al introducir comando
#     Deteccion de errores y contador de fallos
# SI  Cambio de los parametros de busqueda
#     Compatibilidad con terminal de windows y Linux
# SI  Si hay un hilo corriendo (el programa) pedir que se cierre, y opciones de segundo plano
# SI  Control de errores de hilo
# SI  Modelo Vista Controlador
# /-  Añadir funcionalidad para scrapear y hacer llamadas a la API de wallapop, milanuncios y ebay
#     Crear configuraciones de uso de los hilos, siendo unas más eficientes que otras (modo scrapping, modo analisis, modo normal)
# --  NO PROBABLE IMPLEMENTACIÓN Se puede llegar a crear un recomendador de fiabilidad dependiendo de las reviews del usuario, creación de la cuenta, ventas, redes sociales vinculadas y reviews de usuarios

#   recomendaciones
# --------------------
# IMPLEMENTADO  Sistema que permita utilizar y buscar proxy para que no baneen por IP
#               Crear una lista dorada de proxies entre las que rote si se sabe que funcionan, y gestionar su validez

# FALTA, SI RECIBO UNA URL, EXTRAER PARAMETROS Y CREAR UNA REQUEST EN CONDICIONES, AÑADIR PARAMETROS SEGUN LA URL A LOS PARAMS
# SE PUEDEN CREAR VARIOS HILOS DE CADA TIPO, PERO LOS HILOS DE PROXY NO SE PUEDEN SOLAPAR AL BUSCAR, QUE TENGAN ACCESOS CONTROLADOS A RECURSOS, IGUAL QUE LOS DE BUSQUEDA
# CREAR VARIOS HILOS CON DIFERENTES PARÁMETROS, ELEGIR QUE HOJA DE PARÁMETROS CARGAR PARA CADA HILO

# POSIBLE PORTEO A C++ Y ADAPTAR CHROMEDRIVER Y BUSCADOR A RASPIOS

# SI LA CLASE API VA A SER USADA POR DISTINTOS TIPOS DE HILO, COMPROBAR QUE SE PUEDE REALIZAR UNA INSTANCIA PARA CADA HILO CORRECTAMENTE

# METER INTERRUPCIÓN O BORRADO DE HILO POR ENTRADA DE TECLADO
