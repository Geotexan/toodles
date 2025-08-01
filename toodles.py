#!/usr/bin/env python

"""
Toodles
=======

Lee el peso de la báscula por puerto serie y la escribe en un fichero.
"""

import sys
import logging
import fire

# import serial
import signal
import time
import datetime

# import io
import contextlib
from comutils import recv_peso, EPELSA_FIBRA, EPELSA_GEOTEXTIL

DEBUG = False

logging.basicConfig(filename="toodles.log", level=logging.DEBUG)


@contextlib.contextmanager
def smart_open(filename=None):
    if (
        filename
        and filename is not sys.stdout
        and filename != "-"
        and not hasattr(filename, "write")
    ):
        fh = open(filename, "w")
    else:
        fh = filename
    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()


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
        self.HEADER = "Peso\tFechaHora\n"
        self.origen = origen
        self.destino = destino
        if DEBUG:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.ERROR)
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout

    def _activate_debug(self, flag=True):
        """
        Pone el flag de depuración activo y ejecuta Toodles en modo demonio con
        los valores por defecto.
        :param flag: Si off o no se especifica este comando, desactiva la
                     depuración (valor por defecto: True).
        """
        try:
            flagdebug = flag.upper() in ("ON", "TRUE", "1")
        except AttributeError:  # No es cadena.
            if isinstance(flag, bool):
                flagdebug = flag
            else:
                flagdebug = False
        DEBUG = flagdebug
        # Y como no sé en Fire consumir flags tras --
        if DEBUG:
            print("DEBUG {}".format(DEBUG))
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.ERROR)
        self.daemon()

    def _signal_handler(self, sig, frame):
        """
        Captura la interrupción Ctr+C y sale _gracefully_.
        """
        self.logger.info("Se presionó Ctrl+C.")
        try:
            self.destino.flush()
            self.destino.close()
        except AttributeError:  # self.destino es str y ya está cerrado
            pass
        sys.exit(0)

    def capture(self, puerto=None, protocol=None):
        """
        Abre el puerto serie y captura el peso actual en la báscula.
        :param puerto: puerto serie del que leerá
        :param protocol: protocolo fibra (0) o geotextil (1).
        :return: peso
        """
        try:
            assert protocol in (EPELSA_FIBRA, EPELSA_GEOTEXTIL)
        except AssertionError:
            print("capture: protocol debe ser 0 (fibra) o 1 (geotextil).")
            sys.exit(1)
        if not protocol:
            protocol = EPELSA_FIBRA
        if puerto:
            self.origen = puerto
        self.logger.info(f"Leyendo del puerto {puerto}...")
        if puerto:  # Si el puerto no está definido, devuelvo None.
            res = recv_peso(puerto, protocol)
        else:
            res = None
        self.logger.info(f"Peso leído: {res}")
        return res

    def dump(self, peso=None, destino=None, fechahora=None):
        """
        Escribe el peso recibido en el destino especificado.
        :param peso: Peso a volcar.
        :param destino: Destino donde escribir el volcado.
        """
        if not fechahora:
            fechahora = datetime.datetime.now()
        if destino:
            self.destino = destino
        self.logger.info("Abriendo destino: {}".format(self.destino))
        with smart_open(self.destino) as iostream:
            strahora = fechahora.strftime("%Y%m%d%H%M")
            self.logger.info(f"Escribiendo {peso} ({strahora}) en {destino}...")
            strpeso = str(peso)
            self._write_header(iostream)
            iostream.write("{}\t{}".format(strpeso, strahora))
            iostream.flush()
            self.logger.info("EOW")

    def _write_header(self, iostream):
        """
        Escribe la cabecera que espera leer SAP en el destino.
        Prerrequisitos: destino debe aceptar la interfaz de _file_ y estar
        abierto para escritura.
        """
        iostream.write(self.HEADER)
        iostream.flush()

    def run(self, puerto=None, destino=None, protocol=EPELSA_FIBRA):
        """
        Captura el peso y lo escribe en la salida. Hace una única iteración.
        :param puerto: Puerto del que leer (por ejemplo: COM1 o /dev/ttyS0)
        :param destino: Destino donde escribir el volcado (ej.: out.txt)
        """
        if destino:
            self.destino = destino
        if not self.destino:
            self.destino = sys.stdout
        self.logger.info(f"Capturando de {puerto} y volcando a {destino}...")
        peso = self.capture(puerto, protocol)
        if peso:
            self.logger.info(f"Peso capturado: {peso}.")
            self.dump(peso, self.destino)
            self.logger.info(f"Peso {peso} volcado a {destino}.")
        else:
            self.logger.warning(f"Peso nulo. No se escribe a {destino}.")

    def daemon(self, timeout=5, puerto=None, destino=None, protocol=EPELSA_FIBRA):
        """
        Ejecuta el programa indefinidamente leyendo el peso de la báscula cada
        `timeout` segundos.
        :param timeout: Segundos entre lecturas. Por defecto, 5.
        :param puerto: Puerto del que leer (por ejemplo: COM1 o /dev/ttyS0)
        :param destino: Destino donde escribir el volcado (por ejemplo: out.txt)
        """
        if timeout is not None:
            self.timeout = timeout
        signal.signal(signal.SIGINT, self._signal_handler)
        print("Presiona Ctrl+C para terminar.")
        while True:
            self.run(puerto, destino, protocol)
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
    fire.Fire(
        {
            "capture": toodles.capture,
            "dump": toodles.dump,
            "run": toodles.run,
            "daemon": toodles.daemon,
            "debug": toodles._activate_debug,
        }
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
