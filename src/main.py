import requests
import logging
import json

from hyperparameters.TeamStrength import TeamStrength
from services.matchesParamsPrepare import *
from config.defs import *
from scraper import *

from multiprocessing.dummy import Pool as ThreadPool

logging.basicConfig(filename='logs.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

matchesDataset = matchesParamsPrepare()
output = []

def addTeamStrength():
  global output
  for m in output:
    m["away_team_strength"] = TeamStrength().buildParam(m["away"], m["date"][:4])
    m["home_team_strength"] = TeamStrength().buildParam(m["home"], m["date"][:4])
    m["FVO"] = TeamStrength().buildFVO(m["away"])
    m["FVD"] = TeamStrength().buildFVD(m["away"])
    m["FCO"] = TeamStrength().buildFVO(m["home"])
    m["FCD"] = TeamStrength().buildFVD(m["home"])

def exportToJson():
  global output
  with open('output/br-league.json', 'w+') as f:
    json.dump(output, f, indent=2, sort_keys=True, ensure_ascii=False)

def fetch_url(m):
  global output
  res = requests.get(BASE_URL.format(m["home"], m["away"], m["date"]))
  try:
    output.append(scraper().getResponseInfo(m, res.json()))
  except:
    logging.debug('Erro ao consultar os dados da partida: {} x {} ocorrida em {}'.format(m["home"], m["away"], m["date"]))

if __name__ == "__main__":
  pool = ThreadPool(processes=4)
  results = pool.map(fetch_url, matchesDataset.matches)
  pool.close()
  pool.join()

exportToJson()
addTeamStrength()
exportToJson()