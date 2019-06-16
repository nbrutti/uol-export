import logging
from models.Models import *
from services.matchesParamsPrepare import *

logging.basicConfig(filename='logs.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class scraper(object):

  def getResponseInfo(self, m, res):
    self.home_id, self.away_id = self.getTeamsIds(res)
    self.__data = {
      "home_id": self.home_id,
      "away_id": self.away_id,
      "date": m["date"],
      "home": m["home"],
      "away": m["away"],
      "HG": m["HG"],
      "AG": m["AG"],
      "PH": m["PH"],
      "PD": m["PD"],
      "PA": m["PA"],
      "MaxH": m["MaxH"],
      "MaxD": m["MaxD"],
      "MaxA": m["MaxA"],
      "AvgH": m["AvgH"],
      "AvgD": m["AvgD"],
      "AvgA": m["AvgA"]
    }
    
    M = Partida.create(id_time_casa=self.home_id, id_time_visitante=self.away_id, time_casa=m["home"], time_visitante=m["away"], data=m["date"], time_da_casa_venceu=self.addHomeWin(res), \
                     HG=m["HG"], AG=m["AG"], PH=m["PH"], PD=m["PD"], PA=m["PA"], MAX_H=m["MaxH"], MAX_D=m["MaxD"], MAX_A=m["MaxA"], AVG_H=m["AvgH"], AVG_D=m["AvgD"], AVG_A=m["AvgA"])
    M.save()
    self.addGoals(M, res)
    self.addPenalty(M, res)
    self.addSubstitutions(M, res)
    #self.addSubstitutionsEffect(M, res, self.__data["home"])
    #self.addSubstitutionsEffect(M, res, self.__data["away"])
    self.addYellowCards(M, res)
    self.addRedCards(M, res)
    self.getOrCreateTeams()
    self.addGoalsAgainst(M, res)

    print (self.__data)
    return self.__data

  def getMinutes(self, goal):
    t = (45 if (goal["id-periodo"] == '2') else 0) + int(goal['minuto'])
    return t

  def getScoreWhenReplaced(self, M, res, substitution):
    home_goals = 0
    away_goals = 0
    home_id, away_id = self.getTeamsIds(res)
    time = 45 if substitution["time"] == 'INTERVALO' else int(substitution["time"])
    # Percorre todos os gols e monta o placar
    for i in range(len(res["placar"]["eventos"]["gols"])):
      if (self.getMinutes(res["placar"]["eventos"]["gols"][i]) <= time):
        if (res["placar"]["eventos"]["gols"][i]["id-equipe"] == home_id):
          home_goals += 1
        elif (res["placar"]["eventos"]["gols"][i]["id-equipe"] == away_id):
          away_goals += 1
    # Percorre todos os gols contra e monta o placar
    try:
      for i in range(len(res["placar"]["eventos"]["gols-contra"])):
        if (self.getMinutes(res["placar"]["eventos"]["gols-contra"][i]) <= time):
          if (res["placar"]["eventos"]["gols-contra"][i]["id-equipe"] == home_id):
            away_goals += 1
          elif (res["placar"]["eventos"]["gols-contra"][i]["id-equipe"] == away_id):
            home_goals += 1
    except:
      pass
    return home_goals, away_goals

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

  def getIndexOfSub(self, pos):
    if (pos == 'Goleiro'):
      return 0
    elif (pos == 'Zagueiro' or pos == 'Lateral-direito' or pos == 'Lateral-esquerdo'):
      return 1
    elif (pos == 'Volante'):
      return 2
    elif (pos == 'Meia'):
      return 3
    elif (pos == 'Meia-atacante'):
      return 4
    elif (pos == 'Atacante'):
      return 5
    else:
      return -1

  def getSubTactialType(self, res, substitution):
    player_in_pos = self.getPlayerPosById(res, substitution["id_player_in"])
    player_out_pos = self.getPlayerPosById(res, substitution["id_player_out"])

    index_in = self.getIndexOfSub(player_in_pos)
    index_out = self.getIndexOfSub(player_out_pos)

    if (index_in == -1 or index_out == -1):
      logging.info("Não foi possível extrair o tipo da substituição do jogo {} x {}".format(self.__data["home"], self.__data["away"]))
      return None

    if (index_in > index_out):
      return "OFF"
    elif (index_in < index_out):
      return "DEF"
    else:
      return "NA"

  def findGoalsInterval(self, x, y, team_goal):
    goalsofteam = []
    for g in self.__data["goals"]:
      if (int(g["time"]) >= x and int(g["time"]) <= y):
        if (g["team"] == team_goal):
          goalsofteam.append(g)
    return goalsofteam

  def addSubstitutionsEffect(self, this_substitution, team):
    '''
      Verifica se a substituição foi efetiva, com base nas seguintes situações:
      Se a equipe mandante estiver ganhando e após a substituição ela venha a
      manter o placar esta substituição é positiva(1) neste cenário, caso contrá
      rio é (0)'
      
      Se a equipe mandante estiver perdendo e após a substituição houve um
      incremento favorável para equipe no placar, esta substituição é consi
      derada positiva(1), caso contrário (0).

    '''
    #this_substitutions = [s if team == s["team"] else None for s in self.__data["substitutions"]]
    time = 45 if this_substitution["time"] == 'INTERVALO' else this_substitution["time"]
    x = int(time)

    '''try:
      count = 1
      while (True):
        if (this_substitutions[i + count] is not None):
          y = int(this_substitutions[i + count]["time"])
          break
        else:
          count += 1
    except:
      y = 90'''

    y = 90

    favorable_goals = self.findGoalsInterval(x, y, team)
    opponents_goals = self.findGoalsInterval(x, y, self.__data["away"] if team == self.__data["home"] else self.__data["home"])
    effectiveness   = 0

    if (favorable_goals):
      effectiveness = 1
    elif (not opponents_goals and team != self.__data["home"] and this_substitution['tactical_type'] in ['NA', 'DEF']):
      effectiveness = 1
    elif (not opponents_goals and team == self.__data["home"] and this_substitution['tactical_type'] in ['DEF']):
      effectiveness = 1
    else:
      effectiveness = 0
    return effectiveness

  def addSubstitutions(self, M, res):
    number_sub_home = 0
    number_sub_away = 0
    self.__data["substitutions"] = []

    for i in range(len(res["placar"]["eventos"]["substituicoes"]) - 1, -1, -1):
      substitution = {}
      if (str(res["placar"]["eventos"]["substituicoes"][i]["periodo"]) == 'intervalo-de-jogo'):
        substitution["time"] = 'INTERVALO'
      else:
        substitution["time"] = str(self.getMinuto(res, i, "substituicoes"))
      substitution["team"] = self.__data["home"] if self.getTeamsIds(res)[0] == res["placar"]["eventos"]["substituicoes"][i]["id-equipe"] else self.__data["away"]

      if (substitution["team"] == self.__data["home"]):
        number_sub_home += 1
      else:
        number_sub_away += 1

      substitution["id_player_out"] = res["placar"]["eventos"]["substituicoes"][i]["id-jogador"]
      substitution["id_player_in"] = res["placar"]["eventos"]["substituicoes"][i]["id-jogador-substituto"]
      substitution["tactical_type"] = self.getSubTactialType(res, substitution)
      substitution["score_home"], substitution["score_away"] = self.getScoreWhenReplaced(M, res, substitution)
      substitution["number_of_sub"] = number_sub_home if substitution["team"] == self.__data["home"] else number_sub_away
      substitution["effectiveness"] = self.addSubstitutionsEffect(substitution, self.__data["away"])

      s = Substituicao.create(tempo=substitution["time"], tipo_tatico=substitution["tactical_type"], efetividade=substitution["effectiveness"]).save()
      PartidasSubstituicoes.create(partida=M, substituicao=s).save()
      self.__data["substitutions"].append(substitution)

  def addPenalty(self, M, res):
    self.__data["penaltys"] = []

    for i in range(len(res["placar"]["eventos"]["penaltis"])):
      penalty = {}
      penalty["time"] = str(self.getMinuto(res, i, "penaltis"))
      penalty["team"] = self.__data["home"] if self.getTeamsIds(res)[0] == res["placar"]["eventos"]["penaltis"][i]["id-equipe"] else self.__data["away"]
      p = Penalti.create(tempo=penalty["time"]).save()
      PartidasPenaltis.create(partida=M, penalti=p).save()
      self.__data["penaltys"].append(penalty)

  def addYellowCards(self, M, res):
    self.__data["yellowcards"] = []

    for i in range(len(res["placar"]["eventos"]["cartoes-amarelos"])):
      yellowcard = {}
      yellowcard["time"] = str(self.getMinuto(res, i, "cartoes-amarelos"))
      yellowcard["team"] = self.__data["home"] if self.getTeamsIds(res)[0] == res["placar"]["eventos"]["cartoes-amarelos"][i]["id-equipe"] else self.__data["away"]
      yellowcard["player_id"] = res["placar"]["eventos"]["cartoes-amarelos"][i]["id-jogador"]
      y = CartaoAmarelo.create(tempo=yellowcard["time"], id_jogador=yellowcard["player_id"]).save()
      PartidasCartoesAmarelos.create(partida=M, cartoes_amarelos=y).save()
      self.__data["yellowcards"].append(yellowcard)

  def addRedCards(self, M, res):
    self.__data["redcards"] = []

    for i in range(len(res["placar"]["eventos"]["cartoes-vermelhos"])):
      redcard = {}
      redcard["time"] = str(self.getMinuto(res, i, "cartoes-vermelhos"))
      redcard["team"] = self.__data["home"] if self.getTeamsIds(res)[0] == res["placar"]["eventos"]["cartoes-vermelhos"][i]["id-equipe"] else self.__data["away"]
      redcard["player_id"] = res["placar"]["eventos"]["cartoes-vermelhos"][i]["id-jogador"]
      r = CartaoVermelho.create(tempo=redcard["time"], id_jogador=redcard["player_id"]).save()
      PartidasCartoesVermelhos.create(partida=M, cartoes_vermelhos=r).save()
      self.__data["redcards"].append(redcard)

  def addGoalsAgainst(self, M, res):
    self.__data["againstgoals"] = []

    for i in range(len(res["placar"]["eventos"]["gols-contra"])):
      againstgoal = {}
      againstgoal["time"] = str(self.getMinuto(res, i, "gols-contra"))
      againstgoal["team"] = self.__data["home"] if self.getTeamsIds(res)[0] == res["placar"]["eventos"]["gols-contra"][i]["id-equipe"] else self.__data["away"]
      againstgoal["player_id"] = res["placar"]["eventos"]["gols-contra"][i]["id-jogador"]
      ga = GolContra.create(tempo=againstgoal["time"], id_jogador=againstgoal["player_id"]).save()
      PartidasGolsContra.create(partida=M, gols_contra=ga).save()
      self.__data["againstgoals"].append(againstgoal)

  def addGoals(self, M, res):
    self.__data["goals"] = []

    for i in range(len(res["placar"]["eventos"]["gols"])):
      goal = {}
      goal["time"] = str(self.getMinuto(res, i, "gols"))
      goal["team"] = self.__data["home"] if self.getTeamsIds(res)[0] == res["placar"]["eventos"]["gols"][i]["id-equipe"] else self.__data["away"]
      goal["player_id"] = res["placar"]["eventos"]["gols"][i]["id-jogador"]
      g = Gol.create(tempo=goal["time"], id_jogador=goal["player_id"]).save()
      PartidasGols.create(partida=M, gols=g).save()
      self.__data["goals"].append(goal)

  def addHomeWin(self, res):
    winner = 0
    if (res["placar"]["partida"]["fim"]["saldo-gols"][0] > res["placar"]["partida"]["fim"]["saldo-gols"][1]):
      winner = 1
    elif (res["placar"]["partida"]["fim"]["saldo-gols"][0] < res["placar"]["partida"]["fim"]["saldo-gols"][1]):
      winner = -1
    else:
      winner = 0
    self.__data["home_win"] = winner
    return winner

  def getOrCreateTeams(self):
    t1 = Time.get_or_create(api_id=0 if self.__data["home_id"] == '' else self.__data["home_id"], nome=self.__data["home"])
    t2 = Time.get_or_create(api_id=0 if self.__data["away_id"] == '' else self.__data["home_id"], nome=self.__data["away"])
    #Time.update([t1, t2], fields=[Time.goals_scored, Time.goals_conceded, Time.win_matches, Time.lost_matches])
