from config.defs import *
import csv

class matchesParamsPrepare(object):
  '''
    Extract the parameters from the .csv file to apply to BASE_URL
    @see config.defs.py
  '''

  def __init__(self):
    self.matches = []
    self.readFile()

  def _teamConverter(self, team):
    return team.replace(' ', '-').lower()

  def _dateConverter(self, date):
    d = date.split('/')
    return "20{}{}{}".format(d[2], d[1], d[0])

  def readFile(self):
    with open(CSV_FILE) as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
        match = {}
        match["home"] = self._teamConverter(row["Home"])
        match["away"] = self._teamConverter(row["Away"])
        match["date"] = self._dateConverter(row["Date"])
        self.matches.append(match)

        