# Força do time
# Criação do atributo relacionado a força do time. Este atributo será criado com base no artigo de Rajitha Silva e Tim Swartz. 
# Disponível em: http://people.stat.sfu.ca/~tim/papers/substitution.pdf

import json


# Importação do dataset
file_src = 'output/br-league.json'

class TeamStrength(object):
  def __init__(self):
    with open(file_src) as f:
      self._dict = json.load(f)

  def getTotalAwayGoals(self, team, season):
    count = 0
    for d in self._dict:
      if (d["away"] == team):
        count = [(g["team"] == team) and (season == d["date"][:4]) for g in d["goals"]].count(True)
    return count

  def getTotalHomeGoals(self, team, season):
    count = 0
    for d in self._dict:
      if (d["home"] == team):
        count += [(g["team"] == team) and (season == d["date"][:4]) for g in d["goals"]].count(True)
    return count

  '''def goals_scored_by(self, team):
    count = 0
    for d in self._dict:
      count += [g["team"] == team for g in d["goals"]].count(True)
    return count'''

  '''def goals_allowed(self, team):
    count = 0
    for d in self._dict:
      if (d["away"] == team or d["home"] == team):
        count += [g["team"] != team for g in d["goals"]].count(True)
    return count'''

  def getTotalMatches(self, team, season):
    return [(d["home"] == team or d["away"] == team) and (season == d["date"][:4]) for d in self._dict].count(True)

  def getTotalGoalsAllowed(self, team, season):
    count = 0
    for d in self._dict:
      if (d["away"] == team and d["date"][:4] == season):
        count += [g["team"] != team for g in d["goals"]].count(True)
    return count

  def getTotalGoalsAllowedd(self, team):
    count = 0
    for d in self._dict:
      if (d["away"] == team):
        count += [g["team"] != team for g in d["goals"]].count(True)
    return count

  def getTotalGoalsScoredd(self, team):
    count = 0
    for d in self._dict:
      if (d["away"] == team):
        count += [g["team"] == team for g in d["goals"]].count(True)
    return count

  def getTotalGoalsScored(self, team, season):
    count = 0
    for d in self._dict:
      if (d["away"] == team and d["date"][:4] == season):
        count += [g["team"] == team for g in d["goals"]].count(True)
    return count

  def buildFVO(self, team):
    total_matches = [(d["home"] == team or d["away"] == team) for d in self._dict].count(True)
    total_goals_scored = self.getTotalGoalsScoredd(team)
    return total_goals_scored / total_matches

  def buildFVD(self, team):
    total_matches = [(d["home"] == team or d["away"] == team) for d in self._dict].count(True)
    total_goals_allowed = self.getTotalGoalsAllowedd(team)
    return total_goals_allowed / total_matches

  def getHTA(self, date):
    total_home_goals = 0
    total_away_goals = 0
    total_matches = 0

    for d in self._dict:
      if (d["date"][:4] == date):
        for g in d["goals"]:
          if (g["team"] == d["home"]):
            total_home_goals += 1

    for d in self._dict:
      if (d["date"][:4] == date):
        for g in d["goals"]:
          if (g["team"] == d["away"]):
            total_away_goals += 1

    for d in self._dict:
      total_matches += 1

    return (total_home_goals - total_away_goals) / total_matches

  def buildD(self, team, season):
    scored = self.getTotalGoalsScored(team, season)
    allowed = self.getTotalGoalsAllowed(team, season)
    total_matches = self.getTotalMatches(team, season)

    return (scored - allowed) / total_matches

  def buildParam(self, team_home, season):
    total_matches = self.getTotalMatches(team_home, season)
    total_home_goals = self.getTotalHomeGoals(team_home, season)
    total_away_goals = self.getTotalAwayGoals(team_home, season)
    HTA = (total_home_goals - total_away_goals) / total_matches
    return round(HTA, 2)