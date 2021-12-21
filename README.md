Toodles
=======

[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)

![Toodles (Creative Commons)](https://gcdn.pbrd.co/images/htlcGDYd9lYy.png?o=1)



Para facilitar la integración de las básculas con SAP+BEAS, este
toma de un fichero de texto el valor de la pesada. Este programita lo único que
hace es leer el valor del peso de la báscula mediante el puerto serie cada
cierto tiempo y escribirlo en un fichero de texto compartido por Samba.

## Instalación

> Requiere [PDM](https://pdm.fming.dev/)

```
git clone git@github.com:Geotexan/toodles.git
cd toodles
pdm install
```

## Dependencias

Todas se instalan automáticamente con `pdm install`:
- fire
- python-serial


## Uso

```
python toodles.py --help
```

---

Imagen con [licencia CC](https://creativecommons.org/licenses/by-nd/2.0/). Autor original: https://www.flickr.com/photos/lorenjavier/3492694257
