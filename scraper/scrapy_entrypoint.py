# 1) Instala un reactor compatible (selectreactor o asyncioreactor)
from twisted.internet import selectreactor
selectreactor.install()

# 2) Monkey-parchea install_shutdown_handlers para que sea un no-op
import scrapy.utils.ossignal
scrapy.utils.ossignal.install_shutdown_handlers = lambda *args, **kwargs: None

# 3) Arranca Scrapy normalmente, pasando todos los args
from scrapy.cmdline import execute
import sys

if __name__ == "__main__":
    # sys.argv example: ["scrapy_entrypoint.py", "crawl", "pubmed", "-a", "query=...", "-a", "max_results=2"]
    execute(sys.argv)
