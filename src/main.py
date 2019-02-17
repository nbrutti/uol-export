from services.matchesParamsPrepare import *
from config.defs import *

from multiprocessing.dummy import Pool as ThreadPool
import requests

matchesDataset = matchesParamsPrepare()
i = 0

def fetch_url(m):
  global i
  r = requests.get(BASE_URL.format(m["home"], m["away"], m["date"]))
  print (r.status_code, i, m["home"], m["away"], m["date"])
  i = i + 1

if __name__ == "__main__":
  pool = ThreadPool(processes=16)
  results = pool.map(fetch_url, matchesDataset.matches)
  pool.close()
  pool.join()
