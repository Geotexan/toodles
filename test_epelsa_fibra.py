#!/usr/bin/env python

"""
Programa para testear el nuevo display de EPELSA en la línea de fibra.

El protocolo ha cambiado y la conexión física también. Ahora va por cable serie
pero de DB-15 a DB-9 y un adaptardor RS-232 a USB.
"""

import serial
import time


def main():
    """
    Abre el puerto y envía una petición de peso al display.
    """
    # com = serial.Serial("/dev/ttyUSB0")
    com = serial.Serial("COM3")
    while True:
        # com.write(0x26)
        print(time.asctime(), com.read_all())
        time.sleep(1)


if __name__ == "__main__":
    main()
