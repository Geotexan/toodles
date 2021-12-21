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

class Toodles:
    """
    Encapsula toda la funcionalidad del script.
    """
    def __init__(self, origen=None, destino=None, timeout=5):
        """
        Constructor.
        :param origen: Origen de los datos (puerto serie de la báscula).
        :param destino: Destino donde volcar los pesos leídos.
        :param timeout: Tiempo entre lecturas en modo _daemon_.
        """
        self.origen = origen
        self.destino = destino
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout

    def signal_handler(self, sig, frame):
        """
        Captura la interrupción Ctr+C y sale _gracefully_.
        """
        self.logger.info("Se presionó Ctrl+C.")
        self.destino.flush()
        self.destino.close()
        sys.exit(0)


    def capture(self, puerto=None):
        """
        Abre el puerto serie y captura el peso actual en la báscula.
        :param puerto: puerto serie del que leerá
        :return: peso
        """
        self.origen = puerto
        self.logger.info(f"Leyendo del puerto {puerto}...")
        res = None
        self.logger.info(f"Peso leído: {res}")
        return res


    def dump(self, peso=None, destino=None):
        """
        Escribe el peso recibido en el destino especificado.
        :param peso: Peso a volcar.
        :param destino: Destino donde escribir el volcado.
        """
        self.destino = destino
        self.logger.info(f"Escribiendo {peso} en {destino}...")
        self.destino.write(str(peso))
        self.logger.info("EOW")


    def run(self, puerto=None, destino=None):
        """
        Captura el peso y lo escribe en la salida.
        :param puerto: Puerto del que leer (por ejemplo: COM1 o /dev/ttyS0)
        :param destino: Destino donde escribir el volcado (por ejemplo: out.txt)
        """
        self.destino = destino
        if not self.destino:
            self.destino = sys.stdout
        self.logger.info(f"Capturando de {puerto} y volcando a {destino}...")
        self.dump(self.capture(puerto), self.destino)


    def daemon(self, timeout=5, puerto=None, destino=None):
        """
        Ejecuta el programa indefinidamente leyendo el peso de la báscula cada
        `timeout` segundos.
        :param timeout: Segundos entre lecturas. Por defecto, 5.
        :param puerto: Puerto del que leer (por ejemplo: COM1 o /dev/ttyS0)
        :param destino: Destino donde escribir el volcado (por ejemplo: out.txt)
        """
        self.timeout = timeout
        signal.signal(signal.SIGINT, self.signal_handler)
        print("Presiona Ctrl+C para terminar.")
        while True:
             self.run(puerto, destino)
             time.sleep(self.timeout)

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
    toodles = Toodles()
    fire.Fire({
        "capture": toodles.capture,
        "dump": toodles.dump,
        "run": toodles.run,
        "daemon": toodles.daemon
        })
    sys.exit(0)

if __name__ == "__main__":
    main()
