from models.Models import *

class scraper(object):

  def getResponseInfo(self, m, res):
    self.home_id, self.away_id = self.getTeamsIds(res)
    self.__data = {
      "home_id": self.home_id,
      "away_id": self.away_id,
      "date": m["date"],
      "home": m["home"],
      "away": m["away"],
    }
    
    M = Match.create(team_home_id=self.home_id, team_away_id=self.away_id, team_home=m["home"], team_away=m["away"], date=m["date"])
    M.save()

    self.addPenalty(M, res)
    self.addSubstitutions(M, res)
    self.addYellowCards(M, res)
    self.addGoalsAgainst(M, res)
    self.addGoals(M, res)

    print (self.__data)
    return self.__data

  def getPeriodo(self, res, column, index):
    return 45 if str(res["placar"]["eventos"][column][index]["id-periodo"]) == '2' else 0

  def getTeamsIds(self, res):
    return res["placar"]["equipes"]["e1"][0]["id"], res["placar"]["equipes"]["e2"][0]["id"]

  def getPositionById(self, res, pid):
    for k, v in res["placar"]["escalacao"]["jogadores-geral"].items():
      print("{} = {}".format(k, v["posicao"]))

  def getMinuto(self, res, index, column):
    minuto = 0
    if (res["placar"]["eventos"][column][index]["minuto"] != ''):
      minuto = int(res["placar"]["eventos"][column][index]["minuto"]) + self.getPeriodo(res, column, index)
    return minuto

  def addSubstitutions(self, M, res):
    for i in range(len(res["placar"]["eventos"]["substituicoes"])):
      if (str(res["placar"]["eventos"]["substituicoes"][i]["periodo"]) == 'intervalo-de-jogo'):
        self.__data["substitution_{}_time".format(i)] = 'INTERVALO'
      else:
        self.__data["substitution_{}_time".format(i)] = str(self.getMinuto(res, i, "substituicoes"))
      self.__data["substitution_{}_team_id".format(i)] = res["placar"]["eventos"]["substituicoes"][i]["id-equipe"]
      
      # Incluir hiperparâmetro relacionado aos scouts do jogador

      s = Substitution.create(time=self.__data["substitution_{}_time".format(i)])
      s.save()
      MatchSubstitution.create(match=M, substitution=s).save()

  def addPenalty(self, M, res):
    for i in range(len(res["placar"]["eventos"]["penaltis"])):
      self.__data["penalty_{}_time".format(i)] = str(self.getMinuto(res, i, "penaltis"))
      self.__data["penalty_{}_team_id".format(i)] = res["placar"]["eventos"]["penaltis"][i]["id-equipe"]
      p = Penalty.create(time=self.__data["penalty_{}_time".format(i)])
      p.save()
      MatchPenalty.create(match=M, penalty=p).save()

  def addYellowCards(self, M, res):
    for i in range(len(res["placar"]["eventos"]["cartoes-amarelos"])):
      self.__data["yellowcard_{}_time".format(i)] = str(self.getMinuto(res, i, "cartoes-amarelos"))
      self.__data["yellowcard_{}_team_id".format(i)] = res["placar"]["eventos"]["cartoes-amarelos"][i]["id-equipe"]
      self.__data["yellowcard_{}_player_id".format(i)] = res["placar"]["eventos"]["cartoes-amarelos"][i]["id-jogador"]
      y = YellowCard.create(time=self.__data["yellowcard_{}_time".format(i)], player_id=self.__data["yellowcard_{}_player_id".format(i)])
      y.save()
      MatchYcard.create(match=M, y_card=y).save()

  def addRedCards(self, M, res):
    for i in range(len(res["placar"]["eventos"]["cartoes-vermelhos"])):
      self.__data["redcard_{}_time".format(i)] = str(self.getMinuto(res, i, "cartoes-vermelhos"))
      self.__data["redcard_{}_team_id".format(i)] = res["placar"]["eventos"]["cartoes-vermelhos"][i]["id-equipe"]
      self.__data["redcard_{}_player_id".format(i)] = res["placar"]["eventos"]["cartoes-vermelhos"][i]["id-jogador"]
      r = RedCard.create(time=self.__data["redcard_{}_time".format(i)], player_id=self.__data["redcard_{}_player_id".format(i)])
      r.save()
      MatchRcard.create(match=M, r_card=r).save()

  def addGoalsAgainst(self, M, res):
    for i in range(len(res["placar"]["eventos"]["gols-contra"])):
      self.__data["goal_against_{}_time".format(i)] = str(self.getMinuto(res, i, "gols-contra"))
      self.__data["goal_against_{}_team_id".format(i)] = res["placar"]["eventos"]["gols-contra"][i]["id-equipe"]
      self.__data["goal_against_{}_player_id".format(i)] = res["placar"]["eventos"]["gols-contra"][i]["id-jogador"]
      ga = GoalsAgainst.create(time=self.__data["goal_against_{}_time".format(i)], player_id=self.__data["goal_against_{}_player_id".format(i)])
      ga.save()
      MatchAgainstGoal.create(match=M, against_goal=ga).save()

  def addGoals(self, M, res):
    for i in range(len(res["placar"]["eventos"]["gols"])):
      self.__data["goal_{}_time".format(i)] = str(self.getMinuto(res, i, "gols"))
      self.__data["goal_{}_team_id".format(i)] = res["placar"]["eventos"]["gols"][i]["id-equipe"]
      self.__data["goal_{}_player_id".format(i)] = res["placar"]["eventos"]["gols"][i]["id-jogador"]
      g = Goal.create(time=self.__data["goal_{}_time".format(i)], player_id=self.__data["goal_{}_player_id".format(i)])
      g.save()
      MatchGoal.create(match=M, goal=g).save()
