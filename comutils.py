#!/usr/bin/env python

def read_from_com(com, crc=True):
    """
    Abre el puerto `com`, lee hasta final de línea y devuelve lo leído.
    """
    # TODO: Testear en real. Este es el código de la báscula de fibra. La de
    # geotextiles creo que no pasa datos para estable ni nada de eso. Solo peso.
    try:
        c = com.readline(eol='\r')
    except TypeError:   # Versión que no soporta especificar fin de línea.
        import io
        sio = io.TextIOWrapper(io.BufferedRWPair(com, com))
        try:
            c = sio.readline()
        except ValueError:  # ¿Puerto cerrado?
            com = utils.get_puerto_serie()
            try:
                sio = io.TextIOWrapper(io.BufferedRWPair(com, com))
                c = sio.readline()
            except UnicodeDecodeError:
                c = ""  # Basurilla. La lectura no es perfecta. Vuelvo a iterar
            except AttributeError:
                # No se ha podido abrir el puerto serie (NoneType not readable)
                c = ""
        except UnicodeDecodeError:
            c = ""  # Ha leído mierda. Vuelvo a iterar.
    if com:
        com.flushInput()    # Evito que datos antiguos se queden en el
        com.flush()         # buffer impidiendo nuevas lecturas.
    # NEW! Redundancia para tolerancia a errores
    if crc and False:   # FIXME: No funciona como esperaba...
        _c = read_from_com(com, crc=False)
        if _c != c:
            estable = 3     # 3 = Peso nulo.
            algo = "ERRSYNC"
            peso_str = 0
            c = "{} {} {}".format(estable, algo, peso_str)
    return c


def recv_serial(puerto):
    """
    Lee y devuelve del puerto recibido.
    """
    # TODO: Aquí tendré que ajustar el código para leer de verdad del puerto.
    # El COM también tiene readline, así que eso no vale para distinguirlo
    # de mi puerto emulado con ficheros.
    try:
        res = puerto.readline()
    except AttributeError:
        res = read_from_com(puerto, crc=False)
    return res

def recv_peso(puerto):
    """
    Devuelve el peso en báscula si es estable. Si no, devuelve None.
    """
    data = recv_serial(puerto)
    try:
        estable, garbage, peso = data.split()
    except ValueError:
        peso = None
    if estable != '0':
        peso = None
    return peso

