#!/usr/bin/env python

"""
Toodles
=======

Lee el peso de la báscula por puerto serie y la escribe en un fichero.
"""

import sys
import logging
import fire
import serial
import signal
import time

DEBUG=True

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def capture(puerto=None):
    """
    Abre el puerto serie y captura el peso actual en la báscula.
    :param puerto: puerto serie del que leerá
    :return: peso
    """
    logger.info(f"Leyendo del puerto {puerto}...")
    res = None
    logger.info(f"Peso leído: {res}")
    return res


def dump(peso=None, destino=None):
    """
    Escribe el peso recibido en el destino especificado.
    :param peso: Peso a volcar.
    :param destino: Destino donde escribir el volcado.
    """
    logging.info(f"Escribiendo {peso} en {destino}...")
    destino.write(str(peso))
    logging.info("EOW")


def run(puerto=None, destino=None):
    """
    Captura el peso y lo escribe en la salida.
    :param puerto: Puerto del que leer (por ejemplo: COM1 o /dev/ttyS0)
    :param destino: Destino donde escribir el volcado (por ejemplo: out.txt)
    """
    if not destino:
        destino = sys.stdout
    logging.info(f"Capturando de {puerto} y volcando a {destino}...")
    dump(capture(puerto), destino)


def signal_handler(sig, frame):
    """
    Captura la interrupción Ctr+C y sale _gracefully_.
    """
    logging.info("Se presionó Ctrl+C.")
    sys.exit(0)


def daemon(timeout=5, puerto=None, destino=None):
    """
    Ejecuta el programa indefinidamente leyendo el peso de la báscula cada
    `timeout` segundos.
    :param timeout: Segundos entre lecturas. Por defecto, 5.
    :param puerto: Puerto del que leer (por ejemplo: COM1 o /dev/ttyS0)
    :param destino: Destino donde escribir el volcado (por ejemplo: out.txt)
    """
    signal.signal(signal.SIGINT, signal_handler)
    print("Presiona Ctrl+C para terminar.")
    while True:
         run(puerto, destino)
         time.sleep(timeout)

def main():
    """
    Rutina principal.
    """
    # TODO:
    # - `-p (COMn|/dev/ttySn`: Indicar el puerto serie donde leerá los datos.
    # - `-w nombre_fichero.txt`: Fichero al que escribirá los datos. Si se omite,
    #                            escribe en la salida estándar.
    # - `-t n`: Número de segundos entre lecturas. Si se omite, 5 segundos.
    # - `-o (stdout|file|http|ftp|smb)`: EXPERIMENTAL. Salida de los datos por fichero,
    #                             web, ftp o samba. Por defecto, a fichero.
    fire.Fire({
        "capture": capture,
        "dump": dump,
        "run": run,
        "daemon": daemon
        })
    sys.exit(0)

if __name__ == "__main__":
    main()
