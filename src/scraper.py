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
    self.addPenalty(res)
    self.addSubstitutions(res)
    self.addYellowCards(res)
    self.addGoalsAgainst(res)
    self.addGoals(res)
    print (self.__data)
    return None

  def getPeriodo(self, res, column, index):
    return 45 if res["placar"]["eventos"][column][index]["id-periodo"] == '2' else 0

  def getTeamsIds(self, res):
    return res["placar"]["equipes"]["e1"][0]["id"], res["placar"]["equipes"]["e2"][0]["id"]

  def getPositionById(self, res, pid):
    for k, v in res["placar"]["escalacao"]["jogadores-geral"].items():
      print("{} = {}".format(k, v["posicao"]))

  def getSubsType(self, res, subs):
    '''
      O => Ofensive
      N => Neutral
      D => Defensive
    '''
    so_position = self.getPositionById(res, subs["id-jogador"])
    si_position = self.getPositionById(res, subs["id-jogador-substituto"])
    return None

  def addSubstitutions(self, res):
    for i in range(len(res["placar"]["eventos"]["substituicoes"])):
      self.__data["substitution_{}_time".format(i)] = str(int(res["placar"]["eventos"]["substituicoes"][i]["minuto"]) + self.getPeriodo(res, 'substituicoes', i))
      self.__data["substitution_{}_team_id".format(i)] = res["placar"]["eventos"]["substituicoes"][i]["id-equipe"]
      self.__data["substitution_{}_type".format(i)] = self.getSubsType(res, res["placar"]["eventos"]["substituicoes"][i])

  def addPenalty(self, res):
    for i in range(len(res["placar"]["eventos"]["penaltis"])):
      self.__data["penalty_{}_time".format(i)] = str(int(res["placar"]["eventos"]["penaltis"][i]["minuto"]) + self.getPeriodo(res, 'penaltis', i))
      self.__data["penalty_{}_team_id".format(i)] = res["placar"]["eventos"]["penaltis"][i]["id-equipe"]

  def addYellowCards(self, res):
    for i in range(len(res["placar"]["eventos"]["cartoes-amarelos"])):
      self.__data["yellowcard_{}_time".format(i)] = str(int(res["placar"]["eventos"]["cartoes-amarelos"][i]["minuto"]) + self.getPeriodo(res, 'cartoes-amarelos', i))
      self.__data["yellowcard_{}_team_id".format(i)] = res["placar"]["eventos"]["cartoes-amarelos"][i]["id-equipe"]
      self.__data["yellowcard_{}_player_id".format(i)] = res["placar"]["eventos"]["cartoes-amarelos"][i]["id-jogador"]

  def addRedCards(self, res):
    for i in range(len(res["placar"]["eventos"]["cartoes-vermelhos"])):
      self.__data["redcard_{}_time".format(i)] = str(int(res["placar"]["eventos"]["cartoes-vermelhos"][i]["minuto"]) + self.getPeriodo(res, 'cartoes-vermelhos', i))
      self.__data["redcard_{}_team_id".format(i)] = res["placar"]["eventos"]["cartoes-vermelhos"][i]["id-equipe"]
      self.__data["redcard_{}_player_id".format(i)] = res["placar"]["eventos"]["cartoes-vermelhos"][i]["id-jogador"]

  def addGoalsAgainst(self, res):
    for i in range(len(res["placar"]["eventos"]["gols-contra"])):
      self.__data["goal_against_{}_time".format(i)] = str(int(res["placar"]["eventos"]["gols-contra"][i]["minuto"]) + self.getPeriodo(res, 'gols-contra', i))
      self.__data["goal_against_{}_team_id".format(i)] = res["placar"]["eventos"]["gols-contra"][i]["id-equipe"]
      self.__data["goal_against_{}_player_id".format(i)] = res["placar"]["eventos"]["gols-contra"][i]["id-jogador"]

  def addGoals(self, res):
    for i in range(len(res["placar"]["eventos"]["gols"])):
      self.__data["goal_{}_time".format(i)] = str(int(res["placar"]["eventos"]["gols"][i]["minuto"]) + self.getPeriodo(res, 'gols', i))
      self.__data["goal_{}_team_id".format(i)] = res["placar"]["eventos"]["gols"][i]["id-equipe"]
      self.__data["goal_{}_player_id".format(i)] = res["placar"]["eventos"]["gols"][i]["id-jogador"]