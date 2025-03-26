#!/usr/bin/env python

import os

EPELSA_FIBRA, EPELSA_GEOTEXTIL = range(2)


def dialogo_info(titulo: str, texto: str, padre=None):
    """
    Reemplaza el `dialogo_info` del GUI por una salida en modo texto,
    ya que este script se ejecutará en consola y no se carga GTK.
    """
    if padre:
        print(f">>>{padre}")
    print(titulo)
    print(texto)


def get_puerto_serie(puerto=None, timeout: float | None = 0.5):
    """
    Devuelve un objeto de pyserial con el
    puerto correspondiente abierto. None
    si no se pudo abrir.
    "puerto" es una cadena con el valor del "dev"
    correspondiente: COM1, COM2, /dev/ttyS0... o None
    para buscar el primer puerto serie disponible.
    """
    try:
        import serial
    except ImportError:
        dialogo_info(
            titulo="ERROR IMPORTACIÓN",
            texto="Debe instalar el módulo pyserial.",
            padre=None,
        )
        return None
    if puerto is None:
        com = buscar_puerto_serie()
    else:
        try:
            com = serial.Serial(puerto)
        except:
            com = None
    if com is not None:  # Configuración protocolo Eurobil. Misma configuración
        # para los Symbol Phaser P360.
        com.baudrate = 9600
        com.bytesize = 8
        com.parity = "N"
        com.stopbits = 1
        com.timeout = timeout
        # com.timeout = 0.5     # El timeout_add es bloqueante.
        # Leeré cada medio segundo.
    return com


def buscar_puerto_serie():
    """
    Devuelve el primer puerto serie encontrado en
    el sistema o None si no se contró.
    """
    try:
        import serial
    except ImportError:
        dialogo_info(
            titulo="ERROR IMPORTACIÓN",
            texto="Debe instalar el módulo pyserial.",
            padre=None,
        )
        return None
    if os.name == "posix":
        try:
            com = serial.Serial("/dev/ttyS0")
        except:
            try:
                com = serial.Serial("/dev/ttyS1")
            except:
                com = None
    else:
        for numpuerto in (1, 2, 6, 5, 3, 4, 7, 8, 9):
            nompuerto = "COM{}".format(numpuerto)
            try:
                com = serial.Serial(nompuerto)
            except:
                com = None  # Y probamos el siguiente
            else:
                break
    return com


def read_from_com(com, crc=True):
    """
    Abre el puerto `com`, lee hasta final de línea y devuelve lo leído.
    """
    # TODO: Testear en real. Este es el código de la báscula de fibra. La de
    # geotextiles creo que no pasa datos para estable ni nada de eso. Solo
    # peso.
    try:
        c = com.readline(eol="\r")
    except TypeError:  # Versión que no soporta especificar fin de línea.
        import io

        sio = io.TextIOWrapper(io.BufferedRWPair(com, com))
        try:
            c = sio.readline()
        except ValueError:  # ¿Puerto cerrado?
            com = get_puerto_serie()
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
        com.flushInput()  # Evito que datos antiguos se queden en el
        com.flush()  # buffer impidiendo nuevas lecturas.
    # NEW! Redundancia para tolerancia a errores
    if crc and False:  # FIXME: No funciona como esperaba...
        _c = read_from_com(com, crc=False)
        if _c != c:
            estable = 3  # 3 = Peso nulo.
            algo = "ERRSYNC"
            peso_str = 0
            c = "{} {} {}".format(estable, algo, peso_str)
    return c


def recv_serial(puerto, protocolo=EPELSA_FIBRA):
    """
    Lee y devuelve del puerto recibido.
    """
    # El COM también tiene readline, así que eso no vale para distinguirlo
    # de mi puerto emulado con ficheros.
    if protocolo == EPELSA_FIBRA:
        try:
            res = puerto.read_until(expected=b"\r")
        except AttributeError:
            res = read_from_com(puerto, crc=False)
    elif protocolo == EPELSA_GEOTEXTIL:
        print("Leyendo EPELSA GEOTEXTIL...")
        try:
            res = puerto.read_until(
                expected=b"\r"
            )  # Bloqueante porque timeot None arriba
            # res = puerto.readline()
            print(">>>>>>>>>>> {}".format(res))
        except AttributeError:
            res = read_from_com(puerto, crc=False)
            print(">>>!!!!!!!>>>>>>>> {}".format(res))
    else:
        res = None
    return res


def recv_peso(puerto, protocol=EPELSA_FIBRA):
    """
    Devuelve el peso en báscula si es estable. Si no, devuelve None.
    """
    if isinstance(puerto, str):
        if protocol == EPELSA_GEOTEXTIL:
            timeout = None
        elif protocol == EPELSA_FIBRA:
            timeout = 0.5
        else:
            timeout = None
        puerto = get_puerto_serie(puerto, timeout)
    if protocol == EPELSA_FIBRA:
        peso = recv_peso_fibra(puerto)
    elif protocol == EPELSA_GEOTEXTIL:
        peso = recv_peso_geotextil(puerto)
    else:
        peso = None
    return peso


def recv_peso_fibra(puerto):
    """
    Lee el peso del puerto serie según el protocolo de la báscula EPELSA de la
    línea de fibra.
    """
    data = recv_serial(puerto, EPELSA_FIBRA)
    try:
        estable, garbage, peso = data.split()
        try:
            peso = float(peso)
        except ValueError:
            peso = None
    except ValueError:
        peso = None
        estable = None
    if estable != b"2":  # Fibra: 0=inestable, 2=estable, 3=nulo
        peso = None
    return peso


def recv_peso_geotextil(puerto):
    """
    Lee el peso del puerto serie según el protocolo de la báscula EPELSA de la
    línea de geotextiles.
    """
    data = recv_serial(puerto, EPELSA_GEOTEXTIL)
    try:

        peso = float(data.decode("utf8").split()[0].replace(",", "."))
    except (ValueError, TypeError, AttributeError):
        peso = None
    return peso
