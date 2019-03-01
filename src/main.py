import requests
import logging

from services.matchesParamsPrepare import *
from config.defs import *
from scraper import *

from multiprocessing.dummy import Pool as ThreadPool

logging.basicConfig(filename='logs.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

matchesDataset = matchesParamsPrepare()
output = []

def fetch_url(m):
  global output
  res = requests.get(BASE_URL.format(m["home"], m["away"], m["date"]))
  output.append(scraper().getResponseInfo(m, res.json()))

if __name__ == "__main__":
  pool = ThreadPool(processes=8)
  results = pool.map(fetch_url, matchesDataset.matches)
  pool.close()
  pool.join()

print (output)
