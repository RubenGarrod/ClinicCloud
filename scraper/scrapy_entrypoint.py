# -*- coding: utf-8 -*-
"""
Script de configuracion para evitar problemas de compatibilidad entre Scrapy y Twisted
en el contenedor Docker.
"""
#reactor compatible (selectreactor)
from twisted.internet import selectreactor
selectreactor.install()

#Monkey-parchea install_shutdown_handlers para que sea un no-op
import scrapy.utils.ossignal
scrapy.utils.ossignal.install_shutdown_handlers = lambda *args, **kwargs: None

#Arranca Scrapy normalmente, pasando todos los args
from scrapy.cmdline import execute
import sys

if __name__ == "__main__":
    # sys.argv example: ["scrapy_entrypoint.py", "crawl", "pubmed", "-a", "query=...", "-a", "max_results=2"]
    execute(sys.argv)
