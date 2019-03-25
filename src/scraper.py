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

  def getPlayerPosById(self, res, pid):
    for id in res["placar"]["escalacao"]["jogadores-geral"]:
      if (id == pid):
        return res["placar"]["escalacao"]["jogadores-geral"][id]["posicao"]
    return None

  def getSubTactialType(self, res, substitution):
    player_in_pos = self.getPlayerPosById(res, substitution["id_player_in"])
    player_out_pos = self.getPlayerPosById(res, substitution["id_player_out"])
    if (player_in_pos is None or player_out_pos is None):
      raise("Não foi possível extrair as posições do jogador")
      return
    if (player_in_pos == player_out_pos):
      return "NA"
    elif (player_in_pos in ['Meia', 'Meia-atacante', 'Atacante']):
      if (player_out_pos in ['Lateral-direito', 'Zagueiro', 'Lateral-esquerdo', 'Volante']):
        return "OFF"
      elif (player_out_pos in ['Atacante']):
        if (player_in_pos not in ['Atacante', 'Meia-atacante']):
          return "DEF"
      else:
        return "NA"
    else:
      return "DEF"

  def addSubstitutions(self, M, res):
    self.__data["substitutions"] = []
    
    for i in range(len(res["placar"]["eventos"]["substituicoes"])):
      substitution = {}
      if (str(res["placar"]["eventos"]["substituicoes"][i]["periodo"]) == 'intervalo-de-jogo'):
        substitution["time"] = 'INTERVALO'
      else:
        substitution["time"] = str(self.getMinuto(res, i, "substituicoes"))
      substitution["team_id".format(i)] = res["placar"]["eventos"]["substituicoes"][i]["id-equipe"]
      
      substitution["id_player_out"] = res["placar"]["eventos"]["substituicoes"][i]["id-jogador"]
      substitution["id_player_in"] = res["placar"]["eventos"]["substituicoes"][i]["id-jogador-substituto"]
      substitution["tactical_type"] = self.getSubTactialType(res, substitution)

      s = Substitution.create(time=substitution["time"], tactical_type=self.getSubTactialType(res, substitution)).save()
      MatchSubstitution.create(match=M, substitution=s).save()
      self.__data["substitutions"].append(substitution)

  def addPenalty(self, M, res):
    self.__data["penaltys"] = []

    for i in range(len(res["placar"]["eventos"]["penaltis"])):
      penalty = {}
      penalty["time"] = str(self.getMinuto(res, i, "penaltis"))
      penalty["team_id"] = res["placar"]["eventos"]["penaltis"][i]["id-equipe"]
      p = Penalty.create(time=penalty["time"]).save()
      MatchPenalty.create(match=M, penalty=p).save()
      self.__data["penaltys"].append(penalty)

  def addYellowCards(self, M, res):
    self.__data["yellowcards"] = []

    for i in range(len(res["placar"]["eventos"]["cartoes-amarelos"])):
      yellowcard = {}
      yellowcard["time"] = str(self.getMinuto(res, i, "cartoes-amarelos"))
      yellowcard["team_id"] = res["placar"]["eventos"]["cartoes-amarelos"][i]["id-equipe"]
      yellowcard["player_id"] = res["placar"]["eventos"]["cartoes-amarelos"][i]["id-jogador"]
      y = YellowCard.create(time=yellowcard["time"], player_id=yellowcard["player_id"]).save()
      MatchYcard.create(match=M, y_card=y).save()
      self.__data["yellowcards"].append(yellowcard)

  def addRedCards(self, M, res):
    self.__data["redcards"] = []

    for i in range(len(res["placar"]["eventos"]["cartoes-vermelhos"])):
      redcard = {}
      redcard["time"] = str(self.getMinuto(res, i, "cartoes-vermelhos"))
      redcard["team_id"] = res["placar"]["eventos"]["cartoes-vermelhos"][i]["id-equipe"]
      redcard["player_id"] = res["placar"]["eventos"]["cartoes-vermelhos"][i]["id-jogador"]
      r = RedCard.create(time=redcard["time"], player_id=redcard["player_id"]).save()
      MatchRcard.create(match=M, r_card=r).save()
      self.__data["redcards"].append(redcard)

  def addGoalsAgainst(self, M, res):
    self.__data["againstgoals"] = []

    for i in range(len(res["placar"]["eventos"]["gols-contra"])):
      againstgoal = {}
      againstgoal["time"] = str(self.getMinuto(res, i, "gols-contra"))
      againstgoal["team_id"] = res["placar"]["eventos"]["gols-contra"][i]["id-equipe"]
      againstgoal["player_id"] = res["placar"]["eventos"]["gols-contra"][i]["id-jogador"]
      ga = GoalsAgainst.create(time=againstgoal["time"], player_id=againstgoal["player_id"]).save()
      MatchAgainstGoal.create(match=M, against_goal=ga).save()

  def addGoals(self, M, res):
    self.__data["goals"] = []

    for i in range(len(res["placar"]["eventos"]["gols"])):
      goal = {}
      goal["time"] = str(self.getMinuto(res, i, "gols"))
      goal["team_id"] = res["placar"]["eventos"]["gols"][i]["id-equipe"]
      goal["player_id"] = res["placar"]["eventos"]["gols"][i]["id-jogador"]
      g = Goal.create(time=goal["time"], player_id=goal["player_id"]).save()
      MatchGoal.create(match=M, goal=g).save()
