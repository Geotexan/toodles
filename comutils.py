#!/usr/bin/env python

def get_puerto_serie(puerto = None):
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
        dialogo_info(titulo = "ERROR IMPORTACIÓN",
                     texto = "Debe instalar el módulo pyserial.",
                     padre = None)
        return None
    if puerto == None:
        com = buscar_puerto_serie()
    else:
        try:
            com = serial.Serial(puerto)
        except:
            com = None
    if com != None:     # Configuración protocolo Eurobil. Misma configuración
                        # para los Symbol Phaser P360.
        com.baudrate = 9600
        com.bytesize = 8
        com.parity = 'N'
        com.stopbits = 1
        com.timeout = None
        com.timeout = 0.5     # El timeout_add es bloqueante. Leeré cada medio segundo.
    return com

def buscar_puerto_serie():
    """
    Devuelve el primer puerto serie encontrado en
    el sistema o None si no se contró.
    """
    try:
        import serial
    except ImportError:
        dialogo_info(titulo = "ERROR IMPORTACIÓN",
                     texto = "Debe instalar el módulo pyserial.",
                     padre = None)
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

def leer_raw_data(puerto = "COM1", timeout = 30):
    """
    Abre el puerto serie y recibe "en crudo" todos los datos
    almacenados en el terminal.
    Devuelve una lista con los códigos leídos.
    """
    raw_data = []
    com = get_puerto_serie(puerto)
    if com != None:
        com.timeout = timeout
        raw_data = com.readlines()
        # El P360 manda los códigos separados por \r\n, pero para ello hay que configurarlo:
        # F* -> Resetea el terminal.
        # Cuando aún está mostrando el mensaje de inicio (antes de que aparezca "scan") pulsar F y a continuación BK.
        # En el menú "0: System setup" -> "5: Set scan options" -> "3. DATA SUFFIX".
        # En el mismo submenú: "6. Edit Suffix Code" (por defecto 7013 = \r\n).
    return raw_data

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
        # res = puerto.readline()
        res = puerto.read_until(expected=b'\r')
    except AttributeError:
        res = read_from_com(puerto, crc=False)
    return res

def recv_peso(puerto):
    """
    Devuelve el peso en báscula si es estable. Si no, devuelve None.
    """
    if isinstance(puerto, str):
        puerto = get_puerto_serie(puerto)
    data = recv_serial(puerto)
    try:
        estable, garbage, peso = data.split()
        try:
            peso = float(peso)
        except ValueError:
            peso = None
    except ValueError:
        peso = None
        estable = None
    if estable != b'2':  # Fibra: 0=inestable, 2=estable, 3=nulo
        peso = None
    return peso

