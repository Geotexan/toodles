#!/usr/bin/env python

import unittest
import tempfile
import os

from toodles import Toodles

PESOTEST = 543.21

class DummyPort():
    """
    Crea un puerto ficticio con la interfaz del puerto serie
    (io.TextIOWrapper) y el formato de peso que devuelve la báscula real:
    n xxxxxx mmm.mm
    Donde:
    - n: Indica si el peso es estable (0), inestable (2) o nulo (3).
    - xxxxxx: Texto de código de error que se puede ignorar.
    - mmm.mm: Peso (float) mostrado en el display de la báscula.
    """
    def __init__(self, data=None, destroy_on_gc=False):
        self.destroy_on_gc = destroy_on_gc
        self.fakefile = os.path.join(tempfile.gettempdir(), "fakeport.txt")
        self.seek = 0
        if data is None:
            peso = PESOTEST
            data = "{} {} {}".format(0, "XXXXXXX", peso)
        with open(self.fakefile, mode="w") as iostream:
            iostream.write(data)

    def __del__(self):
        if self.destroy_on_gc:
            os.unlink(self.fakefile)

    def write(self, txt):
        with open(self.fakefile, mode="a") as iostream:
            return iostream.write(txt)

    def readline(self):
        with open(self.fakefile, mode="r") as iostream:
            iostream.seek(self.seek)
            line = iostream.readline()
            self.seek += len(line)
        return line


class TestToodles(unittest.TestCase):
    def test_capture(self):
        """
        Comprueba que la lectura devuelve algo.
        """
        toodles = Toodles()
        # Cuando leo de None, devuelve None.
        data = toodles.capture(None)
        self.assertIsNone(data)

    def test_dump(self):
        """
        Comprueba que se escribe el peso en destino.
        """
        toodles = Toodles()
        destino = tempfile.NamedTemporaryFile(mode="w", delete=False)
        peso = "123.45"
        toodles.dump(peso, destino)
        # El método dump cierra el fichero al terminar. Hay que abrir de nuevo.
        # destino.seek(0)
        with open(destino.name) as destino:
            data = destino.readline()
        os.unlink(destino.name)
        pesoleido, fechaleida = data.split()
        self.assertEqual(pesoleido, peso)

    def test_run(self):
        """
        Comprueba una iteración completa de lectura-escritura con cabecera.
        """
        toodles = Toodles()
        destino = tempfile.NamedTemporaryFile(mode="w", delete=False)
        peso = PESOTEST
        puerto = DummyPort(data="0 XXXXXXX {}".format(peso))
        toodles.run(puerto, destino)
        # El método dump cierra el fichero al terminar. Hay que abrir de nuevo.
        # destino.seek(0)
        with open(destino.name) as destino:
            header = destino.readline()
            data = destino.readline()
        os.unlink(destino.name)
        pesoleido, fechahora = data.split()
        self.assertEqual(float(pesoleido), float(peso))



if __name__ == '__main__':
    unittest.main()
